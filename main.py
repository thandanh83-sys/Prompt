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

# Lấy danh sách IP được phép (cách nhau bằng dấu phẩy)
ADMIN_ALLOWED_IPS = os.environ.get("ADMIN_ALLOWED_IPS", "").split(",")
ADMIN_ALLOWED_IPS = [ip.strip() for ip in ADMIN_ALLOWED_IPS if ip.strip()]

if not ADMIN_PASSWORD or not ADMIN_SECRET_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("LỖI BẢO MẬT: Thiếu biến môi trường bắt buộc trên Render.")

api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

DEFAULT_ORIGINS = ["https://thandanh83-sys.github.io"]
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in env_origins.split(",") if o.strip()] or DEFAULT_ORIGINS

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

# Hàm kiểm tra IP Admin
def verify_admin_ip(request: Request):
    client_ip = get_client_ip(request)
    if ADMIN_ALLOWED_IPS:
        if client_ip not in ADMIN_ALLOWED_IPS:
            logger.warning(f"TỪ CHỐI TRUY CẬP ADMIN: IP lạ {client_ip} cố gắng truy cập.")
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối. IP của bạn không nằm trong danh sách cho phép.")
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
    allow_methods=["GET", "POST", "OPTIONS"],
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
    if not isinstance(text, str) or not text.strip():
        return ""
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
        {"role": "user", "content": f"<prompt_can_cham>\n{user_prompt}\n</prompt_can_cham>"},
    ]

    try:
        logger.info("Đang gọi Groq...")
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq thất bại: {e}. Chuyển sang Gemini...")

    if gemini_model:
        try:
            temp_model = genai.GenerativeModel(
                'gemini-1.5-flash', 
                system_instruction=system_prompt
            )
            response = temp_model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                )
            )
            if not response.text:
                 raise ValueError("Gemini trả về chuỗi rỗng.")
            logger.info("Gemini trả về thành công (Fallback).")
            return response.text
        except Exception as e:
            logger.error(f"Gemini cũng thất bại: {e}")
            raise HTTPException(status_code=503, detail="Hệ thống AI đang quá tải. Vui lòng thử lại sau ít phút.")
    else:
        raise HTTPException(status_code=503, detail="Groq đang gặp sự cố và chưa cấu hình Gemini dự phòng.")

def bg_save_history(payload: dict):
    if not supabase: return
    try:
        supabase.table("history").insert(payload).execute()
        logger.info("Đã lưu lịch sử vào Supabase.")
    except Exception as e:
        logger.error(f"LỖI BACKGROUND: Không thể lưu lịch sử vào Supabase: {e}")

def bg_cleanup_history():
    if not supabase: return
    try:
        ten_days_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10)).isoformat()
        supabase.table("history").delete().lt("created_at", ten_days_ago).execute()
        logger.info("Đã dọn dẹp lịch sử cũ hơn 10 ngày.")
    except Exception as e:
        logger.warning(f"LỖI BACKGROUND: Không thể dọn dẹp lịch sử: {e}")

@app.get("/")
def read_root(): 
    return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check(): 
    return {"status": "ok"}

@app.get("/check_admin_ip")
def check_admin_ip(client_ip: str = Depends(verify_admin_ip)):
    return {"is_admin": True}

@app.get("/top_prompts")
def get_top_prompts():
    if not supabase:
        return {"prompts": []}
    try:
        res = supabase.table("history")\
            .select("prompt, type, total_score, created_at")\
            .gte("total_score", 8.0)\
            .order("total_score", desc=True)\
            .limit(10)\
            .execute()
        return {"prompts": res.data}
    except Exception as e:
        logger.error(f"Lỗi lấy top prompts: {e}")
        return {"prompts": []}

@app.post("/login")
@limiter.limit("5/minute")
def admin_login(request: Request, req: LoginRequest, client_ip: str = Depends(verify_admin_ip)):
    if secrets.compare_digest(req.password, ADMIN_PASSWORD):
        return {"token": ADMIN_SECRET_TOKEN}
    raise HTTPException(status_code=401, detail="Sai mật khẩu")

