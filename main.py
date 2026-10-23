import os
import json
import re
import time
import logging
import secrets
import datetime
import uvicorn
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
    raise RuntimeError("LỖI BẢO MẬT: Thiếu biến môi trường bắt buộc trên Render.")

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
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1, 
            timeout=30.0
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq thất bại: {e}")
        raise HTTPException(status_code=503, detail="Hệ thống AI đang quá tải. Vui lòng thử lại sau 1 phút.")

def bg_save_history(payload: dict):
    if not supabase: return
    try:
        supabase.table("history").insert(payload).execute()
    except Exception as e:
        # Lờ đi lỗi trùng lặp prompt
        if '23505' in str(e) or 'duplicate key' in str(e):
            pass
        else:
            logger.error(f"LỖI BACKGROUND: Không thể lưu lịch sử: {e}")

@app.get("/")
def read_root(): return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check(): return {"status": "ok"}

@app.post("/evaluate")
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
        # CHỈ GỬI ID VÀ TÊN, KHÔNG GỬI RUBRIC ĐỂ TIẾT KIỆM TOKEN
        criteria_desc = "".join([f"- {k}: {v['name']}\n" for k, v in all_criteria.items()])
        scores_example = ", ".join([f'"{k}": 5' for k in all_criteria.keys()])
        
        # CHỈ GỬI MÃ VÀ TÊN LỖI (BỎ HẾT MÔ TẢ DÀI DÒNG)
        error_codes_desc = ""
        for code, rule in error_rules.ERROR_RULES.items():
            error_codes_desc += f"- {code}: {rule['name']}\n"
        
        # RÚT GỌN TỐI ĐA SYSTEM PROMPT
        system_prompt = f"""
Bạn là chuyên gia chấm điểm Prompt. Hãy chấm điểm các tiêu chí sau (0-10):
{criteria_desc}

Phát hiện lỗi trong các mã sau:
{error_codes_desc}

Viết lại prompt thành 11 mục. Mỗi mục nếu có nhiều ý phải dùng \\n để xuống dòng.
11 mục: "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ".

Trả về JSON chính xác cấu trúc sau (KHÔNG THÊM KEY NÀO KHÁC):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "MÃ_LỖI", "evidence": "Trích dẫn"}} ],
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
                if not json_str:
                    raise ReportValidationError("AI không trả về JSON hợp lệ.")
                ai_data = json.loads(json_str)
                validate_full_report(ai_data, main_criteria, tech_criteria, prompt_text)
                success = True
                break
            except HTTPException:
                raise
            except (json.JSONDecodeError, ReportValidationError, TypeError, ValueError) as e:
                last_error = e
                logger.warning("Lần thử %s thất bại: %s", attempt + 1, e)
        
        if not success:
            raise ReportValidationError(f"AI trả về dữ liệu không hợp lệ sau 2 lần thử: {last_error}")

        final_score = calculate_final_score(ai_data["scores"], main_criteria, tech_criteria)
        display_details = {all_criteria[k]["name"]: v for k, v in ai_data["scores"].items() if k in all_criteria}
        
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
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.exception("Lỗi nghiêm trọng trong /evaluate")
        return JSONResponse(status_code=500, content={"error": "Lỗi máy chủ nội bộ."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
