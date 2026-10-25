import os
import json
import re
import logging
import random  
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from groq import Groq, RateLimitError
from supabase import create_client, Client
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

import rules_v38
import error_rules
from validator import validate_full_report, calculate_final_score, ReportValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prompt-evaluator")

MAX_PROMPT_LENGTH = 5000
RATE_LIMIT = "20/minute"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_SECRET_TOKEN = os.environ.get("ADMIN_SECRET_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

ADMIN_ALLOWED_IPS = os.environ.get("ADMIN_ALLOWED_IPS", "").split(",")
ADMIN_ALLOWED_IPS = [ip.strip() for ip in ADMIN_ALLOWED_IPS if ip.strip()]

if not ADMIN_PASSWORD or not ADMIN_SECRET_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("LỖI BẢO MẬT: Thiếu biến môi trường.")

api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)
DEFAULT_ORIGINS = ["https://thandanh83-sys.github.io"]
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
configured_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
ALLOWED_ORIGINS = list(dict.fromkeys([*DEFAULT_ORIGINS, *configured_origins]))

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded: return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def verify_admin_ip(request: Request):
    client_ip = get_client_ip(request)
    if ADMIN_ALLOWED_IPS and client_ip not in ADMIN_ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Truy cập bị từ chối.")
    return client_ip

def verify_admin_token(token: str = Depends(api_key_header)):
    if not token or token != ADMIN_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")
    return token

limiter = Limiter(key_func=get_client_ip)
app = FastAPI()
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "Bạn đã đạt giới hạn sử dụng, vui lòng thử lại sau 1 phút."})

app.add_middleware(
    CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "X-Admin-Token"],
)

class PromptRequest(BaseModel): prompt: str
class AdminLoginRequest(BaseModel): password: str

client = Groq(api_key=GROQ_API_KEY)
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

def extract_json(text: str) -> str:
    if not isinstance(text, str) or not text.strip(): return ""
    text = text.strip()
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError: pass
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError: pass
    for i, char in enumerate(text):
        if char == '{':
            try:
                obj, end_idx = json.JSONDecoder().raw_decode(text[i:])
                return text[i:i+end_idx]
            except json.JSONDecodeError: continue
    return ""

def call_llm(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Dữ liệu prompt:\n" + json.dumps({"prompt_can_cham": user_prompt}, ensure_ascii=False)},
    ]
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b", messages=messages, response_format={"type": "json_object"},
            temperature=0.1, timeout=30.0
        )
        return resp.choices[0].message.content
    except RateLimitError as e:
        logger.warning(f"Groq Rate Limit: {e}")
        raise HTTPException(status_code=429, detail="Đã chạm giới hạn Token. Vui lòng đợi 1 phút!")
    except Exception as e:
        logger.error(f"Groq thất bại: {e}")
        raise HTTPException(status_code=503, detail="Hệ thống AI quá tải. Vui lòng thử lại sau.")

def bg_save_history(payload: dict):
    if not supabase: return
    try: supabase.table("history").insert(payload).execute()
    except Exception as e: logger.error(f"LỖI BACKGROUND: {e}")

# ... (Các API /, /health, /login, /history, /delete... giữ nguyên)
@app.get("/check_admin_ip")
def check_admin_ip(client_ip: str = Depends(verify_admin_ip)): return {"is_admin": True}
@app.post("/login")
def login(req: AdminLoginRequest, request: Request):
    if req.password != ADMIN_PASSWORD: raise HTTPException(status_code=401, detail="Sai mật khẩu")
    return {"token": ADMIN_SECRET_TOKEN}
@app.get("/top_prompts")
def get_top_prompts():
    if not supabase: return JSONResponse(status_code=500, content={"error": "Supabase chưa cấu hình."})
    try:
        response = supabase.table("history").select("prompt", "type", "total_score", "created_at").gte("total_score", 7.0).limit(50).execute()
        prompts = response.data
        if len(prompts) > 5: prompts = random.sample(prompts, 5)
        return {"prompts": prompts}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Không thể lấy dữ liệu."})

