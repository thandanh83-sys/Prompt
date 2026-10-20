from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import time
from groq import Groq
from supabase import create_client, Client

import rules_v38
from validator import validate_full_report, calculate_final_score

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PromptRequest(BaseModel):
    prompt: str

api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

@app.get("/")
def read_root(): return {"status": "Backend đang chạy ổn định!"}

@app.get("/health")
def health_check(): return {"status": "ok"}

@app.post("/evaluate")
async def evaluate(req: PromptRequest):
    prompt_text = req.prompt.strip()
    if not prompt_text: return {"error": "Prompt trống."}
    
    # 1. KIỂM TRA CACHE TRÊN SUPABASE
    if supabase:
        try:
            response_db = supabase.table("history").select("*").eq("prompt", prompt_text).execute()
            if response_db.data:
                cached_data = response_db.data[0]
                return {
                    "prompt": cached_data["prompt"], "type": cached_data["type"],
                    "total": cached_data["total_score"], "details": cached_data["details"],
                    "errors": cached_data["errors"], "rewrite": cached_data["rewrite"]
                }
        except Exception as e: print(f"Lỗi đọc Supabase: {e}")

    # 2. GỌI AI
    try:
        content_type = rules_v38.classify_prompt(prompt_text)
        criteria = rules_v38.get_criteria_by_type(content_type)
        if not criteria: return {"error": "Không xác định được loại tiêu chí."}
        
        criteria_desc = "\n".join([f"- {k}: {v['name']}" for k, v in criteria.items()])
        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in criteria.keys()])
        
        # [CẬP NHẬT PROMPT AI]: Cấm AI tự ý sửa chữ khi trích dẫn
        system_prompt = f"""
Bạn là chuyên gia đánh giá prompt. Chấm điểm prompt sau. Điểm mỗi tiêu chí từ 0-10.
BƯỚC 1: Chấm điểm dựa trên bản gốc.
BƯỚC 2: Viết 11 mục bản sửa.

TIÊU CHÍ BẮT BUỘC:
{criteria_desc}

MÃ LỖI BẮT BUỘC:
{error_codes_desc}

LƯU Ý VỀ BẰNG CHỨNG (evidence) - CỰC KỲ QUAN TRỌNG:
- Bạn phải trích xuất bằng chứng (evidence) CHÍNH XÁC TỪNG CHỮ từ Prompt gốc, không được tự ý sửa chữ, đảo chữ hay thêm bớt.
- Nếu lỗi thuộc về toàn bộ câu (như thiếu bối cảnh, thiếu mục tiêu), hãy ghi ngắn gọn CHÍNH XÁC là "Toàn bộ prompt".

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ:
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn chính xác hoặc 'Toàn bộ prompt']"}} ],
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
                    response_format={"type": "json_object"}, temperature=0.0, top_p=0.1 
                )
                break
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e):
                    if attempt < max_retries - 1: time.sleep(3); continue
                    else: return {"error": "Hệ thống AI quá tải."}
                raise e
        
        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:-3].strip()
        
        ai_data = json.loads(raw_text)

        # [THÊM MỚI]: TỰ ĐỘNG LÀM SẠCH DỮ LIỆU (AUTO-SANITIZE)
        # Nếu AI trả về bằng chứng sai (không nằm trong prompt gốc), tự động sửa thành "Toàn bộ prompt"
        if "errors" in ai_data and isinstance(ai_data["errors"], list):
            for err in ai_data["errors"]:
                evidence = str(err.get("evidence", "")).strip()
                if evidence and evidence.lower() != "toàn bộ prompt" and evidence not in prompt_text:
                    print(f"Đã tự động sửa lỗi AI trích dẫn sai: '{evidence}' -> 'Toàn bộ prompt'")
                    err["evidence"] = "Toàn bộ prompt"

        validate_full_report(ai_data, content_type, prompt_text)
        final_score = calculate_final_score(ai_data["scores"], content_type)
        
        result = {
            "prompt": prompt_text, "type": content_type, "total": final_score,
            "details": {criteria[k]["name"]: v for k, v in ai_data["scores"].items()},
            "errors": ai_data["errors"], "rewrite": ai_data["rewrite"]
        }

        # 3. LƯU VÀO SUPABASE
        if supabase:
            try:
                supabase.table("history").insert({
                    "prompt": prompt_text, "type": content_type, "total_score": final_score,
                    "details": result["details"], "errors": result["errors"], "rewrite": result["rewrite"]
                }).execute()
            except Exception as e: print(f"Lỗi lưu Supabase: {e}")

        return result
    except Exception as e: return {"error": str(e)}

if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8000)
