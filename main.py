import os
import json
import re
import time
import logging
import secrets
import datetime
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

import rules_v38
from validator import validate_full_report, calculate_final_score, ReportValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prompt-evaluator")

MAX_PROMPT_LENGTH = 5000
RATE_LIMIT = "20/minute"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_SECRET_TOKEN = os.environ.get("ADMIN_SECRET_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ADMIN_ALLOWED_IPS = os.environ.get("ADMIN_ALLOWED_IPS", "").split(",")
ADMIN_ALLOWED_IPS = [ip.strip() for ip in ADMIN_ALLOWED_IPS if ip.strip()]

if not ADMIN_PASSWORD or not ADMIN_SECRET_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("LỖI BẢO MẬT: Thiếu biến môi trường bắt buộc trên Render.")

api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

DEFAULT_ORIGINS = ["https://thandanh83-sys.github.io"]
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
configured_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
ALLOWED_ORIGINS = list(dict.fromkeys([*DEFAULT_ORIGINS, *configured_origins]))

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def verify_admin_ip(request: Request):
    client_ip = get_client_ip(request)
    if ADMIN_ALLOWED_IPS:
        if client_ip not in ADMIN_ALLOWED_IPS:
            logger.warning(f"TỪ CHỐI TRUY CẬP ADMIN: IP lạ {client_ip}.")
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối.")
    return client_ip

limiter = Limiter(key_func=get_client_ip)
app = FastAPI()
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "Bạn đã đạt giới hạn sử dụng, vui lòng thử lại sau 1 phút."})

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token"],
)

class PromptRequest(BaseModel):
    prompt: str

class LoginRequest(BaseModel):
    password: str

client = Groq(api_key=GROQ_API_KEY)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

def extract_json(text: str) -> str:
    if not isinstance(text, str) or not text.strip(): return ""
    text = text.strip()
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
    for i, char in enumerate(text):
        if char == '{':
            try:
                obj, end_idx = json.JSONDecoder().raw_decode(text[i:])
                return text[i:i+end_idx]
            except json.JSONDecodeError:
                continue
    return ""

def call_llm(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Dữ liệu prompt cần đánh giá:\n" + json.dumps({"prompt_can_cham": user_prompt}, ensure_ascii=False)},
    ]
    
    try:
        logger.info("Đang gọi Groq (Primary)...")
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=15.0
        )
        logger.info("Groq trả về thành công.")
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq thất bại: {e}. Chuyển sang Gemini...")

    if gemini_model:
        try:
            logger.info("Đang gọi Gemini (Fallback)...")
            temp_model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
            response = temp_model.generate_content(
                json.dumps({"prompt_can_cham": user_prompt}, ensure_ascii=False),
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json", temperature=0.1),
                request_options={"timeout": 20}
            )
            if not response.text: raise ValueError("Gemini trả về chuỗi rỗng.")
            logger.info("Gemini trả về thành công (Fallback).")
            return response.text
        except Exception as e:
            logger.error(f"Gemini cũng thất bại: {e}")
            raise HTTPException(status_code=503, detail="Hệ thống AI đang quá tải, vui lòng thử lại.")
    else:
        raise HTTPException(status_code=503, detail="Groq gặp sự cố và chưa cấu hình Gemini.")

def bg_save_history(payload: dict):
    if not supabase: return
    try:
        supabase.table("history").insert(payload).execute()
    except Exception as e:
        logger.error(f"LỖI BACKGROUND: Không thể lưu lịch sử: {e}")

@app.get("/")
def read_root(): return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check(): return {"status": "ok"}

@app.get("/check_admin_ip")
def check_admin_ip(client_ip: str = Depends(verify_admin_ip)):
    return {"is_admin": True}

@app.post("/login")
@limiter.limit("5/minute")
def admin_login(request: Request, req: LoginRequest, client_ip: str = Depends(verify_admin_ip)):
    if secrets.compare_digest(req.password, ADMIN_PASSWORD):
        if supabase:
            try:
                supabase.table("admin_login_logs").insert({"ip_address": client_ip, "user_agent": request.headers.get("user-agent", "Unknown")}).execute()
            except Exception as e:
                logger.error(f"Lỗi lưu log IP Admin: {e}")
        return {"token": ADMIN_SECRET_TOKEN}
    raise HTTPException(status_code=401, detail="Sai mật khẩu")

