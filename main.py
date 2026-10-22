# ... (Giữ nguyên toàn bộ code phía trên của main.py) ...

@app.post("/evaluate")
@limiter.limit(RATE_LIMIT)
def evaluate(request: Request, req: PromptRequest, background_tasks: BackgroundTasks):
    prompt_text = req.prompt.strip()
    if not prompt_text: return JSONResponse(status_code=400, content={"error": "Prompt trống."})
    if len(prompt_text) > MAX_PROMPT_LENGTH: return JSONResponse(status_code=400, content={"error": f"Prompt vượt quá {MAX_PROMPT_LENGTH} ký tự."})

    background_tasks.add_task(bg_cleanup_history)

    try:
        classification = rules_v38.classify_prompt(prompt_text)
        if classification["main_task"] == rules_v38.TYPE_EMPTY: return JSONResponse(status_code=400, content={"error": "Nội dung không hợp lệ."})

        criteria_pack = rules_v38.get_criteria_by_type(classification)
        main_task = classification["main_task"]
        techniques = classification["techniques"]
        main_criteria = criteria_pack["main"]
        tech_criteria = criteria_pack["tech"]
        
        all_criteria = {**main_criteria, **tech_criteria}
        criteria_desc = "".join([f"- ID {k} ({v['name']}): {v['rubric']}\n" for k, v in all_criteria.items()])
        error_codes_desc = "\n".join([f"- {k}: {v}" for k, v in rules_v38.VALID_ERROR_CODES.items()])
        scores_example = ", ".join([f'"{k}": 8' for k in all_criteria.keys()])

        system_prompt = f"""
Bạn là Chuyên gia Prompt Engineering. Đánh giá và viết lại câu lệnh của người dùng theo form 11 mục.

BƯỚC 1: XÁC ĐỊNH LĨNH VỰC & CHUYÊN GIA.
BƯỚC 2: VIẾT LẠI PROMPT THEO ĐÚNG CẤU TRÚC JSON SAU (Sử dụng \\n để xuống dòng trong nội dung):
{{
  "scores": {{ {scores_example} }},
  "errors": [ {{"code": "[Mã lỗi]", "evidence": "[Trích dẫn hoặc 'Toàn bộ']"}} ],
  "rewrite": {{ 
    "1. VAI TRÒ": "...", "2. BỐI CẢNH": "...", "3. INPUT": "...", "4. MỤC TIÊU": "...", "5. YÊU CẦU": "...",
    "6. RÀNG BUỘC": "...", "7. TASK": "...", "8. ĐỊNH DẠNG ĐẦU RA": "...", "9. NEVER DO": "...", 
    "10. THỨ TỰ ƯU TIÊN": "...", "11. XỬ LÝ NỘI BỘ": "..."
  }}
}}

THANG ĐIỂM (RUBRIC):
{criteria_desc}

MÃ LỖI:
{error_codes_desc}

CHỈ TRẢ VỀ CHUỖI JSON HỢP LỆ. KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO KHÁC.
"""
        
        ai_data = None
        last_error = ""
        for attempt in range(2):
            try:
                raw_text = call_llm(system_prompt, prompt_text)
                if not raw_text: raise ReportValidationError("AI trả về rỗng.")
                
                json_str = extract_json(raw_text)
                ai_data = json.loads(json_str)
                validate_full_report(ai_data, main_criteria, tech_criteria, prompt_text)
                break 
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Lần {attempt+1}: Lỗi ({e}). Đang thử lại...")
                ai_data = None

        if ai_data is None:
            # Trả về lỗi chi tiết để dễ debug
            return JSONResponse(status_code=502, content={"error": f"AI trả về dữ liệu không hợp lệ: {last_error}"})

        final_score = calculate_final_score(ai_data["scores"], main_criteria, tech_criteria)
        display_details = {all_criteria[k]["name"]: v for k, v in ai_data["scores"].items() if k in all_criteria}
        
        result = {
            "prompt": prompt_text, "type": main_task, "techniques": techniques, 
            "total": final_score, "details": display_details,
            "errors": ai_data.get("errors", []), "rewrite": ai_data["rewrite"]
        }

        db_payload = {
            "prompt": prompt_text, "type": main_task, "total_score": final_score,
            "details": result["details"], "errors": result["errors"], "rewrite": result["rewrite"],
        }
        background_tasks.add_task(bg_save_history, db_payload)
        return result

    except rules_v38.ConfigurationError as ce:
        logger.error(f"LỖI CẤU HÌNH: {ce}")
        return JSONResponse(status_code=500, content={"error": "Lỗi cấu hình hệ thống."})
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Lỗi nghiêm trọng trong /evaluate")
        # Bắt lỗi và trả về chi tiết
        return JSONResponse(status_code=500, content={"error": f"Lỗi máy chủ: {str(e)}"})
