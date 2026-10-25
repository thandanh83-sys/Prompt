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
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối.")
    return client_ip

def verify_admin_token(token: str = Depends(api_key_header)):
    if not token or token != ADMIN_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn.")
    return token

# ==========================================
# KHỞI TẠO FASTAPI VÀ CẤU HÌNH MIDDLEWARE
# ==========================================
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

# KHAI BÁO CÁC CLASS REQUEST
class PromptRequest(BaseModel):
    prompt: str

class AdminLoginRequest(BaseModel):
    password: str

# Sử dụng Groq
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

# [TỐI ƯU] Chỉ dùng 1 model duy nhất là 120b, timeout lên 40s để chống Cold Start của Render
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
            max_tokens=3000, 
            timeout=40.0 # Tăng lên 40s
        )
        return resp.choices[0].message.content
    except RateLimitError as e:
        logger.warning(f"Groq Rate Limit Reached: {e}")
        raise HTTPException(status_code=429, detail="Hệ thống đang bận. Vui lòng đợi 1 phút rồi thử lại!")
    except Exception as e:
        logger.error(f"Groq thất bại: {e}")
        raise HTTPException(status_code=503, detail="Hệ thống AI đang quá tải. Vui lòng thử lại sau.")

def bg_save_history(payload: dict):
    if not supabase: return
    try:
        supabase.table("history").insert(payload).execute()
    except Exception as e:
        if '23505' in str(e) or 'duplicate key' in str(e):
            pass
        else:
            logger.error(f"LỖI BACKGROUND: Không thể lưu lịch sử: {e}")

@app.get("/")
def read_root(): return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check(): return {"status": "ok"}

@app.get("/check_admin_ip")
def check_admin_ip(client_ip: str = Depends(verify_admin_ip)):
    return {"is_admin": True}

# ==========================================
# API ĐĂNG NHẬP ADMIN
# ==========================================
@app.post("/login")
def login(req: AdminLoginRequest, request: Request):
    if req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Sai mật khẩu")
    
    if supabase:
        try:
            client_ip = get_client_ip(request)
            user_agent = request.headers.get("user-agent", "Unknown")
            supabase.table("admin_login_logs").insert({
                "ip_address": client_ip,
                "user_agent": user_agent
            }).execute()
        except Exception as e:
            logger.error(f"Lỗi lưu log admin login: {e}")

    return {"token": ADMIN_SECRET_TOKEN}

# ==========================================
# API LẤY LỊCH SỬ ĐÁNH GIÁ (CHO ADMIN)
# ==========================================
@app.get("/history")
def get_history(token: str = Depends(verify_admin_token)):
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase chưa cấu hình."})
    try:
        response = supabase.table("history").select("*").order("created_at", desc=True).limit(100).execute()
        return {"history": response.data}
    except Exception as e:
        logger.error(f"Lỗi lấy history: {e}")
        return JSONResponse(status_code=500, content={"error": "Không thể lấy lịch sử."})

# ==========================================
# API XÓA PROMPT (CHO ADMIN)
# ==========================================
@app.delete("/admin/delete_prompt/{prompt_id}")
def delete_prompt(prompt_id: str, token: str = Depends(verify_admin_token)):
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase chưa cấu hình."})
    try:
        supabase.table("history").delete().eq("id", prompt_id).execute()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Lỗi xóa prompt: {e}")
        return JSONResponse(status_code=500, content={"error": "Không thể xóa prompt."})

@app.delete("/admin/delete_all_prompts")
def delete_all_prompts(token: str = Depends(verify_admin_token)):
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase chưa cấu hình."})
    try:
        supabase.table("history").delete().neq("id", "0").execute()
        return {"status": "success", "message": "Đã xóa toàn bộ lịch sử."}
    except Exception as e:
        logger.error(f"Lỗi xóa toàn bộ prompt: {e}")
        return JSONResponse(status_code=500, content={"error": "Không thể xóa toàn bộ dữ liệu."})

# ==========================================
# API LẤY LỊCH SỬ IP ĐĂNG NHẬP ADMIN
# ==========================================
@app.get("/admin/ip_logs")
def get_ip_logs(token: str = Depends(verify_admin_token)):
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase chưa cấu hình."})
    try:
        response = supabase.table("admin_login_logs").select("*").order("login_time", desc=True).limit(50).execute()
        return {"logs": response.data}
    except Exception as e:
        logger.error(f"Lỗi lấy IP logs: {e}")
        return JSONResponse(status_code=500, content={"error": "Không thể lấy log IP."})

# ==========================================
# API LẤY DANH SÁCH PROMPT CHO THƯ VIỆN
# ==========================================
@app.get("/top_prompts")
def get_top_prompts():
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase chưa được cấu hình."})
    
    try:
        response = supabase.table("history") \
            .select("prompt", "type", "total_score", "created_at") \
            .gte("total_score", 7.0) \
            .limit(50) \
            .execute()
        
        prompts = response.data
        
        if len(prompts) > 5:
            prompts = random.sample(prompts, 5)
            
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Lỗi khi lấy top prompts: {e}")
        return JSONResponse(status_code=500, content={"error": "Không thể lấy dữ liệu thư viện."})

