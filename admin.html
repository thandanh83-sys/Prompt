<!DOCTYPE html>
<html lang="vi" class="light" translate="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    
    <meta name="theme-color" content="#f8f7fc">
    <title>Quản trị - Trợ lý AI</title>
    
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23ec4899'/%3E%3Cstop offset='100%25' stop-color='%233b82f6'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='100' height='100' rx='20' fill='url(%23g)'/%3E%3Ctext x='50' y='72' font-size='60' font-family='Arial,sans-serif' font-weight='bold' fill='white' text-anchor='middle'%3EP%3C/text%3E%3C/svg%3E">

    <script>
        if ('scrollRestoration' in history) { history.scrollRestoration = 'manual'; }
        window.scrollTo(0, 0);

        let savedTheme = null;
        try { savedTheme = window.localStorage.getItem('theme'); } catch (error) { }
        const useDarkTheme = savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.classList.toggle('dark', useDarkTheme);
        document.documentElement.classList.toggle('light', !useDarkTheme);
        
        if (useDarkTheme) {
            const metaTheme = document.querySelector('meta[name="theme-color"]');
            if (metaTheme) metaTheme.setAttribute('content', '#0b1120');
        }
    </script>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>

    <style>
        html { background-color: #f8f7fc; transition: background-color .15s ease; min-height: 100vh; min-height: 100dvh; scroll-behavior: smooth; }
        html.dark { background-color: #0b1120 !important; }
        body { -webkit-tap-highlight-color: transparent; overflow-x: hidden; background-color: transparent !important; overscroll-behavior-y: none; min-height: 100vh; min-height: 100dvh; padding-top: env(safe-area-inset-top, 0px); display: flex; flex-direction: column; }
        
        /* BACKGROUND ĐA LỚP CHO TRANG ADMIN */
        .admin-bg { position: fixed; inset: 0; z-index: -3; pointer-events: none; background-color: #f8f7fc; }
        html.dark .admin-bg { background-color: #0b1120; }
        
        .admin-glow-1 { position: fixed; top: 5%; left: 10%; width: 500px; height: 500px; background: rgba(236, 72, 153, 0.15); filter: blur(120px); z-index: -2; border-radius: 50%; pointer-events: none; }
        .admin-glow-2 { position: fixed; bottom: 10%; right: 10%; width: 500px; height: 500px; background: rgba(59, 130, 246, 0.15); filter: blur(120px); z-index: -2; border-radius: 50%; pointer-events: none; }
        .admin-glow-3 { position: fixed; top: 40%; left: 40%; width: 400px; height: 400px; background: rgba(168, 85, 247, 0.1); filter: blur(100px); z-index: -2; border-radius: 50%; pointer-events: none; }

        .app-header { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); border-color: rgba(0,0,0,.06); transition: all .2s; }
        .dark .app-header { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border-color: rgba(255,255,255,.1); }
        
        .brand-text { 
            background: linear-gradient(100deg, #ec4899, #a052c8 52%, #3979f5); 
            -webkit-background-clip: text; 
            background-clip: text; 
            color: transparent; 
            line-height: 1.2;
        }
        
        /* CSS MENU CHUẨN + OVERLAY */
        .menu-dropdown { 
            transition: opacity 0.2s ease-out, transform 0.2s ease-out; 
            transform-origin: top left; 
            will-change: opacity, transform; 
            width: min(280px, calc(100vw - 32px)); 
            max-height: calc(100dvh - 100px); 
            overflow-y: auto; 
            box-sizing: border-box; 
            z-index: 9999 !important; 
        }
        .menu-overlay { 
            position: fixed; inset: 0; background: rgba(0,0,0,.5); backdrop-filter: blur(4px); 
            z-index: 40; opacity: 0; pointer-events: none; transition: all .2s ease; 
        }
        .menu-overlay.active { opacity: 1; pointer-events: auto; }

        /* HIỆU ỨNG KÍNH MỜ (GLASSMORPHISM) CHO DASHBOARD */
        .glass-panel {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
            transition: all 0.3s ease;
        }
        .dark .glass-panel {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }

        /* STAT CARDS (THẺ THỐNG KÊ) */
        .stat-card { 
            background: linear-gradient(135deg, rgba(255,255,255,1) 0%, rgba(248,250,252,1) 100%); 
            border: 1px solid rgba(0,0,0,0.05); 
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .dark .stat-card { 
            background: linear-gradient(135deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.9) 100%); 
            border: 1px solid rgba(51,65,85,0.6); 
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        }
        .dark .stat-card:hover {
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
            border-color: rgba(59,130,246,0.3);
        }

        /* VIÊN THUỐC (PILL) CHO BẢNG */
        .error-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
            margin: 2px;
        }
        .clean-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        /* TABS */
        .tab-btn { transition: all 0.2s; border-bottom: 2px solid transparent; position: relative; }
        .tab-btn.active { color: #ec4899; border-bottom-color: #ec4899; }
        .dark .tab-btn.active { color: #3b82f6; border-bottom-color: #3b82f6; }
        .tab-btn.active::after {
            content: ''; position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px;
            background: currentColor; box-shadow: 0 0 10px currentColor;
        }
    </style>
</head>

<body class="antialiased font-sans relative text-slate-800 dark:text-slate-200">
    <div class="admin-bg"></div>
    <div class="admin-glow-1 hidden md:block"></div>
    <div class="admin-glow-2 hidden md:block"></div>
    <div class="admin-glow-3 hidden md:block"></div>

    <div id="menuOverlay" class="menu-overlay"></div>

    <header class="app-header fixed top-0 left-0 w-full z-50 border-b pt-[env(safe-area-inset-top,0px)]">
        <div class="w-full max-w-7xl mx-auto px-3 sm:px-6 h-16 md:h-20 grid grid-cols-3 items-center">
            
            <div class="flex items-center justify-start relative z-50">
                <button id="btnHamburger" class="w-10 h-10 shrink-0 flex items-center justify-center rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Mở menu">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
                </button>
                
                <div id="dropdownMenu" class="menu-dropdown absolute top-12 md:top-14 left-0 bg-white/95 dark:bg-[#1e293b]/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-2xl shadow-2xl hidden opacity-0 scale-95 z-50 p-2">
                    <div class="flex flex-col gap-1">
                        <a href="./index.html" class="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/50 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-colors" title="Về trang chủ">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-pink-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                            Trang chủ
                        </a>
                        <a href="./landing.html" class="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/50 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-colors" title="Đi đến trang Đánh giá">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-blue-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
                            Đánh giá
                        </a>
                        <a href="./library.html" class="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/50 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-colors" title="Đi đến Thư viện">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-purple-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                            Thư viện
                        </a>
                        <a href="./profile.html" class="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/50 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-colors" title="Đi đến Trang cá nhân">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-slate-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                            Trang cá nhân
                        </a>
                        
                        <div class="h-px bg-slate-100 dark:bg-slate-700/50 my-1 mx-2"></div>
                        
                        <button id="themeToggleMenu" class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/50 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-colors text-left" title="Chuyển đổi chế độ Sáng/Tối">
                            <span id="themeIconMenu" class="w-5 h-5 flex items-center justify-center shrink-0">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" class="w-5 h-5 text-blue-400"><path fill="currentColor" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                            </span>
                            <span id="themeTextMenu">Chế độ Tối</span>
                        </button>

                        <div id="adminMenuDivider" class="h-px bg-slate-100 dark:bg-slate-700/50 my-1 mx-2"></div>
                        <a id="menuBtnAdmin" href="./admin.html" class="flex items-center gap-3 px-3 py-3 rounded-xl bg-green-50 dark:bg-green-900/20 text-sm font-semibold text-green-600 dark:text-green-400 transition-colors" title="Trang Quản trị viên">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                            Quản trị viên
                        </a>
                    </div>
                </div>
            </div>

            <div class="flex items-center justify-center z-40">
                <a href="./index.html" class="flex items-center gap-1.5 min-w-0 no-underline focus:outline-none" title="Trợ lý AI - Trang chủ">
                    <svg class="w-5 h-5 sm:w-7 sm:h-7 shrink-0" viewBox="0 0 24 24"><defs><linearGradient id="brandSparkGradient" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ec4899"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient></defs><path fill="url(#brandSparkGradient)" d="M12 2L14.7 9.3 22 12l-7.3 2.7L12 22l-2.7-7.3L2 12l7.3-2.7L12 2Z"/></svg>
                    <span class="brand-text text-[15px] sm:text-lg font-extrabold truncate">Trợ lý AI</span>
                </a>
            </div>
            
            <div class="flex items-center justify-end z-50">
                <div class="w-10"></div>
            </div>
        </div>
    </header>

    <main class="w-full max-w-5xl mx-auto px-4 sm:px-6 pt-32 md:pt-40 pb-32 flex-grow flex flex-col items-center justify-center relative z-10">
        
        <div id="adminAccessNotice" class="glass-panel rounded-3xl p-6 max-w-lg w-full text-center" style="display:none;">
            <h2 class="text-xl font-extrabold text-slate-800 dark:text-white mb-3">Không thể truy cập khu vực quản trị</h2>
            <p id="adminAccessMessage" class="text-sm text-slate-600 dark:text-slate-300 mb-5">Máy chủ chưa xác nhận quyền truy cập.</p>
            <a href="./index.html" class="inline-flex items-center justify-center px-5 py-2.5 rounded-xl font-semibold text-white bg-gradient-to-r from-pink-500 to-blue-500 hover:scale-105 transition-transform">Về trang chủ</a>
        </div>
        
        <div id="adminLoginBox" class="glass-panel rounded-[2rem] p-8 md:p-10 max-w-md w-full text-center relative overflow-hidden z-10">
            <div class="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-gradient-to-r from-pink-500 to-blue-500 rounded-b-full opacity-80"></div>
            
            <div class="w-20 h-20 mx-auto mb-6 rounded-2xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 group hover:scale-105 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="w-full h-full"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ec4899"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient></defs><rect width="100" height="100" fill="url(#g)"/><text x="50" y="72" font-size="60" font-family="Arial,sans-serif" font-weight="bold" fill="white" text-anchor="middle">P</text></svg>
            </div>
            
            <h3 class="font-extrabold text-3xl mb-2 text-slate-800 dark:text-white tracking-tight">Đăng nhập Admin</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400 mb-8">Hệ thống quản trị nội bộ - Trợ lý AI</p>
            
            <div class="relative w-full mb-6">
                <input type="password" id="adminPassword" class="w-full p-4 pl-5 pr-12 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-300 dark:border-slate-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400 text-sm font-medium transition-all" placeholder="Nhập mật khẩu...">
                <button type="button" id="toggleAdminPassword" class="absolute inset-y-0 right-0 pr-4 flex items-center text-xl text-slate-400 hover:text-pink-500 transition-colors cursor-pointer" title="Hiện/Ẩn mật khẩu">🐵</button>
            </div>
            
            <p id="adminError" class="text-red-500 text-xs font-bold mb-4 bg-red-50 dark:bg-red-900/20 p-2 rounded-lg" style="display: none;">Sai mật khẩu hoặc lỗi kết nối.</p>
            
            <button id="btnAdminLogin" class="w-full py-4 rounded-2xl font-bold text-white bg-gradient-to-r from-pink-500 to-blue-500 shadow-[0_0_20px_rgba(236,72,153,0.3)] hover:shadow-[0_0_30px_rgba(59,130,246,0.5)] hover:scale-[1.02] active:scale-95 transition-all text-sm flex items-center justify-center gap-2">
                Đăng nhập ngay
            </button>
            
            <div class="mt-8 text-xs text-slate-400 dark:text-slate-500">
                © 2026 Trợ lý AI. Bảo mật nội bộ.
            </div>
        </div>

        <!-- DASHBOARD -->
        <div id="adminDashboard" class="w-full mt-6 relative z-10" style="display: none;">
            
            <!-- TABS -->
            <div class="flex justify-between items-center mb-6 bg-white/50 dark:bg-slate-800/40 backdrop-blur-md rounded-2xl px-4 pt-2 border border-white/20 dark:border-slate-700/50 shadow-sm">
                <div class="flex gap-6">
                    <button id="tabBtnOverview" class="tab-btn active pb-3 text-sm md:text-base font-bold text-slate-500 dark:text-slate-400 hover:text-pink-500 dark:hover:text-blue-400" onclick="switchTab('overview')">📊 Tổng quan</button>
                    <button id="tabBtnIpLogs" class="tab-btn pb-3 text-sm md:text-base font-bold text-slate-500 dark:text-slate-400 hover:text-pink-500 dark:hover:text-blue-400" onclick="switchTab('iplogs')">🌐 Lịch sử IP</button>
                </div>
                <button id="btnAdminLogout" class="px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600 hover:bg-red-50 hover:text-red-600 hover:border-red-200 dark:hover:bg-red-900/30 dark:hover:border-red-800 transition mb-2">Đăng xuất</button>
            </div>

            <div id="tabContentOverview" class="space-y-6">
                <!-- STAT CARDS -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="stat-card rounded-3xl p-5 flex flex-col justify-center items-center text-center relative overflow-hidden group">
                        <div class="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center mb-2"><span class="text-xl">📝</span></div>
                        <p class="text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 relative z-10">Lượt đánh giá</p>
                        <p id="statTotal" class="text-4xl font-extrabold text-blue-500 relative z-10">0</p>
                    </div>
                    <div class="stat-card rounded-3xl p-5 flex flex-col justify-center items-center text-center relative overflow-hidden group">
                        <div class="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="w-10 h-10 rounded-full bg-pink-100 dark:bg-pink-900/50 flex items-center justify-center mb-2"><span class="text-xl">⭐</span></div>
                        <p class="text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 relative z-10">Điểm TB</p>
                        <p id="statAvg" class="text-4xl font-extrabold text-pink-500 relative z-10">0.0</p>
                    </div>
                    <div class="stat-card rounded-3xl p-5 flex flex-col justify-center items-center text-center relative overflow-hidden group">
                        <div class="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center mb-2"><span class="text-xl">✨</span></div>
                        <p class="text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 relative z-10">Prompt Sạch</p>
                        <p id="statClean" class="text-4xl font-extrabold text-green-500 relative z-10">0%</p>
                    </div>
                </div>

                <!-- CHARTS -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="glass-panel rounded-3xl p-5 relative overflow-hidden">
                        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500"></div>
                        <p class="text-xs font-bold text-slate-600 dark:text-slate-300 mb-4 uppercase tracking-widest text-center">Top Lỗi Phổ Biến</p>
                        <div class="h-56 w-full flex justify-center"><canvas id="errorChart"></canvas></div>
                    </div>
                    <div class="glass-panel rounded-3xl p-5 relative overflow-hidden">
                        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-cyan-500 to-green-500"></div>
                        <p class="text-xs font-bold text-slate-600 dark:text-slate-300 mb-4 uppercase tracking-widest text-center">Phân Bố Điểm Số</p>
                        <div class="h-56 w-full flex justify-center"><canvas id="scoreChart"></canvas></div>
                    </div>
                </div>

                <!-- HISTORY TABLE -->
                <div class="glass-panel rounded-3xl overflow-hidden">
                    <div class="px-6 py-5 border-b border-white/20 dark:border-slate-700/50 flex justify-between items-center bg-white/30 dark:bg-slate-800/30">
                        <p class="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2"><span>🕒</span> Lịch sử gần đây</p>
                        <!-- NÚT XÓA TẤT CẢ -->
                        <button onclick="deleteAllPrompts()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-500 hover:text-white dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-500 dark:hover:text-white transition-all text-xs font-bold border border-red-200 dark:border-red-800/50">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                            Xóa tất cả
                        </button>
                    </div>
                    <div class="overflow-x-auto max-h-[500px] overflow-y-auto custom-scrollbar">
                        <table class="w-full text-sm text-left relative">
                            <thead class="text-[10px] text-slate-500 uppercase bg-slate-100/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-10 border-b border-slate-200 dark:border-slate-700/50">
                                <tr>
                                    <th class="px-5 py-4 font-bold tracking-wider">Thời gian</th>
                                    <th class="px-5 py-4 font-bold tracking-wider">Prompt</th>
                                    <th class="px-5 py-4 font-bold tracking-wider text-center">Điểm</th>
                                    <th class="px-5 py-4 font-bold tracking-wider">Mã lỗi</th>
                                </tr>
                            </thead>
                            <tbody id="adminHistoryList" class="divide-y divide-slate-100 dark:divide-slate-800/50">
                                <tr><td colspan="4" class="text-center py-10 text-slate-500">Đang tải dữ liệu...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB IP LOGS -->
            <div id="tabContentIpLogs" class="space-y-5" style="display: none;">
                <div class="glass-panel rounded-3xl overflow-hidden">
                    <div class="px-6 py-5 border-b border-white/20 dark:border-slate-700/50 flex justify-between items-center bg-white/30 dark:bg-slate-800/30">
                        <p class="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2"><span>🌐</span> Danh sách IP Đăng nhập</p>
                    </div>
                    <div class="overflow-x-auto max-h-[500px] overflow-y-auto custom-scrollbar">
                        <table class="w-full text-sm text-left relative">
                            <thead class="text-[10px] text-slate-500 uppercase bg-slate-100/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-10 border-b border-slate-200 dark:border-slate-700/50">
                                <tr>
                                    <th class="px-5 py-4 font-bold tracking-wider">Thời gian</th>
                                    <th class="px-5 py-4 font-bold tracking-wider">Địa chỉ IP</th>
                                    <th class="px-5 py-4 font-bold tracking-wider">Thiết bị / Trình duyệt</th>
                                </tr>
                            </thead>
                            <tbody id="ipLogsList" class="divide-y divide-slate-100 dark:divide-slate-800/50">
                                <tr><td colspan="3" class="text-center py-10 text-slate-500">Đang tải dữ liệu...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="border-t border-slate-200 dark:border-white/10 py-8 text-center text-slate-500 text-sm relative z-10 mt-auto">
        <p>© 2026 Trợ lý AI - Nghiên cứu AI & Tư duy.</p>
    </footer>

    <script>
        const API_URL = "https://prompt-tx2e.onrender.com";
        const $ = id => document.getElementById(id);
        const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

        let adminToken = null;
        let chart1 = null, chart2 = null;

        const moonSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" class="w-5 h-5 text-blue-400"><defs><linearGradient id="moonGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#60a5fa" /><stop offset="100%" stop-color="#3b82f6" /></linearGradient></defs><path fill="url(#moonGrad)" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
        const sunSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" class="w-5 h-5 text-yellow-500"><defs><linearGradient id="sunGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#fef08a" /><stop offset="100%" stop-color="#f59e0b" /></linearGradient></defs><circle cx="12" cy="12" r="5" fill="url(#sunGrad)"></circle><path stroke="url(#sunGrad)" stroke-width="2" stroke-linecap="round" d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path></svg>`;

        // 1. MENU LOGIC
        const hamburger = $('btnHamburger');
        const dropdown = $('dropdownMenu');
        const overlay = $('menuOverlay');
        
        if (hamburger && dropdown) {
            hamburger.addEventListener('click', (e) => {
                e.stopPropagation();
                const isHidden = dropdown.classList.contains('hidden');
                if (isHidden) {
                    dropdown.classList.remove('hidden');
                    if (overlay) overlay.classList.add('active');
                    requestAnimationFrame(() => {
                        dropdown.classList.remove('opacity-0', 'scale-95');
                        dropdown.classList.add('opacity-100', 'scale-100');
                    });
                } else {
                    dropdown.classList.remove('opacity-100', 'scale-100');
                    dropdown.classList.add('opacity-0', 'scale-95');
                    if (overlay) overlay.classList.remove('active');
                    setTimeout(() => { if (dropdown.classList.contains('opacity-0')) dropdown.classList.add('hidden'); }, 200);
                }
            });
            
            if (overlay) {
                overlay.addEventListener('click', () => {
                    dropdown.classList.remove('opacity-100', 'scale-100');
                    dropdown.classList.add('opacity-0', 'scale-95');
                    overlay.classList.remove('active');
                    setTimeout(() => { if (dropdown.classList.contains('opacity-0')) dropdown.classList.add('hidden'); }, 200);
                });
            }

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && !hamburger.contains(e.target) && !dropdown.classList.contains('hidden')) {
                    dropdown.classList.remove('opacity-100', 'scale-100');
                    dropdown.classList.add('opacity-0', 'scale-95');
                    if (overlay) overlay.classList.remove('active');
                    setTimeout(() => { if (dropdown.classList.contains('opacity-0')) dropdown.classList.add('hidden'); }, 200);
                }
            });
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !dropdown.classList.contains('hidden')) {
                    dropdown.classList.remove('opacity-100', 'scale-100');
                    dropdown.classList.add('opacity-0', 'scale-95');
                    if (overlay) overlay.classList.remove('active');
                    setTimeout(() => { if (dropdown.classList.contains('opacity-0')) dropdown.classList.add('hidden'); }, 200);
                }
            });
        }

        // 2. THEME LOGIC
        function applyTheme(dark) {
            document.documentElement.classList.toggle('dark', dark); document.documentElement.classList.toggle('light', !dark);
            if($('themeIconMenu')) $('themeIconMenu').innerHTML = dark ? sunSVG : moonSVG; 
            if($('themeTextMenu')) $('themeTextMenu').textContent = dark ? 'Chế độ Sáng' : 'Chế độ Tối';
            try { window.localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (error) { }
            const themeColor = document.querySelector('meta[name="theme-color"]'); 
            if (themeColor) themeColor.setAttribute('content', dark ? '#0b1120' : '#f8f7fc');
            if (chart1 || chart2) updateChartsTheme(dark);
        }
        applyTheme(document.documentElement.classList.contains('dark'));
        if($('themeToggleMenu')) {
            $('themeToggleMenu').addEventListener('click', (e) => { 
                e.preventDefault(); e.stopPropagation(); 
                applyTheme(!document.documentElement.classList.contains('dark')); 
            });
        }

        // 3. ADMIN LOGIC
        async function checkAdminAccess() {
            const showAccessNotice = message => {
                $('adminLoginBox').style.display = 'none';
                $('adminDashboard').style.display = 'none';
                $('adminAccessMessage').textContent = message;
                $('adminAccessNotice').style.display = 'block';
            };
            try {
                const res = await fetch(`${API_URL}/check_admin_ip`);
                if (res.ok) {
                    $('adminMenuDivider').style.display = 'block';
                    $('menuBtnAdmin').style.display = 'flex';
                    return;
                }
                showAccessNotice(res.status === 403 ? 'Địa chỉ IP hiện tại chưa được cấp quyền quản trị.' : `Máy chủ chưa xác nhận được quyền truy cập (HTTP ${res.status}).`);
            } catch {
                showAccessNotice('Không kết nối được máy chủ để xác minh quyền quản trị. Vui lòng thử lại sau.');
            }
        }
        checkAdminAccess();

        window.switchTab = function(tabName) {
            const btnOverview = $('tabBtnOverview'), btnIpLogs = $('tabBtnIpLogs');
            const contentOverview = $('tabContentOverview'), contentIpLogs = $('tabContentIpLogs');
            if (tabName === 'overview') {
                btnOverview.classList.add('active'); btnIpLogs.classList.remove('active');
                contentOverview.style.display = 'block'; contentIpLogs.style.display = 'none';
            } else {
                btnIpLogs.classList.add('active'); btnOverview.classList.remove('active');
                contentIpLogs.style.display = 'block'; contentOverview.style.display = 'none';
                fetchIpLogs();
            }
        };

        $('toggleAdminPassword').addEventListener('click', function() {
            const input = $('adminPassword');
            if (input.type === 'password') { input.type = 'text'; this.innerText = '🙈'; } else { input.type = 'password'; this.innerText = '🐵'; }
        });

        async function handleLogin() {
            const pwd = $('adminPassword').value.trim(); if (!pwd) return;
            const btn = $('btnAdminLogin'); btn.disabled = true; btn.innerHTML = 'Đang kiểm tra...';
            try {
                const response = await fetch(`${API_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pwd }) });
                const data = await response.json();
                if (response.ok && data.token) {
                    adminToken = data.token;
                    sessionStorage.setItem('adminToken', adminToken);
                    $('adminLoginBox').style.display = 'none'; $('adminDashboard').style.display = 'block';
                    switchTab('overview'); fetchHistory();
                } else {
                    $('adminError').style.display = 'block'; $('adminError').textContent = data.detail || "Sai mật khẩu.";
                    btn.disabled = false; btn.innerHTML = 'Đăng nhập ngay';
                }
            } catch {
                $('adminError').style.display = 'block'; $('adminError').textContent = "Lỗi kết nối Server.";
                btn.disabled = false; btn.innerHTML = 'Đăng nhập ngay';
            }
        }
        $('btnAdminLogin').addEventListener('click', handleLogin);
        $('adminPassword').addEventListener('keypress', (e) => { if (e.key === 'Enter') { e.preventDefault(); handleLogin(); } });

        $('btnAdminLogout').addEventListener('click', () => {
            adminToken = null; sessionStorage.removeItem('adminToken');
            $('adminLoginBox').style.display = 'block'; $('adminDashboard').style.display = 'none';
            $('adminPassword').value = ''; $('adminError').style.display = 'none';
            $('btnAdminLogin').disabled = false; $('btnAdminLogin').innerHTML = 'Đăng nhập ngay';
            if (chart1) { chart1.destroy(); chart1 = null; } if (chart2) { chart2.destroy(); chart2 = null; }
        });

        function updateChartsTheme(isDark) {
            const textColor = isDark ? '#94a3b8' : '#64748b';
            [chart1, chart2].forEach(c => {
                if (!c) return;
                const legendLabels = c.options?.plugins?.legend?.labels;
                if (legendLabels) legendLabels.color = textColor;
                if (c.options?.scales?.x?.ticks) c.options.scales.x.ticks.color = textColor;
                if (c.options?.scales?.y?.ticks) c.options.scales.y.ticks.color = textColor;
                c.update();
            });
        }

        // HÀM XÓA TẤT CẢ PROMPT
        window.deleteAllPrompts = async function() {
            if (!confirm("CẢNH BÁO: Bạn có chắc chắn muốn xóa TOÀN BỘ lịch sử đánh giá? Hành động này sẽ xóa sạch dữ liệu trên Supabase và không thể hoàn tác!")) return;
            try {
                const res = await fetch(`${API_URL}/admin/delete_all_prompts`, { 
                    method: 'DELETE', 
                    headers: { 'X-Admin-Token': adminToken } 
                });
                if (res.ok) {
                    alert("Đã xóa toàn bộ dữ liệu thành công!");
                    fetchHistory(); // Tải lại bảng
                } else {
                    const err = await res.json();
                    alert("Lỗi khi xóa: " + (err.error || "Không xác định"));
                }
            } catch { alert("Lỗi kết nối!"); }
        };

        async function fetchHistory() {
            const tbody = $('adminHistoryList');
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-10 text-slate-500 text-xs">Đang tải dữ liệu...</td></tr>';
            try {
                const response = await fetch(`${API_URL}/history`, { method: 'GET', headers: { 'X-Admin-Token': adminToken } });
                const data = await response.json();
                if (!response.ok || !data.history) { tbody.innerHTML = '<tr><td colspan="4" class="text-center py-10 text-red-500 text-xs">Lỗi tải dữ liệu.</td></tr>'; return; }

                tbody.replaceChildren();
                let totalScore = 0, cleanCount = 0;
                const errorCounts = {};
                const scoreDist = { '0-3': 0, '4-6': 0, '7-8': 0, '9-10': 0 };

                data.history.forEach(item => {
                    totalScore += item.total_score;
                    if (!item.errors || item.errors.length === 0) cleanCount++;
                    (item.errors || []).forEach(e => { errorCounts[e.code] = (errorCounts[e.code] || 0) + 1; });
                    const s = item.total_score;
                    if (s <= 3) scoreDist['0-3']++; else if (s <= 6) scoreDist['4-6']++; else if (s <= 8) scoreDist['7-8']++; else scoreDist['9-10']++;
                });

                const n = data.history.length;
                if (n > 0) {
                    $('statTotal').textContent = n;
                    $('statAvg').textContent = (totalScore / n).toFixed(1);
                    $('statClean').textContent = `${Math.round((cleanCount / n) * 100)}%`;
                } else {
                    $('statTotal').textContent = '0'; $('statAvg').textContent = '0.0'; $('statClean').textContent = '0%';
                }

                if (n === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-10 text-slate-500 text-xs">Chưa có dữ liệu.</td></tr>';
                } else {
                    data.history.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.className = 'hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors group';
                        const errBadges = (item.errors || []).map(e =>
                            `<span class="error-pill">${escapeHtml(e.code)}</span>`
                        ).join('') || '<span class="clean-pill">Sạch</span>';
                        tr.innerHTML = `
                            <td class="px-5 py-3 text-[11px] text-slate-500 whitespace-nowrap font-medium">${new Date(item.created_at).toLocaleString('vi-VN')}</td>
                            <td class="px-5 py-3 max-w-xs"><div class="line-clamp-2 text-[12px] text-slate-700 dark:text-slate-300 font-medium">${escapeHtml(item.prompt)}</div></td>
                            <td class="px-5 py-3 text-center"><span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-pink-50 dark:bg-pink-900/20 font-bold text-pink-500 text-sm shadow-sm">${item.total_score}</span></td>
                            <td class="px-5 py-3 max-w-[150px]">${errBadges}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }

                if (chart1) chart1.destroy();
                const ERROR_NAMES = { "A01": "Lỗi chính tả", "A02": "Thiếu dấu câu", "A03": "Lặp lại", "B01": "Thiếu cấu trúc", "B02": "Mục không logic", "B03": "Sai phân cấp", "B04": "Chưa định dạng", "C01": "Đối tượng chưa rõ", "C02": "Thiếu bối cảnh", "C03": "Chung chung", "C04": "Thiếu ví dụ", "D01": "Mâu thuẫn", "D02": "Bất khả thi", "D03": "Vai trò sai", "E01": "Trộn lĩnh vực", "E02": "Thuật ngữ lộn xộn", "E03": "Thiếu đặc thù" };
                const errLabels = Object.keys(errorCounts).length ? Object.keys(errorCounts).map(c => ERROR_NAMES[c] || c) : ['Không có lỗi'];
                const errData = Object.keys(errorCounts).length ? Object.values(errorCounts) : [1];
                const palette = ['#ec4899','#3b82f6','#22c55e','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#84cc16','#f97316','#6366f1'];
                
                chart1 = new Chart($('errorChart').getContext('2d'), {
                    type: 'doughnut',
                    data: { labels: errLabels, datasets: [{ data: errData, backgroundColor: palette, borderWidth: 0, hoverOffset: 4 }] },
                    options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom', labels: { color: document.documentElement.classList.contains('dark') ? '#94a3b8' : '#64748b', font: { size: 10, family: 'sans-serif' }, boxWidth: 8, usePointStyle: true, padding: 15 } } } }
                });

                if (chart2) chart2.destroy();
                chart2 = new Chart($('scoreChart').getContext('2d'), {
                    type: 'bar',
                    data: { labels: ['0-3', '4-6', '7-8', '9-10'], datasets: [{ label: 'Số prompt', data: [scoreDist['0-3'], scoreDist['4-6'], scoreDist['7-8'], scoreDist['9-10']], backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#22c55e'], borderRadius: 8, borderSkipped: false, barPercentage: 0.6 }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: document.documentElement.classList.contains('dark') ? '#94a3b8' : '#64748b', font: { size: 11, family: 'sans-serif', weight: 'bold' } }, grid: { display: false } }, y: { beginAtZero: true, ticks: { color: document.documentElement.classList.contains('dark') ? '#94a3b8' : '#64748b', font: { size: 10 }, precision: 0 }, grid: { color: document.documentElement.classList.contains('dark') ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)', drawBorder: false } } } }
                });
            } catch (e) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center py-10 text-red-500 text-xs">Lỗi kết nối Server.</td></tr>';
            }
        }

        async function fetchIpLogs() {
            const tbody = $('ipLogsList');
            tbody.innerHTML = '<tr><td colspan="3" class="text-center py-10 text-slate-500 text-xs">Đang tải...</td></tr>';
            try {
                const res = await fetch(`${API_URL}/admin/ip_logs`, { headers: { 'X-Admin-Token': adminToken } });
                const data = await res.json();
                if (!res.ok || !data.logs) { tbody.innerHTML = '<tr><td colspan="3" class="text-center py-10 text-red-500 text-xs">Lỗi tải dữ liệu IP.</td></tr>'; return; }
                if (data.logs.length === 0) { tbody.innerHTML = '<tr><td colspan="3" class="text-center py-10 text-slate-500 text-xs">Chưa có log nào.</td></tr>'; return; }
                tbody.replaceChildren();
                data.logs.forEach(log => {
                    const tr = document.createElement('tr');
                    tr.className = 'hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors';
                    tr.innerHTML = `
                        <td class="px-5 py-3 text-[11px] text-slate-500 whitespace-nowrap font-medium">${new Date(log.login_time || log.created_at || log.timestamp).toLocaleString('vi-VN')}</td>
                        <td class="px-5 py-3 text-[12px] font-mono text-slate-700 dark:text-slate-300">${escapeHtml(log.ip_address || log.ip || '—')}</td>
                        <td class="px-5 py-3 text-[12px] text-slate-600 dark:text-slate-400">${escapeHtml(log.user_agent || '—')}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center py-10 text-red-500 text-xs">Lỗi kết nối Server.</td></tr>';
            }
        }

        (async function autoRestore() {
            const t = sessionStorage.getItem('adminToken');
            if (!t) return;
            try {
                const response = await fetch(`${API_URL}/history`, { method: 'GET', headers: { 'X-Admin-Token': t } });
                const data = await response.json();
                if (!response.ok || !Array.isArray(data.history)) throw new Error('Phiên Admin không hợp lệ.');
                adminToken = t;
                $('adminLoginBox').style.display = 'none';
                $('adminDashboard').style.display = 'block';
                switchTab('overview');
                await fetchHistory();
            } catch {
                adminToken = null;
                sessionStorage.removeItem('adminToken');
                $('adminLoginBox').style.display = 'block';
                $('adminDashboard').style.display = 'none';
            }
        })();
    </script>
</body>
</html>
