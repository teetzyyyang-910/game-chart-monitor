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
    return f"🎮 每週遊戲排行榜週報 — {datetime.now().strftime('%Y/%m/%d')}"


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



def build_email_html(appstore_data: dict, gplay_data: dict, report_url: str = "") -> str:
    """
    Email 摘要版：所有地區 Top 3 + 完整報告連結
    """
    now_str = datetime.now().strftime("%Y/%m/%d")
    from collections import OrderedDict

    groups = OrderedDict()
    for r in REGIONS:
        g = r.get("group", "其他")
        groups.setdefault(g, []).append(r)

    GROUP_COLORS = {
        "東南亞": "#0369a1",
        "東北亞": "#7c3aed",
        "美洲":   "#b45309",
        "歐洲":   "#065f46",
        "亞洲":   "#9f1239",
    }

    # 收集所有變化（用於摘要標題）
    total_new = 0
    total_up  = 0
    total_dn  = 0

    body = ""
    for group_name, group_regions in groups.items():
        color = GROUP_COLORS.get(group_name, "#374151")
        body += f'''<tr><td colspan="5" style="padding:14px 8px 4px;font-weight:700;font-size:13px;color:{color};letter-spacing:.5px;border-bottom:2px solid {color}">{group_name}</td></tr>'''

        for region in group_regions:
            as_c = region["appstore"]
            gp_c = region["gplay"]
            flag_name = region["name"]

            # 取 Top 3
            as_free  = appstore_data.get(as_c, {}).get("top-free", [])[:3]
            gp_free  = gplay_data.get(gp_c, {}).get("topselling_free", [])[:3]
            as_paid  = appstore_data.get(as_c, {}).get("top-paid", [])[:3]
            gp_gross = gplay_data.get(gp_c, {}).get("topselling_grossing", [])[:3]

            def fmt_top3(apps):
                items = []
                for a in apps:
                    name = a.get("name", "")[:18]
                    chg  = a.get("rank_change")
                    if chg is None:
                        badge = '<span style="color:#888;font-size:9px">NEW</span> '
                        total_new  # just reference
                    elif chg >= 3:
                        badge = f'<span style="color:#16a34a;font-size:9px">▲{chg}</span> '
                    elif chg <= -3:
                        badge = f'<span style="color:#dc2626;font-size:9px">▼{abs(chg)}</span> '
                    else:
                        badge = ""
                    items.append(f"{badge}{name}")
                return "<br>".join(f'<span style="font-size:11px;color:#374151">#{i+1} {t}</span>' for i, t in enumerate(items)) if items else '<span style="color:#ccc;font-size:11px">—</span>'

            body += f'''
            <tr style="border-bottom:1px solid #f0f0f0">
              <td style="padding:8px;font-size:13px;white-space:nowrap;vertical-align:top">{flag_name}</td>
              <td style="padding:8px;vertical-align:top">
                <div style="font-size:10px;color:#6366f1;font-weight:600;margin-bottom:3px">🍎 免費</div>
                {fmt_top3(as_free)}
              </td>
              <td style="padding:8px;vertical-align:top">
                <div style="font-size:10px;color:#6366f1;font-weight:600;margin-bottom:3px">🍎 付費</div>
                {fmt_top3(as_paid)}
              </td>
              <td style="padding:8px;vertical-align:top">
                <div style="font-size:10px;color:#16a34a;font-weight:600;margin-bottom:3px">🤖 免費</div>
                {fmt_top3(gp_free)}
              </td>
              <td style="padding:8px;vertical-align:top">
                <div style="font-size:10px;color:#16a34a;font-weight:600;margin-bottom:3px">🤖 暢銷</div>
                {fmt_top3(gp_gross)}
              </td>
            </tr>'''

    link_section = ""
    if report_url:
        link_section = f'''
        <div style="text-align:center;margin:20px 0">
          <a href="{report_url}" style="display:inline-block;background:linear-gradient(135deg,#1a73e8,#0d47a1);color:white;text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;font-size:14px">
            📊 查看完整互動報告 →
          </a>
          <p style="color:#aaa;font-size:11px;margin-top:8px">點擊後可用下拉選單切換地區，查看完整 Top 15 排行榜</p>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:900px;margin:0 auto;padding:16px">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1a73e8,#0d47a1);color:white;border-radius:12px;padding:20px 24px;margin-bottom:16px;text-align:center">
    <h1 style="margin:0;font-size:20px">🎮 雙平台遊戲排行榜趨勢 🐑</h1>
    <p style="margin:4px 0 0;opacity:.8;font-size:12px">資料日期：{now_str} ｜ 各地區 Top 3 摘要</p>
  </div>

  <!-- 摘要表格 -->
  <div style="background:white;border-radius:10px;overflow:hidden;border:1px solid #e5e7eb;margin-bottom:16px">
    <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse">
      <thead>
        <tr style="background:#f8fafc">
          <th style="padding:10px 8px;text-align:left;font-size:12px;color:#6b7280;font-weight:600;width:80px">地區</th>
          <th style="padding:10px 8px;text-align:left;font-size:12px;color:#6366f1;font-weight:600">🍎 App Store 免費</th>
          <th style="padding:10px 8px;text-align:left;font-size:12px;color:#6366f1;font-weight:600">🍎 App Store 付費</th>
          <th style="padding:10px 8px;text-align:left;font-size:12px;color:#16a34a;font-weight:600">🤖 Google Play 免費</th>
          <th style="padding:10px 8px;text-align:left;font-size:12px;color:#16a34a;font-weight:600">🤖 Google Play 暢銷</th>
        </tr>
      </thead>
      <tbody>
        {body}
      </tbody>
    </table>
  </div>

  <!-- 完整報告連結 -->
  {link_section}

  <div style="text-align:center;color:#aaa;font-size:11px;padding:8px 0">
    ▲3↑ 上升3名以上 ｜ ▼3↓ 下降3名以上 ｜ NEW 本週新進榜
  </div>
</div>
</body>
</html>"""


def build_subject() -> str:
    return f"🎮 每週遊戲排行榜週報 — {datetime.now().strftime('%Y/%m/%d')}"


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


def build_email_html(appstore_data: dict, gplay_data: dict) -> str:
    """靜態 HTML，適合 Email 客戶端（無 JavaScript）"""
    now_str = datetime.now().strftime("%Y/%m/%d")

    # 依洲分組
    from collections import OrderedDict
    groups = OrderedDict()
    for r in REGIONS:
        g = r.get("group", "其他")
        groups.setdefault(g, []).append(r)

    body = ""
    for group_name in GROUP_ORDER:
        if group_name not in groups:
            continue
        body += '<h2 style="font-size:15px;margin:24px 0 10px;padding:6px 14px;background:#f1f5f9;border-left:4px solid #4285f4;border-radius:4px;color:#334155">{}</h2>'.format(group_name)
        for region in groups[group_name]:
            body += _static_region_block(region, appstore_data, gplay_data)

    return """<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:1100px;margin:0 auto;padding:20px">
  <div style="background:linear-gradient(135deg,#1a73e8,#0d47a1);color:white;border-radius:12px;padding:24px 28px;margin-bottom:24px;text-align:center">
    <h1 style="margin:0;font-size:22px">🎮 雙平台遊戲排行榜趨勢 🐑</h1>
    <p style="margin:6px 0 0;opacity:.8;font-size:13px">資料日期：{now} ｜ 涵蓋東南亞、東北亞、美洲、歐洲、亞洲共 10 個市場</p>
  </div>
  {body}
  <div style="text-align:center;color:#aaa;font-size:12px;padding:16px 0">
    此報告由自動化系統產生 · 每週一、週五早上 10:00 寄出 · 資料來源：App Store / Google Play
  </div>
</div>
</body>
</html>""".format(now=now_str, body=body)