@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest, background_tasks: BackgroundTasks):
    prompt_text = req.prompt.strip()
    if not prompt_text: return JSONResponse(status_code=400, content={"error": "Prompt trống."})
    if len(prompt_text) > MAX_PROMPT_LENGTH: return JSONResponse(status_code=400, content={"error": f"Prompt vượt quá {MAX_PROMPT_LENGTH} ký tự."})

    try:
        classification = rules_v38.classify_prompt(prompt_text)
        criteria_pack = rules_v38.get_criteria_by_type(classification)
        main_task = classification["main_task"]
        techniques = classification["techniques"]
        main_criteria = criteria_pack["main"]
        tech_criteria = criteria_pack["tech"]
        
        all_criteria = {**main_criteria, **tech_criteria}
        criteria_desc = "".join([f"- ID {k} ({v['name']}): {v['rubric']}\n" for k, v in all_criteria.items()])
        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 5' for k in all_criteria.keys()])
        
        SECTION_NAMES = ["1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"]

        system_prompt = f"""
Bạn là một Chuyên gia Prompt Engineering xuất sắc. Nhiệm vụ của bạn là đánh giá câu lệnh (prompt) của người dùng và viết lại nó thành một Prompt chuẩn 11 mục.

QUY TẮC SỐNG CÒN:
1. Người dùng có thể nhập câu ngắn hoặc chưa đầy đủ (ví dụ: "tả mẹ", "so sánh 2 bài văn"). Bạn TUYỆT ĐỐI KHÔNG ĐƯỢC HỎI LẠI. KHÔNG ĐƯỢC trả về văn bản thường.
2. BẠN PHẢI TỰ ĐỘNG ĐÓNG VAI CHUYÊN GIA, TỰ SUY LUẬN VÀ MỞ RỘNG NGỮ CẢNH để điền đầy đủ 11 mục. Hãy giả định rằng người dùng muốn bạn tạo ra một Prompt mẫu hoàn chỉnh.
3. CHẤM ĐIỂM NGHIÊM NGẶT: Đối chiếu với THANG ĐIỂM. Nếu câu lệnh quá ngắn, sơ sài: Chấm điểm thấp (1-3 điểm). Nếu câu lệnh đã chi tiết: Chấm điểm cao (7-10 điểm).
4. BẢN SỬA (rewrite): Phải là một Prompt hoàn chỉnh 11 mục do bạn tự tay viết ra.
5. ĐỊNH DẠNG ĐẶC BIỆT: Trong phần "rewrite", mỗi mục bạn PHẢI sử dụng ký tự `\\n` để xuống dòng cho các ý nhỏ (gạch đầu dòng). Không được viết dính chùm.
6. BẮT BUỘC TRẢ VỀ JSON CÓ 3 KEY: "scores", "errors", "rewrite". NẾU THIẾU BẤT KỲ KEY NÀO, BẠN SẼ BỊ PHẠT.

CẤU TRÚC 11 MỤC BẮT BUỘC (Hãy điền chi tiết vào phần rewrite):
"1. VAI TRÒ": [Vai trò chuyên môn, số năm kinh nghiệm, lĩnh vực, kỹ năng cốt lõi]
"2. BỐI CẢNH": [Người dùng là ai, Mục đích, Không gian, Thời gian, Cảm xúc, Văn hóa, Chuyên môn, Ràng buộc, Kỳ vọng, Đối thủ, Lịch sử, Tương lai] (Dùng \\n để xuống dòng từng ý)
"3. INPUT": [Người dùng cung cấp gì: ảnh, file, văn bản, dữ liệu, câu hỏi]
"4. MỤC TIÊU": [Kết quả cuối cùng cần đạt, đo lường được]
"5. YÊU CẦU": [Yêu cầu cụ thể, hành động rõ ràng, không mơ hồ]
"6. RÀNG BUỘC": [PHẢI làm gì, KHÔNG ĐƯỢC làm gì, GIỚI HẠN về độ dài/định dạng] (Dùng \\n để xuống dòng)
"7. TASK": [Các bước thực hiện 1, 2, 3...] (Dùng \\n để xuống dòng)
"8. ĐỊNH DẠNG ĐẦU RA": [Văn bản, bảng, code, ảnh, JSON, danh sách]
"9. NEVER DO": [Danh sách lỗi cần tránh]
"10. THỨ TỰ ƯU TIÊN": [Ưu tiên 1, 2, 3...]
"11. XỬ LÝ NỘI BỘ": [Tự kiểm tra logic, độ chính xác trước khi xuất kết quả]

BƯỚC 2: TRẢ VỀ JSON THEO CẤU TRÚC SAU:
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn nguyên văn từ prompt gốc]"}} ],
  "rewrite": {{ 
    "1. VAI TRÒ": "...", "2. BỐI CẢNH": "...", "3. INPUT": "...", "4. MỤC TIÊU": "...", "5. YÊU CẦU": "...",
    "6. RÀNG BUỘC": "...", "7. TASK": "...", "8. ĐỊNH DẠNG ĐẦU RA": "...", "9. NEVER DO": "...", 
    "10. THỨ TỰ ƯU TIÊN": "...", "11. XỬ LÝ NỘI BỘ": "..."
  }}
}}

THANG ĐIỂM (RUBRIC):
{criteria_desc}

MÃ LỖI:
{error_codes_desc}
"""
        
        ai_data = {}
        success = False
        max_retries = 2

        # VÒNG LẶP THỬ LẠI: Nếu AI trả về sai, tự động gọi lại
        for attempt in range(max_retries):
            try:
                raw_text = call_llm(system_prompt, prompt_text)
                json_str = extract_json(raw_text)
                ai_data = json.loads(json_str)
                
                # Validate chặt chẽ, nếu sai sẽ văng lỗi và chạy lại vòng lặp
                validate_full_report(ai_data, main_criteria, tech_criteria, prompt_text)
                success = True
                break # Nếu thành công thì thoát vòng lặp
            except Exception as e:
                logger.warning(f"Lần thử {attempt+1} thất bại: {e}")
        
        # NẾU THỬ 2 LẦN VẪN LỖI -> DÙNG FALLBACK
        if not success:
            logger.error("Đã thử 2 lần nhưng AI vẫn trả về sai. Dùng Fallback.")
            if not isinstance(ai_data, dict): ai_data = {}
            if "scores" not in ai_data or not isinstance(ai_data["scores"], dict): ai_data["scores"] = {}
            if "errors" not in ai_data or not isinstance(ai_data["errors"], list): ai_data["errors"] = []
            if "rewrite" not in ai_data or not isinstance(ai_data["rewrite"], dict): ai_data["rewrite"] = {}
            
            for k in all_criteria.keys():
                if k not in ai_data["scores"]: ai_data["scores"][k] = 1
            
            for sec in SECTION_NAMES:
                if sec not in ai_data["rewrite"] or not ai_data["rewrite"][sec]: 
                    if sec == "1. VAI TRÒ": ai_data["rewrite"][sec] = "Bạn là một chuyên gia trong lĩnh vực này."
                    elif sec == "7. TASK": ai_data["rewrite"][sec] = f"Hãy thực hiện yêu cầu: {prompt_text}"
                    else: ai_data["rewrite"][sec] = f"Hệ thống AI đang bổ sung ngữ cảnh cho mục {sec}."

        final_score = calculate_final_score(ai_data["scores"], main_criteria, tech_criteria)
        display_details = {all_criteria[k]["name"]: v for k, v in ai_data["scores"].items() if k in all_criteria}
        
        result = {
            "prompt": prompt_text, "type": main_task, "techniques": techniques, 
            "total": final_score, "details": display_details,
            "errors": ai_data.get("errors", []), "rewrite": ai_data["rewrite"]
        }

        db_payload = {
            "prompt": prompt_text, "type": main_task, "total_score": final_score,
            "details": result["details"], "errors": result["errors"], "rewrite": result["rewrite"],
        }
        background_tasks.add_task(bg_save_history, db_payload)
        return result

    except Exception as e:
        logger.exception("Lỗi nghiêm trọng trong /evaluate")
        return JSONResponse(status_code=500, content={"error": "Lỗi máy chủ nội bộ."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))