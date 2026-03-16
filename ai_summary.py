"""
用 Gemini API 分析遊戲排名變動原因
"""
import os
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def summarize_rank_changes(notable_games: list) -> str:
    if not GEMINI_API_KEY:
        return ""
    if not notable_games:
        return ""

    games_info = []
    for g in notable_games:
        change_str = "新進榜" if g.get("rank_change") is None else f"排名變動 {'+' if g['rank_change'] > 0 else ''}{g['rank_change']}"
        notes = g.get("release_notes", "")
        if notes and len(notes) > 200:
            notes = notes[:200] + "..."
        games_info.append({
            "遊戲名稱":  g["name"],
            "平台":      "App Store" if g["platform"] == "appstore" else "Google Play",
            "地區":      g["country"].upper(),
            "當前排名":  f"#{g['rank']}",
            "排名狀況":  change_str,
            "版本":      g.get("version", ""),
            "更新日期":  g.get("release_date", ""),
            "版更內容":  notes or "（無版更資訊）",
        })

    prompt = f"""你是一位擁有 30 年經驗的資深遊戲產品經理，深耕全球手遊市場，精通 App Store 與 Google Play 的排行榜運作機制，善於從版本更新內容推斷玩家行為與市場反應。

以下是近期排行榜出現顯著變動的遊戲清單（包含新進榜或排名大幅移動的遊戲），請以你的專業角度，結合版更資訊，用繁體中文分析每款遊戲排名變動的可能原因。

遊戲清單：
{json.dumps(games_info, ensure_ascii=False, indent=2)}

分析要求：
- 優先根據版更內容推斷原因（例如：限定活動、新角色、賽季更新、聯名合作、重大系統改版等）
- 若無版更資訊，則根據遊戲類型、地區市場特性與排名走勢進行合理推測
- 語氣專業精煉，每款遊戲一行
- 格式：• **遊戲名稱**（地區/平台）：分析原因
- 每行不超過 70 字，最多列出 8 款遊戲
- 若有多個可能原因，以最主要的為主，用「；」連接次要原因
- 直接輸出分析結果，不要自我介紹、不要開場白、不要總結語"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        resp = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 2500}},
            timeout=30,
        )
        data = resp.json()
        if "error" in data:
            print(f"  Gemini API error: {data['error'].get('message','')}")
            return ""
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"  AI 摘要失敗: {e}")
        return ""
