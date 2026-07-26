"""从 allure_raw JSON 生成独立 HTML 测试报告（无需 Java / allure CLI）

功能：
- 中文优先级、模块、故事标签
- 真实耗时（从 container 文件读取毫秒级时间戳）
- 失败截图嵌入，点击放大
- 美观专业的 UI
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "reports" / "allure_raw"
HTML_DIR = ROOT / "reports" / "allure_html"
SCREENSHOT_DIR = ROOT / "reports" / "screenshots"

SEVERITY_CN = {
    "blocker": "阻塞",
    "critical": "严重",
    "normal": "一般",
    "minor": "轻微",
    "trivial": "提示",
}

STATUS_ICON = {
    "passed": "✅",
    "failed": "❌",
    "broken": "💥",
    "skipped": "⏭️",
}

STATUS_CN = {
    "passed": "通过",
    "failed": "失败",
    "broken": "异常",
    "skipped": "跳过",
}


def load_json(pattern: str):
    files = sorted(RAW_DIR.glob(pattern))
    return [json.loads(f.read_text(encoding="utf-8")) for f in files]


def build_id_map():
    """构建 result uuid -> (result_data, container_data) 映射"""
    results = {r["uuid"]: r for r in load_json("*-result.json")}
    containers = {}
    for c in load_json("*-container.json"):
        for child_id in c.get("children", []):
            containers[child_id] = c
    return results, containers


def get_duration_ms(container):
    """从 container 计算耗时（毫秒）"""
    start = container.get("start")
    stop = container.get("stop")
    if start and stop:
        return stop - start
    return 0


def collect_screenshots():
    """收集 screenshots 目录中的截图，按时间倒序排列"""
    screenshots = []
    if not SCREENSHOT_DIR.exists():
        return screenshots
    for f in sorted(SCREENSHOT_DIR.glob("*.png"), reverse=True):
        screenshots.append({
            "name": f.name,
            "path": f"../screenshots/{f.name}",
            "size": f.stat().st_size,
        })
    return screenshots


def fmt_duration(ms):
    """格式化耗时"""
    if ms <= 0:
        return "-"
    if ms < 1000:
        return f"{ms}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds / 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"


def build_report():
    results_map, containers = build_id_map()
    all_screenshots = {s["name"]: s for s in collect_screenshots()}

    # 合并 result + container
    merged = []
    for uuid, result in results_map.items():
        container = containers.get(uuid, {})
        merged.append({
            **result,
            "duration_ms": get_duration_ms(container),
            "befores": container.get("befores", []),
            "afters": container.get("afters", []),
        })

    # 排序：按 suite -> name
    merged.sort(key=lambda r: (
        next((l["value"] for l in r.get("labels", []) if l["name"] == "suite"), ""),
        r.get("name", ""),
    ))

    passed = [r for r in merged if r.get("status") == "passed"]
    failed = [r for r in merged if r.get("status") in ("failed", "broken")]
    skipped = [r for r in merged if r.get("status") == "skipped"]
    total = len(merged)
    total_duration = sum(r.get("duration_ms", 0) for r in merged)
    pass_rate = (len(passed) / total * 100) if total else 0

    # ─── 构建表格行 ───────────────────────────────────
    rows = ""
    for idx, r in enumerate(merged):
        status = r.get("status", "unknown")
        name = r.get("name", "Unknown")
        labels = {l["name"]: l["value"] for l in r.get("labels", [])}
        feature = labels.get("feature", "-")
        story = labels.get("story", "-")
        severity = SEVERITY_CN.get(labels.get("severity", ""), labels.get("severity", "-"))
        duration = fmt_duration(r.get("duration_ms", 0))
        status_class = {"passed": "pass", "failed": "fail", "broken": "fail", "skipped": "skip"}.get(status, "")

        # 截图匹配：用 allure testMethod label 精确匹配截图文件名
        test_method = labels.get("testMethod", "")
        related_screenshots = [
            s for name_key, s in all_screenshots.items()
            if test_method and test_method in name_key
        ]
        # 去重
        seen = set()
        unique_ss = []
        for s in related_screenshots:
            if s["name"] not in seen:
                seen.add(s["name"])
                unique_ss.append(s)

        ss_html = ""
        for ss in unique_ss[:2]:
            is_fail = "FAILED" in ss["name"]
            label = "失败截图" if is_fail else "通过截图"
            border_color = "#e74c3c" if is_fail else "#27ae60"
            ss_html += f"""
            <div class="screenshot-thumb" onclick="openLightbox('{ss['path']}')" title="{ss['name']}">
                <img src="{ss['path']}" loading="lazy" style="border-color:{border_color}" />
                <div class="thumb-label" style="color:{border_color}">{label}</div>
            </div>"""

        # Allure 步骤
        steps_html = ""
        for s in r.get("steps", []):
            s_name = s.get("name", "")
            s_status = s.get("status", "passed")
            s_class = "step-pass" if s_status == "passed" else "step-fail"
            steps_html += f'<span class="step {s_class}">{s_name}</span>'

        rows += f"""
        <tr class="{status_class}">
            <td class="center">{idx + 1}</td>
            <td>{name}</td>
            <td>{feature}</td>
            <td>{story}</td>
            <td class="center"><span class="badge severity-{labels.get('severity', '')}">{severity}</span></td>
            <td class="center"><span class="badge status-{status}">{STATUS_CN.get(status, status)}</span></td>
            <td class="right">{duration}</td>
            <td>{ss_html}</td>
        </tr>"""

    # ─── 截图画廊（按用例分组）──────────────────────
    # 将截图按测试方法分组
    screenshot_groups = {}  # test_method -> [screenshots]
    unmatched = []
    for s in all_screenshots.values():
        matched = False
        for r in merged:
            r_labels = {l["name"]: l["value"] for l in r.get("labels", [])}
            test_method = r_labels.get("testMethod", "")
            if test_method and test_method in s["name"]:
                display_name = r.get("name", test_method)
                if display_name not in screenshot_groups:
                    screenshot_groups[display_name] = []
                screenshot_groups[display_name].append(s)
                matched = True
                break
        if not matched:
            unmatched.append(s)

    gallery_html = ""
    for display_name, screenshots in screenshot_groups.items():
        items_html = ""
        for s in screenshots[:3]:  # 每个用例最多3张
            items_html += f"""
            <div class="gallery-item" onclick="openLightbox('{s['path']}')" title="{s['name']}">
                <img src="{s['path']}" loading="lazy" />
                <div class="gallery-label">{s['name'][:50]}</div>
            </div>"""
        gallery_html += f"""
        <div class="gallery-group">
            <div class="gallery-group-title">📋 {display_name}</div>
            <div class="gallery-group-items">{items_html}</div>
        </div>"""

    # 未匹配的截图归到"其他"
    if unmatched:
        items_html = ""
        for s in unmatched:
            items_html += f"""
            <div class="gallery-item" onclick="openLightbox('{s['path']}')" title="{s['name']}">
                <img src="{s['path']}" loading="lazy" />
                <div class="gallery-label">{s['name'][:50]}</div>
            </div>"""
        gallery_html += f"""
        <div class="gallery-group">
            <div class="gallery-group-title">📋 其他截图</div>
            <div class="gallery-group-items">{items_html}</div>
        </div>"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UI 自动化测试报告</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; color: #2c3e50; }}

