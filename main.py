import os
import json
import time
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

import rules_v38
from validator import validate_full_report, calculate_final_score

# ---------------------------------------------------------------------------
# Logging: mọi thứ in ra đây sẽ hiện trong tab "Logs" của Render
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prompt-evaluator")

# ---------------------------------------------------------------------------
# Hằng số cấu hình
# ---------------------------------------------------------------------------
MAX_PROMPT_LENGTH = 5000
RATE_LIMIT = "20/minute"
GENERIC_ERROR = {"error": "Hệ thống đang bận, vui lòng thử lại sau."}

# ---------------------------------------------------------------------------
# CORS (Lỗi P2)
# HƯỚNG DẪN ĐIỀN:
#   - Nếu GitHub Pages của bạn là  https://tenban.github.io/ten-repo/
#     thì origin chỉ là             https://tenban.github.io
# ---------------------------------------------------------------------------
DEFAULT_ORIGINS = [
    "https://thandanh83-sys.github.io", # <-- ĐÃ ĐIỀN LINK CỦA BẠN VÀO ĐÂY
    # "http://localhost:5500",
    # "http://127.0.0.1:5500",
]
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
    return JSONResponse(
        status_code=429,
        content={"error": "Bạn đã đạt giới hạn sử dụng, vui lòng thử lại sau 1 phút."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

class PromptRequest(BaseModel):
    prompt: str

api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None


@app.get("/")
def read_root():
    return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest):
    prompt_text = req.prompt.strip()

    if not prompt_text:
        return JSONResponse(status_code=400, content={"error": "Prompt trống."})
    if len(prompt_text) > MAX_PROMPT_LENGTH:
        return JSONResponse(status_code=400, content={"error": "Prompt vượt quá 5000 ký tự."})

    if supabase:
        try:
            response_db = supabase.table("history").select("*").eq("prompt", prompt_text).execute()
            if response_db.data:
                cached_data = response_db.data[0]
                return {
                    "prompt": cached_data["prompt"], "type": cached_data["type"],
                    "total": cached_data["total_score"], "details": cached_data["details"],
                    "errors": cached_data["errors"], "rewrite": cached_data["rewrite"],
                }
        except Exception as e:
            logger.error(f"Lỗi đọc Supabase: {e}")

    try:
        content_type = rules_v38.classify_prompt(prompt_text)
        criteria = rules_v38.get_criteria_by_type(content_type)
        if not criteria:
            logger.error(f"Không xác định được tiêu chí cho content_type={content_type!r}")
            return JSONResponse(status_code=500, content=GENERIC_ERROR)

        criteria_desc = ""
        for k, v in criteria.items():
            criteria_desc += f"- ID {k} ({v['name']}): {v['rubric']}\n"

        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in criteria.keys()])

        system_prompt = f"""
Bạn là chuyên gia đánh giá prompt. BẠN PHẢI CHẤM ĐIỂM THEO ĐÚNG THANG ĐIỂM (RUBRIC) DƯỚI ĐÂY, KHÔNG ĐƯỢC CHẤM THEO CẢM TÍNH.

THANG ĐIỂM (RUBRIC) BẮT BUỘC:
{criteria_desc}

MÃ LỖI BẮT BUỘC:
{error_codes_desc}

QUY TẮC CHỌN LỖI:
1. CHỈ CHỌN TỐI ĐA 3 LỖI NGHIÊM TRỌNG NHẤT.
2. Bằng chứng (evidence) phải trích dẫn chính xác từ Prompt gốc. Nếu lỗi áp dụng cho cả câu, BẮT BUỘC ghi CHÍNH XÁC là "Toàn bộ".

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ:
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn hoặc 'Toàn bộ']"}} ],
  "rewrite": {{ 
    "1. VAI TRÒ": "...", "2. BỐI CẢNH": "...", "3. INPUT": "...", 
    "4. MỤC TIÊU": "...", "5. YÊU CẦU": "...", "6. RÀNG BUỘC": "...", 
    "7. TASK": "...", "8. ĐỊNH DẠNG ĐẦU RA": "...", "9. NEVER DO": "...", 
    "10. THỨ TỰ ƯU TIÊN": "...", "11. XỬ LÝ NỘI BỘ": "..." 
  }}
}}
Prompt gốc: {prompt_text}
"""
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt_text}],
                    response_format={"type": "json_object"}, temperature=0.0, top_p=0.1,
                )
                break
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e):
                    logger.warning(f"Groq rate limit (lần thử {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    return JSONResponse(status_code=503, content={"error": "Hệ thống AI quá tải, vui lòng thử lại sau."})
                raise

        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()

        ai_data = json.loads(raw_text)

        if "errors" in ai_data and isinstance(ai_data["errors"], list):
            for err in ai_data["errors"]:
                evidence = str(err.get("evidence", "")).strip()
                if evidence and evidence.lower() not in ["toàn bộ", "toàn bộ prompt"] and evidence not in prompt_text:
                    logger.warning(f"[P6] Evidence không có trong prompt | code={err.get('code')!r} | evidence={evidence!r}")

        validate_full_report(ai_data, content_type, prompt_text)
        final_score = calculate_final_score(ai_data["scores"], content_type)

        result = {
            "prompt": prompt_text, "type": content_type, "total": final_score,
            "details": {criteria[k]["name"]: v for k, v in ai_data["scores"].items()},
            "errors": ai_data["errors"], "rewrite": ai_data["rewrite"],
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

    except Exception:
        logger.exception("Lỗi không mong muốn trong /evaluate")
        return JSONResponse(status_code=500, content=GENERIC_ERROR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))