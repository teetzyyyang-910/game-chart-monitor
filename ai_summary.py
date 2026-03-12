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
        if notes and len(notes) > 500:
            notes = notes[:500] + "..."
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

    prompt = f"""以下是本週排行榜有顯著變動的遊戲清單（新進榜或排名大幅移動），請根據版更資訊，用繁體中文簡短分析每款遊戲排名變動的可能原因。

遊戲清單：
{json.dumps(games_info, ensure_ascii=False, indent=2)}

請用以下格式回覆，每款遊戲一行：
• **遊戲名稱**（地區/平台）：一句話說明排名變動原因

注意：
- 如果有版更內容，請根據版更說明推測原因（例如：新角色、限定活動、大型更新等）
- 如果沒有版更資訊，請根據遊戲類型和排名狀況推測
- 每行不超過 60 字
- 最多列出 8 款遊戲"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        resp = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
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
