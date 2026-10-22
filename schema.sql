-- Schema cho Prompt Evaluator.
-- Backend nên dùng Supabase service-role key qua biến môi trường, không đưa key đó vào frontend.
-- Frontend chỉ dùng anon/publishable key; RLS/policies phải giới hạn quyền truy cập.

CREATE TABLE IF NOT EXISTS public.history (
    id BIGSERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    type VARCHAR(50),
    total_score NUMERIC(3, 1),
    details JSONB,
    errors JSONB,
    rewrite JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_history_total_score
    ON public.history(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_history_created_at
    ON public.history(created_at ASC);

CREATE TABLE IF NOT EXISTS public.admin_login_logs (
    id BIGSERIAL PRIMARY KEY,
    ip_address TEXT NOT NULL,
    user_agent TEXT,
    login_time TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_login_time
    ON public.admin_login_logs(login_time DESC);

ALTER TABLE public.history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_login_logs ENABLE ROW LEVEL SECURITY;

-- Không tạo policy công khai mặc định. Backend dùng service-role key ở server.
-- Không bao giờ đặt service-role key trong HTML/frontend.
