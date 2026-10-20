from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import time
from groq import Groq

import rules_v38
from validator import validate_full_report, calculate_final_score

app = FastAPI()

# Cấu hình CORS để Frontend (GitHub Pages) có thể gọi được API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

# Lấy API Key Groq từ biến môi trường Render
api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    print("CẢNH BÁO: CHƯA CÓ GROQ_API_KEY TRÊN RENDER!")

client = Groq(api_key=api_key)

# ==========================================
# [SỬA LỖI 1 & 2]: THÊM ROUTE GỐC VÀ HEALTH CHECK
# Giúp Render không báo lỗi 404 và UptimeRobot có thể ping để giữ server không bị ngủ.
# ==========================================
@app.get("/")
def read_root():
    return {"status": "Backend Hệ thống Đánh giá Prompt đang chạy ổn định!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ==========================================
# API CHÍNH: ĐÁNH GIÁ PROMPT
# ==========================================
@app.post("/evaluate")
async def evaluate(req: PromptRequest):
    prompt_text = req.prompt.strip()
    if not prompt_text:
        return {"error": "Prompt trống, vui lòng nhập nội dung cần đánh giá."}
    
    try:
        # Phân loại prompt tự động
        content_type = rules_v38.classify_prompt(prompt_text)
        criteria = rules_v38.get_criteria_by_type(content_type)
        
        if not criteria:
            return {"error": "Không xác định được loại tiêu chí phù hợp."}
        
        # Tạo danh sách tiêu chí và mã lỗi để đưa vào Prompt của AI
        criteria_desc = "\n".join([f"- {k}: {v['name']}" for k, v in criteria.items()])
        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in criteria.keys()])
        
        system_prompt = f"""
Bạn là chuyên gia đánh giá prompt. Chấm điểm prompt sau. Điểm mỗi tiêu chí từ 0-10.
BƯỚC 1: Chấm điểm dựa trên bản gốc.
BƯỚC 2: Viết 11 mục bản sửa, tự động sửa lỗi chính tả cho người dùng.

TIÊU CHÍ BẮT BUỘC (Chỉ dùng các ID này):
{criteria_desc}

MÃ LỖI BẮT BUỘC (Nếu có lỗi, chỉ dùng các mã này):
{error_codes_desc}

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ (Không markdown, không giải thích thêm):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn nguyên văn từ prompt gốc]"}} ],
  "rewrite": {{ 
    "1. VAI TRÒ": "...", "2. BỐI CẢNH": "...", "3. INPUT": "...", 
    "4. MỤC TIÊU": "...", "5. YÊU CẦU": "...", "6. RÀNG BUỘC": "...", 
    "7. TASK": "...", "8. ĐỊNH DẠNG ĐẦU RA": "...", "9. NEVER DO": "...", 
    "10. THỨ TỰ ƯU TIÊN": "...", "11. XỬ LÝ NỘI BỘ": "..." 
  }}
}}

Prompt gốc cần đánh giá: {prompt_text}
"""

        max_retries = 3
        response = None
        
        # [SỬA LỖI 3]: Đổi sang model Llama 3 hợp lệ của Groq
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_text}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                break
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "rate_limit" in error_msg:
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    else:
                        return {"error": "Hệ thống Groq đang quá tải. Vui lòng thử lại sau ít phút!"}
                raise e
        
        # Xử lý kết quả trả về từ AI
        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```json"): 
            raw_text = raw_text[7:-3].strip()
        
        ai_data = json.loads(raw_text)
        
        # Kiểm tra chéo dữ liệu bằng Python (Validator)
        validate_full_report(ai_data, content_type, prompt_text)
        
        # Tính điểm tổng bằng Python (không tin AI)
        final_score = calculate_final_score(ai_data["scores"], content_type)
        
        # Trả kết quả về cho Frontend
        return {
            "prompt": prompt_text,
            "type": content_type,
            "total": final_score,
            "details": {criteria[k]["name"]: v for k, v in ai_data["scores"].items()},
            "rewrite": ai_data["rewrite"]
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