/* Header */
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #fff; padding: 32px 40px; position: relative; overflow: hidden; }}
.header::after {{ content: ''; position: absolute; top: -50%; right: -10%; width: 400px; height: 400px; background: radial-gradient(circle, rgba(255,255,255,.05) 0%, transparent 70%); border-radius: 50%; }}
.header h1 {{ font-size: 26px; font-weight: 700; letter-spacing: 1px; position: relative; z-index: 1; }}
.header .subtitle {{ font-size: 13px; opacity: .6; margin-top: 8px; position: relative; z-index: 1; }}

/* Summary Cards */
.summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding: 24px 40px; }}
.card {{ background: #fff; border-radius: 14px; padding: 24px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,.06); transition: transform .2s; cursor: default; }}
.card:hover {{ transform: translateY(-2px); }}
.card .num {{ font-size: 36px; font-weight: 800; letter-spacing: -1px; }}
.card .label {{ font-size: 13px; color: #7f8c8d; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }}
.card.total {{ border-left: 4px solid #636e72; }}
.card.pass {{ border-left: 4px solid #27ae60; }}
.card.pass .num {{ color: #27ae60; }}
.card.fail {{ border-left: 4px solid #e74c3c; }}
.card.fail .num {{ color: #e74c3c; }}
.card.rate {{ border-left: 4px solid #2980b9; }}
.card.rate .num {{ color: #2980b9; }}

/* Table */
.table-wrap {{ padding: 0 40px 40px; }}
table {{ width: 100%; background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.06); border-collapse: collapse; }}
th {{ background: #f8f9fc; color: #636e72; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 14px 16px; text-align: center; border-bottom: 2px solid #e9ecef; }}
td {{ padding: 14px 16px; font-size: 14px; border-bottom: 1px solid #f1f3f5; vertical-align: middle; text-align: center; }}
tr:last-child td {{ border-bottom: none; }}
tr.fail {{ background: #fff5f5; }}
tr.skip {{ background: #fafafa; color: #adb5bd; }}
.center {{ text-align: center; }}
.right {{ text-align: right; font-variant-numeric: tabular-nums; }}

/* Badges */
.badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
.status-passed {{ background: #d5f5e3; color: #27ae60; }}
.status-failed {{ background: #fadbd8; color: #e74c3c; }}
.status-broken {{ background: #fdebd0; color: #e67e22; }}
.severity-blocker {{ background: #e74c3c; color: #fff; }}
.severity-critical {{ background: #f39c12; color: #fff; }}
.severity-normal {{ background: #3498db; color: #fff; }}
.severity-minor {{ background: #95a5a6; color: #fff; }}

/* Steps */
.step {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; display: inline-block; }}
.step-pass {{ color: #27ae60; background: #eafaf1; }}
.step-fail {{ color: #e74c3c; background: #fdedec; }}

/* Screenshots */
.screenshot-thumb {{ display: inline-block; cursor: pointer; margin: 2px; }}
.screenshot-thumb img {{ width: 80px; height: 45px; object-fit: cover; border-radius: 6px; border: 1px solid #e9ecef; transition: transform .2s, box-shadow .2s; }}
.screenshot-thumb:hover img {{ transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,.15); }}
.thumb-label {{ font-size: 10px; color: #95a5a6; text-align: center; }}

/* Gallery */
.gallery-title {{ padding: 0 40px 12px; font-size: 16px; font-weight: 600; color: #2c3e50; }}
.gallery {{ padding: 0 40px 40px; }}
.gallery-group {{ margin-bottom: 24px; background: #fff; border-radius: 14px; padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,.04); }}
.gallery-group-title {{ font-size: 14px; font-weight: 600; color: #2c3e50; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f3f5; }}
.gallery-group-items {{ display: flex; flex-wrap: wrap; gap: 12px; }}
.gallery-item {{ cursor: pointer; transition: transform .2s; }}
.gallery-item:hover {{ transform: scale(1.03); }}
.gallery-item img {{ width: 200px; height: 112px; object-fit: cover; border-radius: 10px; border: 2px solid #e9ecef; transition: border-color .2s; }}
.gallery-item:hover img {{ border-color: #6c5ce7; }}
.gallery-label {{ font-size: 11px; color: #7f8c8d; margin-top: 4px; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

/* Lightbox */
.lightbox {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,.9); z-index: 9999; justify-content: center; align-items: center; cursor: zoom-out; }}
.lightbox.show {{ display: flex; }}
.lightbox img {{ max-width: 95%; max-height: 95%; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,.5); }}
.lightbox-close {{ position: fixed; top: 20px; right: 30px; color: #fff; font-size: 36px; cursor: pointer; z-index: 10000; }}

/* Footer */
.footer {{ padding: 24px 40px; text-align: center; font-size: 12px; color: #b2bec3; border-top: 1px solid #eee; }}
</style>
</head>
<body>

<div class="header">
    <h1>🧪 UI 自动化测试报告</h1>
    <div class="subtitle">生成时间: {now} ｜ 项目: GGJX ERP ｜ 总耗时: {fmt_duration(total_duration)}</div>
</div>

<div class="summary">
    <div class="card total"><div class="num">{total}</div><div class="label">总用例数</div></div>
    <div class="card pass"><div class="num">{len(passed)}</div><div class="label">通过</div></div>
    <div class="card fail"><div class="num">{len(failed)}</div><div class="label">失败</div></div>
    <div class="card rate"><div class="num">{pass_rate:.1f}%</div><div class="label">通过率</div></div>
</div>

<div class="table-wrap">
    <table>
    <thead>
        <tr><th>#</th><th>用例名称</th><th>功能模块</th><th>用户故事</th><th>优先级</th><th>状态</th><th>耗时</th><th>截图</th></tr>
    </thead>
    <tbody>{rows}</tbody>
    </table>
</div>

{f'''<div class="gallery-title">📸 截图画廊（按用例分组，点击放大）</div>
<div class="gallery">{gallery_html}</div>''' if gallery_html else ''}

<div class="footer">GGJX ERP UI 自动化测试框架 ｜ Playwright + Pytest + Allure</div>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <span class="lightbox-close">&times;</span>
    <img id="lightbox-img" src="" alt="截图" />
</div>

<script>
function openLightbox(src) {{
    document.getElementById('lightbox-img').src = src;
    document.getElementById('lightbox').classList.add('show');
}}
function closeLightbox() {{
    document.getElementById('lightbox').classList.remove('show');
}}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeLightbox(); }});
</script>

</body>
</html>"""

    HTML_DIR.mkdir(parents=True, exist_ok=True)
    (HTML_DIR / "index.html").write_text(html, encoding="utf-8")

    print(f"报告已生成: {HTML_DIR}/index.html")
    print(f"  总计: {total} | 通过: {len(passed)} | 失败: {len(failed)} | 跳过: {len(skipped)}")
    print(f"  通过率: {pass_rate:.1f}% | 总耗时: {fmt_duration(total_duration)}")
    print(f"  截图: {len(all_screenshots)} 张")


if __name__ == "__main__":
    build_report()