# ==========================================
# API ĐÁNH GIÁ PROMPT (AI)
# ==========================================
@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest, background_tasks: BackgroundTasks):
    prompt_text = req.prompt.strip()
    
    if not prompt_text:
        return JSONResponse(status_code=400, content={"error": "Vui lòng nhập Prompt."})
        
    if len(prompt_text) > MAX_PROMPT_LENGTH:
        return JSONResponse(status_code=400, content={"error": f"Prompt quá dài, vượt quá {MAX_PROMPT_LENGTH} ký tự."})
        
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
            
        rewrite_sections_formatted = ", ".join([f'"{s}"' for s in rules_v38.REQUIRED_REWRITE_SECTIONS])

        system_prompt = f"""
Bạn là Chuyên gia Kiểm định Prompt. Hãy thực hiện 4 bước sau và trả về JSON:

[BƯỚC 1: XÁC ĐỊNH LĨNH VỰC & INPUT RÁC]
- Lĩnh vực: Code, Cosmetics, Marketing, Writing, Education, General.
- [QUY TẮC ĐẶC BIỆT VỀ INPUT RÁC]: Nếu prompt quá ngắn (dưới 3 từ), vô nghĩa, hoặc chỉ là từ rời rạc (Ví dụ: "mạ", "tả"):
  1. Chấm 0 điểm cho TẤT CẢ các tiêu chí.
  2. Mảng "errors" để trống [].
  3. Kích hoạt chế độ [MỞ RỘNG SÁNG TẠO] ở Bước 4: Tự phỏng đoán ý định (VD: "tả" -> tả mẹ), và viết mới một prompt 11 mục thật hoàn chỉnh, chuyên nghiệp.

[BƯỚC 2: CHẤM ĐIỂM & TIÊU CHÍ ĐỘNG]
2.1. Chấm điểm lõi (0-10):
{criteria_desc}
2.2. Tự sinh 3 tiêu chí chuyên ngành (DYN01, DYN02, DYN03) và chấm điểm.

[BƯỚC 3: LỖI]
Đối chiếu mã lỗi:
{error_codes_desc}
- Evidence: KHÔNG dùng ngoặc kép. Lỗi B01, C02, C04 ghi đúng "Không có thông tin này trong prompt". Bắt buộc thêm "hint".

[BƯỚC 4: TÁI CẤU TRÚC VÀ CẢI TIẾN (REWRITE)]
Viết lại đúng 11 mục tiếng Việt:
{rewrite_sections_formatted}

[NGUYÊN TẮC VÀNG KHI VIẾT LẠI - BẮT BUỘC TUÂN THỦ]:
1. TUYỆT ĐỐI KHÔNG ĐƯỢC XÓA HOẶC TÓM TẮT Ý CỦA NGƯỜI DÙNG.
2. Với phần điểm cao (8-10): BẮT BUỘC BÊ NGUYÊN VĂN từ ngữ của họ vào mục tương ứng.
3. Với phần điểm thấp (<8): ĐƯỢC PHÉP viết thêm ý mới, bổ sung chi tiết, nhưng PHẢI GIỮ LẠI từ khóa/ý chính cốt lõi của họ.
4. Nếu là INPUT RÁC: Hãy tự sáng tác một prompt 11 mục xuất sắc dựa trên phỏng đoán.

TRẢ VỀ DUY NHẤT JSON SAU:
{{
  "identified_domain": "...",
  "scores": {{ {scores_example}, "DYN01": 5, "DYN02": 5, "DYN03": 5 }},
  "dynamic_criteria_names": {{ "DYN01": "...", "DYN02": "...", "DYN03": "..." }},
  "errors": [ {{ "code": "MÃ_LỖI", "evidence": "Không có thông tin này trong prompt", "hint": "..." }} ],
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
        
        # [TỐI ƯU] Chỉ thử lại 1 lần, không dùng 2 model để tránh bị chậm
        for attempt in range(2):
            try:
                raw_text = call_llm(system_prompt, prompt_text)
                json_str = extract_json(raw_text)
                if not json_str:
                    raise ReportValidationError("AI trả về định dạng không hợp lệ.")
                ai_data = json.loads(json_str)
                validate_full_report(ai_data, main_criteria, tech_criteria, prompt_text)
                success = True
                break
            except HTTPException:
                raise
            except (json.JSONDecodeError, ReportValidationError, TypeError, ValueError) as e:
                last_error = e
                logger.warning(f"Lần thử {attempt + 1} thất bại: {e}")
        
        if not success:
            logger.error(f"Lỗi Validation sau 2 lần thử: {last_error}")
            return JSONResponse(status_code=422, content={"error": "Hệ thống AI đang xử lý dữ liệu chưa tốt. Vui lòng thử lại!"})

        final_score = calculate_final_score(ai_data["scores"], main_criteria, tech_criteria)
        
        display_details = {}
        for k, v in ai_data["scores"].items():
            if k in all_criteria:
                display_details[all_criteria[k]["name"]] = v
            elif k in ai_data.get("dynamic_criteria_names", {}):
                display_details[ai_data["dynamic_criteria_names"][k]] = v
        
        result = {
            "prompt": prompt_text, "type": main_task, "techniques": techniques, 
            "domain": ai_data.get("identified_domain", "General"),
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

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.exception(f"Lỗi nghiêm trọng: {e}")
        return JSONResponse(status_code=500, content={"error": "Đã xảy ra lỗi kết nối máy chủ. Vui lòng thử lại sau giây lát!"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))