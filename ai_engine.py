import json
import rules_v38
from validator import validate_full_report
import streamlit as st
from google import genai
from google.genai import types

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = "YOUR_API_KEY_HERE"

client = genai.Client(api_key=api_key)

def get_ai_evaluation(prompt_text: str, content_type: str, retries: int = 1):
    criteria = rules_v38.get_criteria_by_type(content_type)
    if not criteria: raise ValueError("Không tìm thấy tiêu chí.")
    
    criteria_desc = "\n".join([f"- {k}: {v['name']}" for k, v in criteria.items()])
    error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
    
    system_prompt = f"""
Bạn là chuyên gia đánh giá prompt. Hãy chấm điểm prompt sau. Điểm mỗi tiêu chí là số nguyên từ 0 đến 10.
BƯỚC 1: Hãy CHẤM ĐIỂM DỰA TRÊN BẢN GỐC (Nếu người dùng viết sai chính tả, trừ điểm).
BƯỚC 2: Ở phần "rewrite" (11 mục), hãy TỰ ĐỘNG SỬA LỖI CHÍNH TẢ để tạo ra prompt hoàn hảo.

DANH SÁCH TIÊU CHÍ (Trả đủ các ID này):
{criteria_desc}

DANH SÁCH MÃ LỖI (Chỉ dùng mã trong danh sách):
{error_codes_desc}

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ (Không markdown):
{{
  "scores": {{ "P01": [int], "P02": [int], "P03": [int], "P04": [int], "P05": [int], "P06": [int], "P07": [int], "P08": [int], "P09": [int], "P10": [int], "P11": [int], "P12": [int], "P13": [int], "P14": [int] }},
  "errors": [ {{"code": "[Mã]", "evidence": "[Trích dẫn]"}} ],
  "rewrite": {{ "1. VAI TRÒ": "[Nội dung]", "2. BỐI CẢNH": "[Nội dung]", "3. INPUT": "[Nội dung]", "4. MỤC TIÊU": "[Nội dung]", "5. YÊU CẦU": "[Nội dung]", "6. RÀNG BUỘC": "[Nội dung]", "7. TASK": "[Nội dung]", "8. ĐỊNH DẠNG ĐẦU RA": "[Nội dung]", "9. NEVER DO": "[Nội dung]", "10. THỨ TỰ ƯU TIÊN": "[Nội dung]", "11. XỬ LÝ NỘI BỘ": "[Nội dung]" }}
}}

Prompt gốc: {prompt_text}
"""
    
    for attempt in range(retries + 1):
        try:
            # SỬA LỖI 404: Dùng tên model chuẩn xác của thư viện mới
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=system_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            raw_text = response.text.strip()
            if raw_text.startswith("```json"): raw_text = raw_text[7:-3].strip()
            ai_data = json.loads(raw_text)
            validate_full_report(ai_data, content_type, prompt_text)
            return ai_data
            
        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"Lỗi AI: {str(e)}")
            continue
