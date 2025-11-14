import random


media_sources = {
    "cna": {"MandName": "中央社",
            "url": ""},
    "tvbs": {"MandName": "TVBS新聞",
             "url": ""},
    "udn": {"MandName": "聯合新聞網",
            "url": ""}
}

SCRAPER_SETTINGS = {
    "cna": {
        "base_url": "https://www.cna.com.tw/list/aall.aspx",
        "K": 25,
        "T": 0.1
    },
    "udn": {
        "base_url": "https://udn.com/api/more",
        "K": 2,
        "T": 0.1
    }
}

# 常用 User-Agent 列表 
USER_AGENT_LIST = [
    # ------------------ 桌面端 (Desktop) ------------------
    # 1. Windows 10 - 最新版 Chrome (高使用率)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # 2. macOS - 最新版 Safari (macOS/iOS 裝置專用)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    
    # 3. Windows 10 - Firefox (非 Chromium 核心)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",

    # 4. Windows 10 - Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    
    # ------------------ 行動裝置 (Mobile) ------------------
    # 5. iOS - iPhone (常用)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    
    # 6. Android - Chrome on Pixel (常用)
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    
    # 7. iPad (平板裝置)
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    
    # ------------------ 較舊或機器人 (Less Common/Bot) ------------------
    # 8. 舊版 Chrome (有時用來測試網站是否封鎖新版)
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    
    # 9. Google 搜尋引擎爬蟲 (Googlebot)
    # **注意:** 除非您確定目標網站允許爬蟲，否則不建議頻繁使用 Bot UA。
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]


REFERER_LIST = [
        "https://www.google.com/",
        "https://tw.search.yahoo.com/"
    ]


def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENT_LIST),
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": random.choice(USER_AGENT_LIST)
    }