@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest, background_tasks: BackgroundTasks):
    prompt_text = req.prompt.strip()
    if not prompt_text: return JSONResponse(status_code=400, content={"error": "Prompt trống."})
    if len(prompt_text) > MAX_PROMPT_LENGTH: return JSONResponse(status_code=400, content={"error": "Prompt quá dài."})

    try:
        classification = rules_v38.classify_prompt(prompt_text)
        criteria_pack = rules_v38.get_criteria_by_type(classification)
        main_task = classification["main_task"]
        techniques = classification["techniques"]
        main_criteria = criteria_pack["main"]
        tech_criteria = criteria_pack["tech"]
        
        all_criteria = {**main_criteria, **tech_criteria}
        criteria_desc = "".join([f"- {k}: {v['name']}\n" for k, v in all_criteria.items()])
        scores_example = ", ".join([f'"{k}": 5' for k in all_criteria.keys()])
        
        error_codes_desc = ""
        for code, rule in error_rules.ERROR_RULES.items():
            error_codes_desc += f"- {code}: {rule['name']}\n"
        
        system_prompt = f"""
Bạn là chuyên gia chấm điểm và tối ưu hóa Prompt. Người dùng có thể nhập Prompt bằng BẤT KỲ NGÔN NGỮ NÀO.

HÃY THỰC HIỆN THEO QUY TRÌNH 4 BƯỚC SAU:

[BƯỚC 1: CHẤM ĐIỂM TIÊU CHÍ LÕI]
{criteria_desc}

[BƯỚC 2: TỰ SINH TIÊU CHÍ CHUYÊN NGÀNH (DYNAMIC)]
Hãy phân tích xem prompt này thuộc lĩnh vực gì (VD: Mỹ phẩm, Code, Marketing...).
Tự nghĩ ra từ 3 đến 5 tiêu chí chuyên sâu quan trọng nhất cho lĩnh vực đó (VD với Mỹ phẩm: "Cảnh báo kích ứng", "Phân tích thành phần"). 
Đặt mã lần lượt là "DYN01", "DYN02", "DYN03", "DYN04", "DYN05" (chỉ tạo tối đa 5) và chấm điểm chúng (0-10).

[BƯỚC 3: TÌM LỖI]
{error_codes_desc}

[BƯỚC 4: TÁI CẤU TRÚC VÀ CẢI TIẾN]
Chuyển đổi prompt thành 11 mục tiếng Việt. 
Quy tắc viết lại: 10 điểm copy nguyên bản, dưới 10 điểm mới cải tiến.

QUY TẮC BẰNG CHỨNG: TUYỆT ĐỐI KHÔNG dùng ngoặc kép bao quanh evidence. Chỉ copy nguyên văn.
Lỗi thiếu thông tin (B01, C02, C04): ghi vào "evidence" là "Không có thông tin này trong prompt".
Thêm trường "hint" cho mỗi lỗi để gợi ý cách sửa cụ thể.

Trả về JSON chính xác cấu trúc sau (KHÔNG THÊM KEY KHÁC):
{{
  "scores": {{ {scores_example}, "DYN01": 5, "DYN02": 5, "DYN03": 5 }},
  "dynamic_criteria_names": {{
      "DYN01": "Tên tiêu chí chuyên ngành 1", "DYN02": "Tên tiêu chí 2", "DYN03": "Tên tiêu chí 3"
  }},
  "errors": [ {{"code": "MÃ_LỖI", "evidence": "Trích dẫn", "hint": "Cách sửa"}} ],
  "rewrite": {{ 
    "1. VAI TRÒ": "...", "2. BỐI CẢNH": "...", "3. INPUT": "...", "4. MỤC TIÊU": "...", "5. YÊU CẦU": "...",
    "6. RÀNG BUỘC": "...", "7. TASK": "...", "8. ĐỊNH DẠNG ĐẦU RA": "...", "9. NEVER DO": "...", 
    "10. THỨ TỰ ƯU TIÊN": "...", "11. XỬ LÝ NỘI BỘ": "..."
  }}
}}
"""
        
        last_error = None
        success = False
        ai_data = {}
        
        for attempt in range(2):
            try:
                raw_text = call_llm(system_prompt, prompt_text)
                json_str = extract_json(raw_text)
                if not json_str: raise ReportValidationError("AI không trả về JSON hợp lệ.")
                ai_data = json.loads(json_str)
                validate_full_report(ai_data, main_criteria, tech_criteria, prompt_text)
                success = True
                break
            except HTTPException: raise
            except (json.JSONDecodeError, ReportValidationError, TypeError, ValueError) as e:
                last_error = e
                logger.warning("Lần thử %s thất bại: %s", attempt + 1, e)
        
        if not success: raise ReportValidationError(f"Dữ liệu không hợp lệ: {last_error}")

        # Tính điểm và gộp tên tiêu chí động vào kết quả
        final_score = calculate_final_score(ai_data["scores"], main_criteria, tech_criteria)
        
        display_details = {}
        for k, v in ai_data["scores"].items():
            if k in all_criteria:
                display_details[all_criteria[k]["name"]] = v
            elif k in ai_data.get("dynamic_criteria_names", {}):
                display_details[ai_data["dynamic_criteria_names"][k]] = v
        
        result = {
            "prompt": prompt_text, "type": main_task, "techniques": techniques, 
            "total": final_score, "details": display_details,
            "errors": ai_data.get("errors", []), 
            "rewrite": ai_data["rewrite"]
        }

        db_payload = {
            "prompt": prompt_text, "type": main_task, "total_score": final_score,
            "details": result["details"], "errors": result["errors"], "rewrite": result["rewrite"],
        }
        background_tasks.add_task(bg_save_history, db_payload)
        return result

    except ReportValidationError as re_err:
        return JSONResponse(status_code=422, content={"error": str(re_err)})
    except HTTPException as http_err: raise http_err
    except Exception as e:
        logger.exception("Lỗi nghiêm trọng trong /evaluate")
        return JSONResponse(status_code=500, content={"error": "Lỗi máy chủ nội bộ."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))