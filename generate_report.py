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
    """收集 screenshots 目录中的截图"""
    screenshots = []
    if not SCREENSHOT_DIR.exists():
        return screenshots
    for f in sorted(SCREENSHOT_DIR.glob("*.png"), reverse=True):
        screenshots.append({
            "name": f.name,
            "path": f"../../screenshots/{f.name}",
            "size": f.stat().st_size,
        })
    return screenshots


def copy_step_screenshots(results_map, html_dir):
    """复制步骤中嵌入的截图到 HTML 目录，返回 {source_name: relative_path}"""
    import shutil
    step_ss_dir = html_dir / "step-screenshots"
    if step_ss_dir.exists():
        shutil.rmtree(step_ss_dir)
    step_ss_dir.mkdir(parents=True, exist_ok=True)
    mapping = {}

    for uuid, result in results_map.items():
        for step in result.get("steps", []):
            for att in step.get("attachments", []):
                if att.get("type") == "image/png":
                    src = att.get("source", "")
                    src_file = RAW_DIR / src
                    if src_file.exists():
                        dest = step_ss_dir / src
                        if not dest.exists():
                            shutil.copy2(src_file, dest)
                        mapping[src] = f"step-screenshots/{src}"

    return mapping


def get_step_screenshots(steps, mapping):
    """为步骤列表提取对应的截图路径"""
    ss_list = []
    for step in steps:
        for att in step.get("attachments", []):
            if att.get("type") == "image/png":
                src = att.get("source", "")
                path = mapping.get(src, "")
                if path:
                    ss_list.append({
                        "step_name": step.get("name", ""),
                        "path": path,
                        "name": att.get("name", src[:30]),
                    })
    return ss_list


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


def get_module_name(results_map):
    """从 allure 数据中提取模块名"""
    packages = set()
    for r in results_map.values():
        for l in r.get("labels", []):
            if l["name"] == "package":
                # cases.test_product -> product
                pkg = l["value"].split(".")[-1]
                packages.add(pkg.replace("test_", ""))
    return "_".join(sorted(packages)) if packages else "report"


def build_report():
    results_map, containers = build_id_map()
    all_screenshots = {s["name"]: s for s in collect_screenshots()}

    # 按模块名生成子目录
    module_name = get_module_name(results_map)
    html_dir = ROOT / "reports" / "allure_html" / module_name
    html_dir.mkdir(parents=True, exist_ok=True)

    step_ss_map = copy_step_screenshots(results_map, html_dir)

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

        # Allure 步骤（折叠显示）
        steps = r.get("steps", [])
        step_count = len(steps)
        fail_count = sum(1 for s in steps if s.get("status") not in ("passed",))
        steps_id = f"steps-{idx}"
        step_ss_list = get_step_screenshots(steps, step_ss_map)

        if steps:
            fail_text = f"（{fail_count} 失败）" if fail_count > 0 else ""
            ss_count = len(step_ss_list)
            ss_hint = f" 📷{ss_count}" if ss_count > 0 else ""
            steps_html = f"""<span class="step-toggle" onclick="var d=document.getElementById('{steps_id}');var t=this;d.classList.toggle('open');t.classList.toggle('open');var a=t.querySelector('.arrow');a.textContent=d.classList.contains('open')?'▼':'▶'"><span class="arrow">▶</span> {step_count} 步{ss_hint}{fail_text}</span>"""
            # 步骤展开区放在行下方
            steps_row = ""
            if steps:
                steps_row = f"""
        <tr class="step-row" id="{steps_id}">
            <td colspan="9" class="step-cell">
                <div class="step-detail">"""
                for s in steps:
                    s_name = s.get("name", "")
                    s_status = s.get("status", "passed")
                    s_class = "step-pass" if s_status == "passed" else "step-fail"
                    icon = "✓" if s_status == "passed" else "✗"

                    # 该步骤的截图
                    step_ss_html = ""
                    for ss in step_ss_list:
                        if ss["step_name"] == s_name:
                            step_ss_html += f'<img src="{ss["path"]}" class="step-ss" onclick="event.stopPropagation();openLightbox(\'{ss["path"]}\')" title="{ss["name"]}" />'

                    steps_row += f'<div class="step {s_class}">{icon} {s_name}{step_ss_html}</div>'
                steps_row += """</div>
            </td>
        </tr>"""
        else:
            steps_html = ""

        rows += f"""
        <tr class="{status_class}">
            <td class="center">{idx + 1}</td>
            <td>{name}</td>
            <td>{feature}</td>
            <td>{story}</td>
            <td class="center"><span class="badge severity-{labels.get('severity', '')}">{severity}</span></td>
            <td class="center"><span class="badge status-{status}">{STATUS_CN.get(status, status)}</span></td>
            <td class="center">{duration}</td>
            <td class="steps-col">{steps_html}</td>
            <td class="screenshot-col">{ss_html}</td>
        </tr>
        {steps_row}"""

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

