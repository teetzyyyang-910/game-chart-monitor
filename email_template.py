"""
產生帶下拉選單的 HTML 週報
"""
from datetime import datetime
import json
from config import REGIONS

APPSTORE_CHARTS = {
    "top-free": "免費遊戲榜",
    "top-paid": "付費遊戲榜",
}
GPLAY_CHARTS = {
    "topselling_free":     "免費遊戲榜",
    "topselling_grossing": "暢銷遊戲榜",
}


def _region_data_js(appstore_data: dict, gplay_data: dict) -> str:
    regions_js = {}
    for region in REGIONS:
        as_c = region["appstore"]
        gp_c = region["gplay"]
        key  = as_c

        as_charts = {ck: appstore_data.get(as_c, {}).get(ck, []) for ck in APPSTORE_CHARTS}
        gp_charts = {ck: gplay_data.get(gp_c, {}).get(ck, []) for ck in GPLAY_CHARTS}
        regions_js[key] = {"appstore": as_charts, "gplay": gp_charts}

    return json.dumps(regions_js, ensure_ascii=False)


def build_html(appstore_data: dict, gplay_data: dict) -> str:
    now_str    = datetime.now().strftime("%Y/%m/%d")
    regions_js = _region_data_js(appstore_data, gplay_data)

    # 按 group 分組產生 optgroup
    from collections import OrderedDict
    groups = OrderedDict()
    for r in REGIONS:
        g = r.get("group", "其他")
        groups.setdefault(g, []).append(r)
    
    options_parts = []
    for group_name, group_regions in groups.items():
        options_parts.append(f'<optgroup label="{group_name}">')
        for r in group_regions:
            options_parts.append(f'<option value="{r["appstore"]}">{r["name"]}</option>')
        options_parts.append('</optgroup>')
    options = "\n".join(options_parts)

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>🎮 遊戲排行榜週報 {now_str}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .header {{ background: linear-gradient(135deg,#1a73e8,#0d47a1); color: white; padding: 24px 32px; text-align: center; }}
    .header h1 {{ font-size: 22px; margin-bottom: 6px; }}
    .header p {{ opacity: .8; font-size: 13px; }}
    .controls {{ background: white; padding: 14px 32px; border-bottom: 1px solid #e0e0e0;
                 display: flex; align-items: center; justify-content: center; gap: 16px; position: sticky; top: 0; z-index: 9999;
                 box-shadow: 0 4px 12px rgba(0,0,0,.12); }}
    .controls label {{ font-weight: 600; font-size: 14px; color: #333; white-space: nowrap; }}
    select {{ padding: 8px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;
              background: white; cursor: pointer; outline: none; min-width: 180px; }}
    select:focus {{ border-color: #1a73e8; box-shadow: 0 0 0 3px rgba(26,115,232,.15); }}
    .content {{ max-width: 1300px; margin: 24px auto; padding: 0 20px 40px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 6px rgba(0,0,0,.08); }}
    .card-header {{ padding: 13px 16px; font-weight: 700; font-size: 15px;
                    display: flex; align-items: center; gap: 8px; }}
    .as-header {{ background: #eef2ff; color: #3730a3; border-bottom: 2px solid #c7d2fe; }}
    .gp-header {{ background: #f0fdf4; color: #15803d; border-bottom: 2px solid #bbf7d0; }}
    .chart-section {{ padding: 0; }}
    .chart-title {{ font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase;
                    letter-spacing: .8px; padding: 10px 14px 6px; background: #fafafa;
                    border-bottom: 1px solid #f0f0f0; border-top: 1px solid #f0f0f0; margin-top: 2px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    thead tr {{ background: #f8f9fa; }}
    th {{ padding: 7px 10px; color: #666; font-size: 11px; font-weight: 600;
          text-align: left; border-bottom: 1px solid #eee; white-space: nowrap; }}
    th:first-child, th:last-child {{ text-align: center; }}
    .rank-cell {{ width: 52px; min-width: 52px; text-align: center; white-space: nowrap; padding: 8px 10px; }}
    .footer {{ text-align: center; color: #bbb; font-size: 12px; padding: 20px; }}
  </style>
</head>
<body>

<div class="header">
  <h1>🎮 雙平台遊戲排行榜趨勢 🐑</h1>
  <p>資料日期：{now_str} ｜ 涵蓋東南亞、東北亞、美洲、歐洲、亞洲共 10 個市場</p>
</div>

<div class="controls">
  <label>🌏 選擇地區：</label>
  <select id="regionSelect" onchange="switchRegion(this.value)" style="font-size:15px;padding:8px 16px;border:1px solid #ddd;border-radius:8px;background:white;cursor:pointer;outline:none;min-width:200px;font-family:inherit">
    {options}
  </select>

</div>

<div class="content">
  <div id="regionContent"></div>
</div>

<div class="footer">此報告由自動化系統產生 · 每週一早上自動寄出 · 資料來源：App Store / Google Play</div>

<script>
const ALL_DATA = {regions_js};

const AS_CHARTS = {{"top-free":"🆓 免費遊戲榜","top-paid":"💰 付費遊戲榜"}};
const GP_CHARTS = {{"topselling_free":"🆓 免費遊戲榜","topselling_grossing":"💰 暢銷遊戲榜"}};
const MEDAL = {{1:"🥇",2:"🥈",3:"🥉"}};

function rankBadge(change) {{
  if (change === null || change === undefined)
    return `<span style="font-size:10px;color:#aaa;background:#f5f5f5;border-radius:4px;padding:1px 5px">NEW</span>`;
  if (change > 0)
    return `<span style="font-size:10px;color:#16a34a;background:#dcfce7;border-radius:4px;padding:1px 5px;white-space:nowrap">▲${{change}}</span>`;
  if (change < 0)
    return `<span style="font-size:10px;color:#dc2626;background:#fee2e2;border-radius:4px;padding:1px 5px;white-space:nowrap">▼${{Math.abs(change)}}</span>`;
  return `<span style="font-size:10px;color:#9ca3af;background:#f3f4f6;border-radius:4px;padding:1px 5px">—</span>`;
}}

function renderRows(apps) {{
  if (!apps || apps.length === 0)
    return `<tr><td colspan="5" style="padding:20px;text-align:center;color:#ccc;font-size:13px">（無資料）</td></tr>`;
  return apps.map(a => {{
    const bg = a.rank<=3 ? "#fffbf0" : (a.rank%2===0 ? "white" : "#fafafa");
    const medal = MEDAL[a.rank] || `<span style="color:#bbb;font-size:12px">#${{a.rank}}</span>`;
    const icon = a.icon
      ? `<img src="${{a.icon}}" width="36" height="36" style="border-radius:8px;vertical-align:middle">`
      : `<span style="display:inline-block;width:36px;height:36px;border-radius:8px;background:#eee"></span>`;
    const dev = a.developer ? `<div style="color:#999;font-size:11px;margin-top:1px">${{a.developer}}</div>` : "";
    const score = (a.score && a.score > 0) ? `<span style="color:#f59e0b;font-size:11px">⭐${{a.score}}</span>` : "";
    const change = (a.rank_change !== undefined) ? rankBadge(a.rank_change) : "";
    return `<tr style="background:${{bg}};border-bottom:1px solid #f5f5f5">
      <td style="padding:8px 10px;text-align:center;width:52px;min-width:52px;white-space:nowrap;font-size:15px">${{medal}}</td>
      <td style="padding:8px 6px;width:48px">${{icon}}</td>
      <td style="padding:8px 10px">
        <a href="${{a.url}}" target="_blank" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-size:13px">${{a.name}}</a>
        ${{dev}}
      </td>
      <td style="padding:8px 6px;text-align:center;width:44px">${{score}}</td>
      <td style="padding:8px 6px;text-align:center;width:52px">${{change}}</td>
    </tr>`;
  }}).join("");
}}

function renderTable(apps) {{
  return `<table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse">
    <thead><tr style="background:#f8f9fa">
      <th style="width:52px;min-width:52px;text-align:center;padding:7px 8px;color:#666;font-size:12px;white-space:nowrap">名次</th>
      <th style="width:48px"></th>
      <th style="text-align:left;padding:7px 8px;color:#666;font-size:12px">遊戲名稱</th>
      <th style="padding:7px 8px;width:44px;color:#666;font-size:12px;text-align:center">評分</th>
      <th style="padding:7px 8px;width:52px;color:#666;font-size:12px;text-align:center">變化</th>
    </tr></thead>
    <tbody>${{renderRows(apps)}}</tbody>
  </table>`;
}}


function switchRegion(key) {{
  const data = ALL_DATA[key] || {{}};
  const label = document.querySelector(`#regionSelect option[value="${{key}}"]`).text;

  let asHtml = "", gpHtml = "";
  for (const [ck, cl] of Object.entries(AS_CHARTS)) {{
    asHtml += `<div class="chart-title">${{cl}}</div>${{renderTable((data.appstore||{{}})[ck]||[])}}`;
  }}
  for (const [ck, cl] of Object.entries(GP_CHARTS)) {{
    gpHtml += `<div class="chart-title">${{cl}}</div>${{renderTable((data.gplay||{{}})[ck]||[])}}`;
  }}

  document.getElementById("regionContent").innerHTML = `
    <div class="grid">
      <div class="card">
        <div class="card-header as-header">🍎 App Store</div>
        <div class="chart-section">${{asHtml}}</div>
      </div>
      <div class="card">
        <div class="card-header gp-header">🤖 Google Play</div>
        <div class="chart-section">${{gpHtml}}</div>
      </div>
    </div>`;
}}

switchRegion(document.getElementById("regionSelect").value);
</script>
</body>
</html>"""


def build_subject() -> str:
    return f"🎮 {datetime.now().strftime('%Y/%m/%d')} — 雙平台遊戲排行榜趨勢"


# ─────────────────────────────────────────────────────────────
# 靜態 Email 版本（無 JS，適合 Outlook / Gmail 等郵件客戶端）
# ─────────────────────────────────────────────────────────────

AS_CHARTS_STATIC = {
    "top-free": "🆓 免費遊戲榜",
    "top-paid": "💰 付費遊戲榜",
}
GP_CHARTS_STATIC = {
    "topselling_free":     "🆓 免費遊戲榜",
    "topselling_grossing": "💰 暢銷遊戲榜",
}

MEDAL_STATIC = {1: "🥇", 2: "🥈", 3: "🥉"}

GROUP_ORDER = ["東南亞", "東北亞", "美洲", "歐洲", "亞洲"]


def _rank_badge(change):
    if change is None:
        return '<span style="font-size:10px;color:#888;background:#f0f0f0;padding:1px 5px;border-radius:3px">NEW</span>'
    if change > 0:
        return '<span style="font-size:10px;color:#16a34a;background:#dcfce7;padding:1px 5px;border-radius:3px">▲{}</span>'.format(change)
    if change < 0:
        return '<span style="font-size:10px;color:#dc2626;background:#fee2e2;padding:1px 5px;border-radius:3px">▼{}</span>'.format(abs(change))
    return '<span style="font-size:10px;color:#999;background:#f3f4f6;padding:1px 5px;border-radius:3px">—</span>'


def _static_table(apps, show_score=False):
    if not apps:
        return '<p style="color:#aaa;font-size:13px;padding:8px 0">（無資料）</p>'
    rows = ""
    for a in apps:
        rank   = a.get("rank", 0)
        medal  = MEDAL_STATIC.get(rank, '<span style="color:#999;font-size:12px">#{}</span>'.format(rank))
        icon   = '<img src="{}" width="32" height="32" style="border-radius:6px;vertical-align:middle;margin-right:6px">'.format(a["icon"]) if a.get("icon") else ''
        name   = '<a href="{}" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-size:13px">{}</a>'.format(a.get("url","#"), a.get("name",""))
        dev    = '<div style="color:#999;font-size:11px">{}</div>'.format(a.get("developer","")) if a.get("developer") else ""
        score  = '<span style="color:#f59e0b;font-size:11px">⭐{}</span>'.format(a["score"]) if show_score and a.get("score") else ""
        change = _rank_badge(a.get("rank_change")) if "rank_change" in a else ""
        bg     = "#fffbf0" if rank <= 3 else ("white" if rank % 2 == 0 else "#fafafa")
        rows += """<tr style="background:{bg};border-bottom:1px solid #f0f0f0">
          <td style="padding:7px 8px;text-align:center;width:36px">{medal}</td>
          <td style="padding:7px 4px;width:40px">{icon}</td>
          <td style="padding:7px 8px">{name}{dev}</td>
          <td style="padding:7px 6px;text-align:center;width:42px">{score}</td>
          <td style="padding:7px 6px;text-align:center;width:48px">{change}</td>
        </tr>""".format(bg=bg, medal=medal, icon=icon, name=name, dev=dev, score=score, change=change)

    return """<table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-size:13px">
      <thead><tr style="background:#f8f9fa">
        <th style="padding:6px 8px;width:36px;text-align:center;color:#666;font-size:11px">名次</th>
        <th style="width:40px"></th>
        <th style="text-align:left;padding:6px 8px;color:#666;font-size:11px">遊戲名稱</th>
        <th style="padding:6px 6px;width:42px;text-align:center;color:#666;font-size:11px">評分</th>
        <th style="padding:6px 6px;width:48px;text-align:center;color:#666;font-size:11px">變化</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""".format(rows=rows)


def _static_region_block(region, appstore_data, gplay_data):
    as_c = region["appstore"]
    gp_c = region["gplay"]
    name = region["name"]

    as_content = ""
    for ck, cl in AS_CHARTS_STATIC.items():
        apps = appstore_data.get(as_c, {}).get(ck, [])
        as_content += '<div style="font-size:11px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px 4px;background:#fafafa;border-top:1px solid #eee">{}</div>{}'.format(cl, _static_table(apps))

    gp_content = ""
    for ck, cl in GP_CHARTS_STATIC.items():
        apps = gplay_data.get(gp_c, {}).get(ck, [])
        gp_content += '<div style="font-size:11px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px 4px;background:#fafafa;border-top:1px solid #eee">{}</div>{}'.format(cl, _static_table(apps, show_score=True))

    return """<div style="margin-bottom:28px">
      <h2 style="font-size:16px;margin:0 0 10px;padding:10px 14px;background:linear-gradient(135deg,#4285f4,#34a853);color:white;border-radius:8px">{name}</h2>
      <table width="100%" cellspacing="0" cellpadding="0"><tr valign="top">
        <td width="50%" style="padding-right:10px">
          <div style="background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
            <div style="padding:10px 12px;background:#eef2ff;color:#3730a3;font-weight:700;font-size:14px">🍎 App Store</div>
            {as_content}
          </div>
        </td>
        <td width="50%" style="padding-left:10px">
          <div style="background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
            <div style="padding:10px 12px;background:#f0fdf4;color:#15803d;font-weight:700;font-size:14px">🤖 Google Play</div>
            {gp_content}
          </div>
        </td>
      </tr></table>
    </div>""".format(name=name, as_content=as_content, gp_content=gp_content)



def build_email_html(appstore_data: dict, gplay_data: dict, report_url: str = "", ai_summary: str = "") -> str:
    """
    Email 版：5個重點地區 Top 5 + 排名變動摘要文字 + 完整報告連結
    """
    now_str = datetime.now().strftime("%Y/%m/%d")

    FOCUS = [
        {"code": "tw", "name": "🇹🇼 台灣"},
        {"code": "us", "name": "🇺🇸 美國"},
        {"code": "kr", "name": "🇰🇷 韓國"},
        {"code": "gb", "name": "🇬🇧 英國"},
        {"code": "sg", "name": "🇸🇬 新加坡"},
    ]
    TOP = 5
    MEDAL = {1:"🥇",2:"🥈",3:"🥉"}

    def change_badge(change):
        if change is None:
            return '<span style="background:#f0f0f0;color:#888;font-size:10px;padding:1px 5px;border-radius:3px;margin-left:4px">NEW</span>'
        if change >= 1:
            return '<span style="background:#dcfce7;color:#16a34a;font-size:10px;padding:1px 5px;border-radius:3px;margin-left:4px">▲{}</span>'.format(change)
        if change <= -1:
            return '<span style="background:#fee2e2;color:#dc2626;font-size:10px;padding:1px 5px;border-radius:3px;margin-left:4px">▼{}</span>'.format(abs(change))
        return '<span style="background:#f3f4f6;color:#9ca3af;font-size:10px;padding:1px 5px;border-radius:3px;margin-left:4px">—</span>'

    def render_top5(apps):
        if not apps:
            return '<div style="color:#aaa;font-size:12px;padding:4px 0">（無資料）</div>'
        rows = ""
        for a in apps[:TOP]:
            rank   = a.get("rank", 0)
            medal  = MEDAL.get(rank, '<span style="color:#999;font-size:11px;min-width:18px;display:inline-block">#{}</span>'.format(rank))
            name   = a.get("name","")[:20]
            icon   = '<img src="{}" width="24" height="24" style="border-radius:4px;vertical-align:middle;margin:0 5px">'.format(a["icon"]) if a.get("icon") else '<span style="display:inline-block;width:24px;height:24px;margin:0 5px"></span>'
            change = change_badge(a.get("rank_change")) if "rank_change" in a else ""
            rows += '<div style="display:flex;align-items:center;padding:4px 0;border-bottom:1px solid #f5f5f5">' + \
                    '<span style="min-width:22px;text-align:center;font-size:13px">{}</span>'.format(medal) + \
                    icon + \
                    '<a href="{}" style="color:#1d4ed8;text-decoration:none;font-size:12px;font-weight:600;flex:1">{}</a>'.format(a.get("url","#"), name) + \
                    change + '</div>'
        return rows

    # ── 收集排名變動摘要文字 ────────────────────────────
    highlights = []
    for r in FOCUS:
        code = r["code"]
        rname = r["name"]
        for platform, data, charts in [
            ("🍎", appstore_data, [("top-free","免費榜")]),
            ("🤖", gplay_data,   [("topselling_free","免費榜"),("topselling_grossing","暢銷榜")]),
        ]:
            for ck, clabel in charts:
                apps = (data.get(code) or {}).get(ck, [])
                for a in apps[:10]:
                    chg  = a.get("rank_change")
                    name = a.get("name","")[:15]
                    rank = a.get("rank",0)
                    if chg is None and rank <= 5:
                        highlights.append("{} {} {} <b>{}</b> 🆕 新進 #{} {}".format(platform, rname, clabel, name, rank, ""))
                    elif chg is not None and chg >= 5:
                        highlights.append("{} {} {} <b>{}</b> 大幅上升 ▲{} → #{}".format(platform, rname, clabel, name, chg, rank))
                    elif chg is not None and chg <= -5:
                        highlights.append("{} {} {} <b>{}</b> 大幅下滑 ▼{} → #{}".format(platform, rname, clabel, name, abs(chg), rank))

    if highlights:
        highlight_html = '<ul style="margin:8px 0;padding-left:20px">' + \
                         "".join('<li style="margin:4px 0;font-size:13px;color:#374151">{}</li>'.format(h) for h in highlights[:8]) + \
                         '</ul>'
    else:
        highlight_html = '<p style="color:#6b7280;font-size:13px;margin:8px 0">本週排名無顯著變動（±5名以上）</p>'

    # ── 各地區 Top 5 表格 ────────────────────────────────
    regions_html = ""
    for r in FOCUS:
        code  = r["code"]
        rname = r["name"]
        as_free  = render_top5((appstore_data.get(code) or {}).get("top-free", []))
        gp_free  = render_top5((gplay_data.get(code) or {}).get("topselling_free", []))
        gp_gross = render_top5((gplay_data.get(code) or {}).get("topselling_grossing", []))

        regions_html += f"""
        <div style="margin-bottom:20px;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
          <div style="background:linear-gradient(135deg,#4285f4,#34a853);color:white;padding:8px 14px;font-weight:700;font-size:14px">{rname}</div>
          <table width="100%" cellspacing="0" cellpadding="0"><tr valign="top">
            <td width="33%" style="padding:10px;border-right:1px solid #f0f0f0">
              <div style="font-size:11px;font-weight:700;color:#6366f1;margin-bottom:6px">🍎 App Store 免費</div>
              {as_free}
            </td>
            <td width="33%" style="padding:10px;border-right:1px solid #f0f0f0">
              <div style="font-size:11px;font-weight:700;color:#16a34a;margin-bottom:6px">🤖 Google Play 免費</div>
              {gp_free}
            </td>
            <td width="33%" style="padding:10px">
              <div style="font-size:11px;font-weight:700;color:#dc2626;margin-bottom:6px">🤖 Google Play 暢銷</div>
              {gp_gross}
            </td>
          </tr></table>
        </div>"""

    # ── 完整報告連結 ─────────────────────────────────────
    link_html = ""
    if report_url:
        link_html = f'<div style="margin-top:12px"><a href="{report_url}" style="display:inline-block;background:rgba(255,255,255,0.2);color:white;text-decoration:none;padding:8px 24px;border-radius:20px;font-size:13px;font-weight:600;border:1px solid rgba(255,255,255,0.5)">📊 查看完整地區報告</a></div>'

    # AI 摘要區塊
    if ai_summary:
        import re
        lines = ai_summary.strip().split("\n")
        items = ""
        for line in lines:
            line = line.strip()
            if line.startswith("•") or line.startswith("-"):
                line = line.lstrip("•-").strip()
                line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                items += f'<li style="margin:5px 0;font-size:13px;color:#374151">{line}</li>'
        ai_summary_html = f'''<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 16px;margin-bottom:16px">
  <div style="font-weight:700;font-size:14px;color:#92400e;margin-bottom:8px">🤖 AI 分析：排名變動原因</div>
  <ul style="margin:0;padding-left:16px">{items}</ul>
  <div style="font-size:10px;color:#aaa;margin-top:6px">由 Gemini AI 根據版更資訊自動分析</div>
</div>'''
    else:
        ai_summary_html = ""

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:800px;margin:0 auto;padding:16px">

  <div style="background:linear-gradient(135deg,#1a73e8,#0d47a1);color:white;border-radius:12px;padding:20px 24px;margin-bottom:16px;text-align:center">
    <h1 style="margin:0;font-size:20px">🎮 雙平台遊戲排行榜趨勢 🐑</h1>
    <p style="margin:4px 0 0;opacity:.8;font-size:12px">資料日期：{now_str} ｜ 重點地區 Top 5</p>
    {link_html}
  </div>

  <!-- 排名變動摘要 -->
  <div style="background:white;border-radius:10px;padding:14px 16px;margin-bottom:16px;border:1px solid #e5e7eb">
    <div style="font-weight:700;font-size:14px;color:#1f2937;margin-bottom:4px">📈 本週排名變動摘要</div>
    {highlight_html}
    <div style="font-size:10px;color:#aaa;margin-top:6px">▲▼ 5名以上變動 ｜ NEW 本週新進 Top 5</div>
  </div>
  {ai_summary_html}

  <!-- 重點地區 Top 5 -->
  {regions_html}

  <div style="text-align:center;color:#aaa;font-size:11px;padding:8px 0">
    每週一、週五早上 10:00 自動寄出 · 資料來源：App Store / Google Play
  </div>
</div>
</body>
</html>"""


def build_subject() -> str:
    return f"🎮 {datetime.now().strftime('%Y/%m/%d')} — 雙平台遊戲排行榜趨勢"


# ─────────────────────────────────────────────────────────────
# 靜態 Email 版本（無 JS，適合 Outlook / Gmail 等郵件客戶端）
# ─────────────────────────────────────────────────────────────

AS_CHARTS_STATIC = {
    "top-free": "🆓 免費遊戲榜",
    "top-paid": "💰 付費遊戲榜",
}
GP_CHARTS_STATIC = {
    "topselling_free":     "🆓 免費遊戲榜",
    "topselling_grossing": "💰 暢銷遊戲榜",
}

MEDAL_STATIC = {1: "🥇", 2: "🥈", 3: "🥉"}

GROUP_ORDER = ["東南亞", "東北亞", "美洲", "歐洲", "亞洲"]


def _rank_badge(change):
    if change is None:
        return '<span style="font-size:10px;color:#888;background:#f0f0f0;padding:1px 5px;border-radius:3px">NEW</span>'
    if change > 0:
        return '<span style="font-size:10px;color:#16a34a;background:#dcfce7;padding:1px 5px;border-radius:3px">▲{}</span>'.format(change)
    if change < 0:
        return '<span style="font-size:10px;color:#dc2626;background:#fee2e2;padding:1px 5px;border-radius:3px">▼{}</span>'.format(abs(change))
    return '<span style="font-size:10px;color:#999;background:#f3f4f6;padding:1px 5px;border-radius:3px">—</span>'


def _static_table(apps, show_score=False):
    if not apps:
        return '<p style="color:#aaa;font-size:13px;padding:8px 0">（無資料）</p>'
    rows = ""
    for a in apps:
        rank   = a.get("rank", 0)
        medal  = MEDAL_STATIC.get(rank, '<span style="color:#999;font-size:12px">#{}</span>'.format(rank))
        icon   = '<img src="{}" width="32" height="32" style="border-radius:6px;vertical-align:middle;margin-right:6px">'.format(a["icon"]) if a.get("icon") else ''
        name   = '<a href="{}" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-size:13px">{}</a>'.format(a.get("url","#"), a.get("name",""))
        dev    = '<div style="color:#999;font-size:11px">{}</div>'.format(a.get("developer","")) if a.get("developer") else ""
        score  = '<span style="color:#f59e0b;font-size:11px">⭐{}</span>'.format(a["score"]) if show_score and a.get("score") else ""
        change = _rank_badge(a.get("rank_change")) if "rank_change" in a else ""
        bg     = "#fffbf0" if rank <= 3 else ("white" if rank % 2 == 0 else "#fafafa")
        rows += """<tr style="background:{bg};border-bottom:1px solid #f0f0f0">
          <td style="padding:7px 8px;text-align:center;width:36px">{medal}</td>
          <td style="padding:7px 4px;width:40px">{icon}</td>
          <td style="padding:7px 8px">{name}{dev}</td>
          <td style="padding:7px 6px;text-align:center;width:42px">{score}</td>
          <td style="padding:7px 6px;text-align:center;width:48px">{change}</td>
        </tr>""".format(bg=bg, medal=medal, icon=icon, name=name, dev=dev, score=score, change=change)

    return """<table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-size:13px">
      <thead><tr style="background:#f8f9fa">
        <th style="padding:6px 8px;width:36px;text-align:center;color:#666;font-size:11px">名次</th>
        <th style="width:40px"></th>
        <th style="text-align:left;padding:6px 8px;color:#666;font-size:11px">遊戲名稱</th>
        <th style="padding:6px 6px;width:42px;text-align:center;color:#666;font-size:11px">評分</th>
        <th style="padding:6px 6px;width:48px;text-align:center;color:#666;font-size:11px">變化</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""".format(rows=rows)


def _static_region_block(region, appstore_data, gplay_data):
    as_c = region["appstore"]
    gp_c = region["gplay"]
    name = region["name"]

    as_content = ""
    for ck, cl in AS_CHARTS_STATIC.items():
        apps = appstore_data.get(as_c, {}).get(ck, [])
        as_content += '<div style="font-size:11px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px 4px;background:#fafafa;border-top:1px solid #eee">{}</div>{}'.format(cl, _static_table(apps))

    gp_content = ""
    for ck, cl in GP_CHARTS_STATIC.items():
        apps = gplay_data.get(gp_c, {}).get(ck, [])
        gp_content += '<div style="font-size:11px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px 4px;background:#fafafa;border-top:1px solid #eee">{}</div>{}'.format(cl, _static_table(apps, show_score=True))

    return """<div style="margin-bottom:28px">
      <h2 style="font-size:16px;margin:0 0 10px;padding:10px 14px;background:linear-gradient(135deg,#4285f4,#34a853);color:white;border-radius:8px">{name}</h2>
      <table width="100%" cellspacing="0" cellpadding="0"><tr valign="top">
        <td width="50%" style="padding-right:10px">
          <div style="background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
            <div style="padding:10px 12px;background:#eef2ff;color:#3730a3;font-weight:700;font-size:14px">🍎 App Store</div>
            {as_content}
          </div>
        </td>
        <td width="50%" style="padding-left:10px">
          <div style="background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
            <div style="padding:10px 12px;background:#f0fdf4;color:#15803d;font-weight:700;font-size:14px">🤖 Google Play</div>
            {gp_content}
          </div>
        </td>
      </tr></table>
    </div>""".format(name=name, as_content=as_content, gp_content=gp_content)



def build_subject() -> str:
    return f"🎮 {datetime.now().strftime('%Y/%m/%d')} — 雙平台遊戲排行榜趨勢"


# ─────────────────────────────────────────────────────────────
# 靜態 Email 版本（無 JS，適合 Outlook / Gmail 等郵件客戶端）
# ─────────────────────────────────────────────────────────────

AS_CHARTS_STATIC = {
    "top-free": "🆓 免費遊戲榜",
    "top-paid": "💰 付費遊戲榜",
}
GP_CHARTS_STATIC = {
    "topselling_free":     "🆓 免費遊戲榜",
    "topselling_grossing": "💰 暢銷遊戲榜",
}

MEDAL_STATIC = {1: "🥇", 2: "🥈", 3: "🥉"}

GROUP_ORDER = ["東南亞", "東北亞", "美洲", "歐洲", "亞洲"]


def _rank_badge(change):
    if change is None:
        return '<span style="font-size:10px;color:#888;background:#f0f0f0;padding:1px 5px;border-radius:3px">NEW</span>'
    if change > 0:
        return '<span style="font-size:10px;color:#16a34a;background:#dcfce7;padding:1px 5px;border-radius:3px">▲{}</span>'.format(change)
    if change < 0:
        return '<span style="font-size:10px;color:#dc2626;background:#fee2e2;padding:1px 5px;border-radius:3px">▼{}</span>'.format(abs(change))
    return '<span style="font-size:10px;color:#999;background:#f3f4f6;padding:1px 5px;border-radius:3px">—</span>'


def _static_table(apps, show_score=False):
    if not apps:
        return '<p style="color:#aaa;font-size:13px;padding:8px 0">（無資料）</p>'
    rows = ""
    for a in apps:
        rank   = a.get("rank", 0)
        medal  = MEDAL_STATIC.get(rank, '<span style="color:#999;font-size:12px">#{}</span>'.format(rank))
        icon   = '<img src="{}" width="32" height="32" style="border-radius:6px;vertical-align:middle;margin-right:6px">'.format(a["icon"]) if a.get("icon") else ''
        name   = '<a href="{}" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-size:13px">{}</a>'.format(a.get("url","#"), a.get("name",""))
        dev    = '<div style="color:#999;font-size:11px">{}</div>'.format(a.get("developer","")) if a.get("developer") else ""
        score  = '<span style="color:#f59e0b;font-size:11px">⭐{}</span>'.format(a["score"]) if show_score and a.get("score") else ""
        change = _rank_badge(a.get("rank_change")) if "rank_change" in a else ""
        bg     = "#fffbf0" if rank <= 3 else ("white" if rank % 2 == 0 else "#fafafa")
        rows += """<tr style="background:{bg};border-bottom:1px solid #f0f0f0">
          <td style="padding:7px 8px;text-align:center;width:36px">{medal}</td>
          <td style="padding:7px 4px;width:40px">{icon}</td>
          <td style="padding:7px 8px">{name}{dev}</td>
          <td style="padding:7px 6px;text-align:center;width:42px">{score}</td>
          <td style="padding:7px 6px;text-align:center;width:48px">{change}</td>
        </tr>""".format(bg=bg, medal=medal, icon=icon, name=name, dev=dev, score=score, change=change)

    return """<table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-size:13px">
      <thead><tr style="background:#f8f9fa">
        <th style="padding:6px 8px;width:36px;text-align:center;color:#666;font-size:11px">名次</th>
        <th style="width:40px"></th>
        <th style="text-align:left;padding:6px 8px;color:#666;font-size:11px">遊戲名稱</th>
        <th style="padding:6px 6px;width:42px;text-align:center;color:#666;font-size:11px">評分</th>
        <th style="padding:6px 6px;width:48px;text-align:center;color:#666;font-size:11px">變化</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""".format(rows=rows)


def _static_region_block(region, appstore_data, gplay_data):
    as_c = region["appstore"]
    gp_c = region["gplay"]
    name = region["name"]

    as_content = ""
    for ck, cl in AS_CHARTS_STATIC.items():
        apps = appstore_data.get(as_c, {}).get(ck, [])
        as_content += '<div style="font-size:11px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px 4px;background:#fafafa;border-top:1px solid #eee">{}</div>{}'.format(cl, _static_table(apps))

    gp_content = ""
    for ck, cl in GP_CHARTS_STATIC.items():
        apps = gplay_data.get(gp_c, {}).get(ck, [])
        gp_content += '<div style="font-size:11px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px 4px;background:#fafafa;border-top:1px solid #eee">{}</div>{}'.format(cl, _static_table(apps, show_score=True))

    return """<div style="margin-bottom:28px">
      <h2 style="font-size:16px;margin:0 0 10px;padding:10px 14px;background:linear-gradient(135deg,#4285f4,#34a853);color:white;border-radius:8px">{name}</h2>
      <table width="100%" cellspacing="0" cellpadding="0"><tr valign="top">
        <td width="50%" style="padding-right:10px">
          <div style="background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
            <div style="padding:10px 12px;background:#eef2ff;color:#3730a3;font-weight:700;font-size:14px">🍎 App Store</div>
            {as_content}
          </div>
        </td>
        <td width="50%" style="padding-left:10px">
          <div style="background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
            <div style="padding:10px 12px;background:#f0fdf4;color:#15803d;font-weight:700;font-size:14px">🤖 Google Play</div>
            {gp_content}
          </div>
        </td>
      </tr></table>
    </div>""".format(name=name, as_content=as_content, gp_content=gp_content)


