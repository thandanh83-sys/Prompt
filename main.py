from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
from google import genai
from google.genai import types

import rules_v38
from validator import validate_full_report, calculate_final_score

app = FastAPI()

# Cấu hình CORS để GitHub Pages (Frontend) có thể gọi API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

# Lấy API Key từ biến môi trường trên Render
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    print("CẢNH BÁO: CHƯA CÓ GEMINI_API_KEY!")

client = genai.Client(api_key=api_key)

@app.post("/evaluate")
async def evaluate(req: PromptRequest):
    prompt_text = req.prompt.strip()
    if not prompt_text:
        return {"error": "Prompt trống"}
    
    try:
        # 1. Phân loại prompt (v38)
        content_type = rules_v38.classify_prompt(prompt_text)
        criteria = rules_v38.get_criteria_by_type(content_type)
        
        # 2. Chuẩn bị Prompt cho AI
        criteria_desc = "\n".join([f"- {k}: {v['name']}" for k, v in criteria.items()])
        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        
        # Tạo mẫu JSON động để tránh AI bị nhầm lẫn cú pháp
        scores_example = ", ".join([f'"{k}": 8' for k in criteria.keys()])
        
        system_prompt = f"""
Bạn là chuyên gia đánh giá prompt. Chấm điểm prompt sau. Điểm mỗi tiêu chí từ 0-10.
BƯỚC 1: Chấm điểm dựa trên bản gốc (nếu người dùng viết sai chính tả, trừ điểm).
BƯỚC 2: Viết 11 mục bản sửa, tự động sửa lỗi chính tả để tạo ra prompt hoàn hảo.

TIÊU CHÍ:
{criteria_desc}

MÃ LỖI:
{error_codes_desc}

TRẢ VỀ ĐÚNG CHUỖI JSON (Không markdown, không giải thích):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn từ prompt gốc]"}} ],
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

Prompt gốc: {prompt_text}
"""
        
        # 3. Gọi AI (Đã sửa sang model 2.5-flash)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", 
                temperature=0.0
            )
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"): 
            raw_text = raw_text[7:-3].strip()
        
        # 4. Kiểm tra dữ liệu (v38 Validator)
        ai_data = json.loads(raw_text)
        validate_full_report(ai_data, content_type, prompt_text)
        final_score = calculate_final_score(ai_data["scores"], content_type)
        
        # 5. Trả kết quả về cho Frontend
        return {
            "prompt": prompt_text,
            "type": content_type,
            "total": final_score,
            "details": {criteria[k]["name"]: v for k, v in ai_data["scores"].items()},
            "rewrite": ai_data["rewrite"]
        }
        
    except Exception as e:
        # Nếu có lỗi, trả về chi tiết để hiển thị lên màn hình đỏ
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