@app.get("/history")
def get_history(token: str = Depends(api_key_header), client_ip: str = Depends(verify_admin_ip)):
    if not token or not secrets.compare_digest(token, ADMIN_SECRET_TOKEN):
        raise HTTPException(status_code=401, detail="Không có quyền truy cập")
    if not supabase:
        return {"history": [], "message": "Supabase chưa được cấu hình"}
    try:
        res = supabase.table("history").select("prompt, type, total_score, created_at, errors").order("created_at", desc=True).limit(100).execute()
        return {"history": res.data}
    except Exception as e:
        logger.error(f"Lỗi lấy lịch sử: {e}")
        raise HTTPException(status_code=500, detail="Lỗi máy chủ")

@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest, background_tasks: BackgroundTasks):
    prompt_text = req.prompt.strip()

    if not prompt_text:
        return JSONResponse(status_code=400, content={"error": "Prompt trống."})
    if len(prompt_text) > MAX_PROMPT_LENGTH:
        return JSONResponse(status_code=400, content={"error": f"Prompt vượt quá {MAX_PROMPT_LENGTH} ký tự."})

    background_tasks.add_task(bg_cleanup_history)

    try:
        classification = rules_v38.classify_prompt(prompt_text)
        
        if classification["main_task"] == rules_v38.TYPE_EMPTY:
             return JSONResponse(status_code=400, content={"error": "Nội dung prompt không hợp lệ."})

        criteria_pack = rules_v38.get_criteria_by_type(classification)
        main_task = classification["main_task"]
        techniques = classification["techniques"]
        main_criteria = criteria_pack["main"]
        tech_criteria = criteria_pack["tech"]
        
        all_criteria = {**main_criteria, **tech_criteria}
        
        criteria_desc = ""
        for k, v in all_criteria.items():
            criteria_desc += f"- ID {k} ({v['name']}): {v['rubric']}\n"

        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in all_criteria.keys()])

        system_prompt = f"""
Bạn là Chuyên gia Prompt Engineering. Đánh giá và viết lại câu lệnh của người dùng theo form 11 mục.

BƯỚC 1: XÁC ĐỊNH LĨNH VỰC & CHUYÊN GIA.
BƯỚC 2: VIẾT LẠI PROMPT THEO ĐÚNG CẤU TRÚC JSON SAU (Sử dụng \\n để xuống dòng trong nội dung):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn hoặc 'Toàn bộ']"}} ],
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

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ. KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO KHÁC.
"""
        
        ai_data = None
        max_attempts = 2 

        for attempt in range(max_attempts):
            try:
                raw_text = call_llm(system_prompt, prompt_text)
                if not raw_text:
                    raise ReportValidationError("AI trả về rỗng.")
                
                json_str = extract_json(raw_text)
                ai_data = json.loads(json_str)
                validate_full_report(ai_data, main_criteria, tech_criteria, prompt_text)
                break 
                
            except json.JSONDecodeError as e:
                logger.warning(f"Lần {attempt+1}: Lỗi parse JSON ({e}). Đang thử lại...")
                ai_data = None
            except ReportValidationError as e:
                logger.warning(f"Lần {attempt+1}: Dữ liệu sai cấu trúc ({e}). Đang thử lại...")
                ai_data = None

        if ai_data is None:
            logger.error("Thất bại sau 2 lần gọi. AI liên tục trả dữ liệu không hợp lệ.")
            return JSONResponse(status_code=502, content={"error": "AI trả về dữ liệu không hợp lệ. Vui lòng thử lại."})

        final_score = calculate_final_score(ai_data["scores"], main_criteria, tech_criteria)

        display_details = {all_criteria[k]["name"]: v for k, v in ai_data["scores"].items() if k in all_criteria}
        
        result = {
            "prompt": prompt_text, 
            "type": main_task, 
            "techniques": techniques, 
            "total": final_score,
            "details": display_details,
            "errors": ai_data.get("errors", []), 
            "rewrite": ai_data["rewrite"]
        }

        db_payload = {
            "prompt": prompt_text, 
            "type": main_task, 
            "total_score": final_score,
            "details": result["details"], 
            "errors": result["errors"], 
            "rewrite": result["rewrite"],
        }
        background_tasks.add_task(bg_save_history, db_payload)

        return result

    except rules_v38.ConfigurationError as ce:
        logger.error(f"LỖI CẤU HÌNH HỆ THỐNG: {ce}")
        return JSONResponse(status_code=500, content={"error": "Lỗi cấu hình hệ thống chấm điểm."})
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Lỗi nghiêm trọng trong /evaluate")
        return JSONResponse(status_code=500, content={"error": "Lỗi máy chủ nội bộ."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))