/* Steps - expand below row */
.step-toggle {{ font-size: 12px; color: #3498db; cursor: pointer; user-select: none; border-bottom: 1px dashed #3498db; white-space: nowrap; }}
.step-toggle:hover {{ color: #2980b9; }}
.step-toggle.open {{ color: #2c3e50; border-bottom: none; }}
.step-row {{ display: none; }}
.step-row.open {{ display: table-row; }}
.step-cell {{ padding: 0 !important; }}
.step-cell .step-detail {{ padding: 16px 24px; background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%); text-align: left; display: flex; flex-wrap: wrap; gap: 4px 12px; border-top: 1px solid #e0e7ff; border-bottom: 2px solid #e0e7ff; }}
.step {{ font-size: 12px; padding: 4px 10px; border-radius: 4px; color: #2c3e50; display: inline-flex; align-items: center; gap: 4px; }}
.step-pass {{ }}
.step-fail {{ color: #e74c3c; font-weight: 600; background: #fff0f0; }}
.step-ss {{ width: 160px; height: 90px; object-fit: cover; border-radius: 6px; margin-top: 6px; margin-left: 20px; display: block; border: 1px solid #e0e7ff; cursor: pointer; transition: transform .2s; }}
.step-ss:hover {{ transform: scale(1.03); box-shadow: 0 2px 8px rgba(0,0,0,.1); }}

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
        <tr><th>#</th><th>用例名称</th><th>功能模块</th><th>用户故事</th><th>优先级</th><th>状态</th><th>耗时</th><th>步骤</th><th>截图</th></tr>
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

    (html_dir / "index.html").write_text(html, encoding="utf-8")

    step_ss_count = len(list((html_dir / "step-screenshots").glob("*.png"))) if (html_dir / "step-screenshots").exists() else 0
    print(f"报告已生成: {html_dir}/index.html")
    print(f"  总计: {total} | 通过: {len(passed)} | 失败: {len(failed)} | 跳过: {len(skipped)}")
    print(f"  通过率: {pass_rate:.1f}% | 总耗时: {fmt_duration(total_duration)}")
    print(f"  截图: {len(all_screenshots)} 张 (conftest) + {step_ss_count} 张 (步骤内)")

    # 输出完整测试总结
    print(f"\n{'='*70}")
    print(f"  🧪 GGJX ERP UI 自动化测试总结")
    print(f"{'='*70}")
    print(f"  模块: {module_name}")
    print(f"  时间: {now}")
    print(f"  报告: {html_dir}/index.html")
    print(f"{'='*70}")
    print(f"  用例总数: {total}")
    print(f"  ✅ 通过:   {len(passed)}")
    print(f"  ❌ 失败:   {len(failed)}")
    if skipped:
        print(f"  ⏭️  跳过:   {len(skipped)}")
    print(f"  通过率:   {pass_rate:.1f}%")
    print(f"  总耗时:   {fmt_duration(total_duration)}")
    print(f"  截图:     {len(all_screenshots)} 张（终态）+ {step_ss_count} 张（步骤内）")
    print(f"{'='*70}")

    # 操作覆盖
    all_steps = []
    for r in merged:
        for s in r.get("steps", []):
            all_steps.append(s.get("name", ""))

    print(f"  操作覆盖:")
    step_names = set()
    for s in all_steps:
        clean = s.split(":")[0].split("'")[0].strip()
        if clean and clean not in step_names:
            step_names.add(clean)
            print(f"    - {clean}")
    print(f"{'='*70}")

    # 逐条结果
    print(f"  用例详情:")
    for idx, r in enumerate(merged, 1):
        name = r.get("name", "-")
        status = r.get("status", "-")
        icon = {"passed": "✅", "failed": "❌", "broken": "💥"}.get(status, "⏭️")
        dur = fmt_duration(r.get("duration_ms", 0))
        steps = r.get("steps", [])
        step_str = " → ".join(s.get("name", "")[:30] for s in steps[:4])
        if len(steps) > 4:
            step_str += f" ... (+{len(steps) - 4}步)"
        print(f"    {idx}. {icon} {name}  [{dur}]")
        print(f"       {step_str}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    build_report()
