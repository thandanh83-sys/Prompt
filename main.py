from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import time
from google import genai

import rules_v38
from validator import validate_full_report, calculate_final_score

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

@app.post("/evaluate")
async def evaluate(req: PromptRequest):
    prompt_text = req.prompt.strip()
    if not prompt_text:
        return {"error": "Prompt trống"}
    
    try:
        content_type = rules_v38.classify_prompt(prompt_text)
        criteria = rules_v38.get_criteria_by_type(content_type)
        
        criteria_desc = "\n".join([f"- {k}: {v['name']}" for k, v in criteria.items()])
        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in criteria.keys()])
        
        system_prompt = f"""
Bạn là chuyên gia đánh giá prompt. Chấm điểm prompt sau. Điểm mỗi tiêu chí từ 0-10.
BƯỚC 1: Chấm điểm dựa trên bản gốc.
BƯỚC 2: Viết 11 mục bản sửa, tự động sửa lỗi chính tả.

TIÊU CHÍ:
{criteria_desc}

MÃ LỖI:
{error_codes_desc}

TRẢ VỀ ĐÚNG CHUỖI JSON (Không markdown):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn]"}} ],
  "rewrite": {{ "1. VAI TRÒ": "...", "2. BỐI CẢNH": "...", "3. INPUT": "...", "4. MỤC TIÊU": "...", "5. YÊU CẦU": "...", "6. RÀNG BUỘC": "...", "7. TASK": "...", "8. ĐỊNH DẠNG ĐẦU RA": "...", "9. NEVER DO": "...", "10. THỨ TỰ ƯU TIÊN": "...", "11. XỬ LÝ NỘI BỘ": "..." }}
}}

Prompt gốc: {prompt_text}
"""

        max_retries = 3
        response = None
        
        for attempt in range(max_retries):
            try:
                response = client.interactions.create(
                    model="gemini-3.8-flash", 
                    input=system_prompt,
                    response_format={
                        "type": "text",
                        "mime_type": "application/json"
                    }
                )
                break
            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                raise e
        
        raw_text = response.output_text.strip()
        if raw_text.startswith("```json"): 
            raw_text = raw_text[7:-3].strip()
        
        ai_data = json.loads(raw_text)
        validate_full_report(ai_data, content_type, prompt_text)
        final_score = calculate_final_score(ai_data["scores"], content_type)
        
        return {
            "prompt": prompt_text,
            "type": content_type,
            "total": final_score,
            "details": {criteria[k]["name"]: v for k, v in ai_data["scores"].items()},
            "rewrite": ai_data["rewrite"]
        }
        
    except Exception as e:
        return {"error": str(e)}
