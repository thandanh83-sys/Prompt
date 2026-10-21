import os
import json
import time
import logging
import secrets
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

import rules_v38
from validator import validate_full_report, calculate_final_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prompt-evaluator")

MAX_PROMPT_LENGTH = 5000
RATE_LIMIT = "20/minute"
GENERIC_ERROR = {"error": "Hệ thống đang bận, vui lòng thử lại sau."}

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_SECRET_TOKEN = os.environ.get("ADMIN_SECRET_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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

limiter = Limiter(key_func=get_client_ip)
app = FastAPI()
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "Bạn đã đạt giới hạn sử dụng, vui lòng thử lại sau 1 phút."})

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token"],
)

class PromptRequest(BaseModel):
    prompt: str

class LoginRequest(BaseModel):
    password: str

client = Groq(api_key=GROQ_API_KEY)
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

def call_llm(system_prompt: str, user_prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"<prompt_can_cham>\n{user_prompt}\n</prompt_can_cham>"},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"Lỗi gọi LLM (Lần {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

@app.get("/")
def read_root(): return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check(): return {"status": "ok"}

@app.post("/login")
@limiter.limit("5/minute")
def admin_login(request: Request, req: LoginRequest):
    if secrets.compare_digest(req.password, ADMIN_PASSWORD):
        return {"token": ADMIN_SECRET_TOKEN}
    raise HTTPException(status_code=401, detail="Sai mật khẩu")

@app.get("/history")
def get_history(token: str = Depends(api_key_header)):
    if not token or not secrets.compare_digest(token, ADMIN_SECRET_TOKEN):
        raise HTTPException(status_code=401, detail="Không có quyền truy cập")
    if not supabase:
        return {"history": [], "message": "Supabase chưa được cấu hình"}
    try:
        res = supabase.table("history").select("prompt, type, total_score, created_at, errors").order("created_at", desc=True).limit(50).execute()
        return {"history": res.data}
    except Exception as e:
        logger.error(f"Lỗi lấy lịch sử: {e}")
        raise HTTPException(status_code=500, detail="Lỗi máy chủ")

@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest):
    prompt_text = req.prompt.strip()

    if not prompt_text:
        return JSONResponse(status_code=400, content={"error": "Prompt trống."})
    if len(prompt_text) > MAX_PROMPT_LENGTH:
        return JSONResponse(status_code=400, content={"error": f"Prompt vượt quá {MAX_PROMPT_LENGTH} ký tự."})

    try:
        content_type = rules_v38.classify_prompt(prompt_text)
        criteria = rules_v38.get_criteria_by_type(content_type)
        
        criteria_desc = ""
        for k, v in criteria.items():
            criteria_desc += f"- ID {k} ({v['name']}): {v['rubric']}\n"

        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in criteria.keys()])

        # Cải thiện System Prompt để AI hiểu cả prompt dài
        system_prompt = f"""
Bạn là Chuyên gia Prompt Engineering. Nhiệm vụ của bạn là đánh giá câu lệnh của người dùng và viết lại nó.
LƯU Ý QUAN TRỌNG: Nếu người dùng dán vào một prompt đã có cấu trúc 11 mục, hãy đánh giá nó dựa trên cấu trúc đó, và tinh chỉnh lại cho hoàn hảo hơn. Đừng cố gắng tạo lại từ đầu nếu nó đã quá tốt.

BƯỚC 1: XÁC ĐỊNH LĨNH VỰC & CHUYÊN GIA.
BƯỚC 2: VIẾT LẠI PROMPT THEO ĐÚNG CẤU TRÚC JSON SAU (Sử dụng \\n để xuống dòng trong nội dung):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn hoặc 'Toàn bộ']"}} ],
  "rewrite": {{ 
    "1. VAI TRÒ": "...",
    "2. BỐI CẢNH": "...",
    "3. INPUT": "...",
    "4. MỤC TIÊU": "...",
    "5. YÊU CẦU": "...",
    "6. RÀNG BUỘC": "...",
    "7. TASK": "...",
    "8. ĐỊNH DẠNG ĐẦU RA": "...",
    "9. NEVER DO": "...",
    "10. THỨ TỰ ƯU TIÊN": "...",
    "11. XỬ LÝ NỘI BỘ": "..."
  }}
}}

THANG ĐIỂM (RUBRIC):
{criteria_desc}

MÃ LỖI:
{error_codes_desc}

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ. KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO KHÁC.
"""
        raw_text = call_llm(system_prompt, prompt_text)

        # LÀM SẠCH JSON (Sửa lỗi nếu AI trả về kèm ```json)
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.replace("```", "").strip()

        ai_data = json.loads(raw_text)

        # [AUTO-REPAIR]: Tự động sửa lỗi nếu AI trả về thiếu mục
        try:
            validate_full_report(ai_data, content_type, prompt_text)
        except ValueError as ve:
            logger.warning(f"AI trả về sai cấu trúc: {ve}. Đang tự động sửa (Auto-Repair)...")
            
            if "scores" not in ai_data or not isinstance(ai_data["scores"], dict): ai_data["scores"] = {}
            for k in criteria.keys():
                if k not in ai_data["scores"]: ai_data["scores"][k] = 0

            if "rewrite" not in ai_data or not isinstance(ai_data["rewrite"], dict): ai_data["rewrite"] = {}
            for sec in rules_v38.REQUIRED_REWRITE_SECTIONS:
                if sec not in ai_data["rewrite"]: ai_data["rewrite"][sec] = "[AI chưa tạo được mục này]"

            valid_errors = []
            if "errors" in ai_data and isinstance(ai_data["errors"], list):
                for err in ai_data["errors"]:
                    if isinstance(err, dict) and err.get("code") in rules_v38.VALID_ERROR_CODES:
                        valid_errors.append(err)
            ai_data["errors"] = valid_errors

        final_score = calculate_final_score(ai_data["scores"], content_type)

        result = {
            "prompt": prompt_text, "type": content_type, "total": final_score,
            "details": {criteria[k]["name"]: v for k, v in ai_data["scores"].items()},
            "errors": ai_data.get("errors", []), "rewrite": ai_data["rewrite"],
        }

        if supabase:
            try:
                supabase.table("history").insert({
                    "prompt": prompt_text, "type": content_type, "total_score": final_score,
                    "details": result["details"], "errors": result["errors"], "rewrite": result["rewrite"],
                }).execute()
            except Exception as e:
                logger.error(f"Lỗi lưu Supabase: {e}")

        return result

    except json.JSONDecodeError:
        logger.error("AI trả về JSON không hợp lệ.")
        return JSONResponse(status_code=500, content={"error": "AI trả về dữ liệu lỗi. Vui lòng thử lại với prompt ngắn hơn."})
    except Exception as e:
        logger.exception("Lỗi trong /evaluate")
        # Trả về chi tiết lỗi để người dùng biết
        return JSONResponse(status_code=500, content={"error": f"Lỗi xử lý: {str(e)[:100]}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))