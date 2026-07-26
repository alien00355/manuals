"""
家庭说明书 — 静态网站构建脚本
用法: python build.py
"""

import os
import re
import json
import sys
import shutil
from pathlib import Path
from html import escape

# Windows 终端 UTF-8 编码兼容
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    import markdown as md_lib
except ImportError:
    print("=" * 50)
    print("❌ 缺少 Python 依赖库")
    print("=" * 50)
    print()
    print("当前使用的 Python: " + sys.executable)
    print()
    print("请运行以下命令安装依赖：")
    print(f"  \"{sys.executable}\" -m pip install markdown pyyaml")
    print()
    print("或者：")
    print("  pip install -r requirements.txt")
    print("=" * 50)
    exit(1)

# --- 配置 ---
BASE_DIR = Path(__file__).parent
MANUALS_DIR = BASE_DIR / "manuals"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE_FILE = BASE_DIR / "template" / "base.html"
STATIC_DIR = BASE_DIR / "static"

# 分类图标映射
CATEGORY_ICONS = {
    "厨房电器": "🍳",
    "清洁电器": "🧹",
    "家具": "🪑",
    "数码产品": "📱",
    "卫浴设备": "🚿",
    "照明电器": "💡",
    "冷暖电器": "🌡️",
    "安防设备": "🔒",
    "其他": "📦",
}


# --- 工具函数 ---
def parse_frontmatter(text: str):
    """解析 Markdown 文件头部的 YAML frontmatter"""
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:
                        meta[key] = value
            body = parts[2].strip()
    return meta, body


def slugify(text: str) -> str:
    """生成标题的锚点 ID，与 markdown 库的 toc 扩展保持一致"""
    anchor = re.sub(r"[^\w一-鿿]+", "-", text).strip("-").lower()
    return anchor if anchor else "section"


def extract_headings(markdown_text: str):
    """从 Markdown 中提取标题，过滤噪音，生成唯一锚点"""
    seen_anchors = {}
    headings = []
    for line in markdown_text.split("\n"):
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()

        # 过滤噪音：去 HTML 标签后的纯文本太短则跳过
        clean = re.sub(r"<[^>]+>", "", title).strip()
        # 跳过空标题、纯符号、单字符
        if not clean or len(clean) < 2:
            continue
        # 跳过纯数字/符号（如 "#"、"*"）
        if re.match(r"^[\W_]+$", clean):
            continue

        base_anchor = slugify(clean)
        # 处理重复锚点：注 → 注-2, 注-3 ...
        if base_anchor in seen_anchors:
            seen_anchors[base_anchor] += 1
            anchor = f"{base_anchor}-{seen_anchors[base_anchor]}"
        else:
            seen_anchors[base_anchor] = 1
            anchor = base_anchor

        headings.append({"level": level, "title": title, "anchor": anchor})
    return headings


def add_heading_ids(html: str, headings: list) -> str:
    """给渲染后的 HTML 标题标签添加 id 属性，使目录锚点可以跳转"""
    for h in headings:
        title_pattern = re.escape(h["title"])
        pattern = rf"(<h{h['level']}>)({title_pattern})(</h{h['level']}>)"
        replacement = rf'\1<span id="{h["anchor"]}"></span>\2\3'
        if f'id="{h["anchor"]}"' not in html:
            html = re.sub(pattern, replacement, html, count=1)
    return html


def wrap_collapsible_sections(html: str) -> str:
    """将 h2 标题及其后续内容包裹为折叠章节（默认折叠）"""
    # 在 h2 前插入分隔标记
    html = re.sub(r'(<h2[^>]*>)', r'<!--SECTION-->\1', html)
    parts = html.split('<!--SECTION-->')
    if not parts or not parts[0].strip():
        parts = parts[1:]

    result = [parts[0]] if parts and not re.search(r'<h2', parts[0]) else []

    for part in parts:
        if not re.search(r'<h2', part):
            if result:
                result[-1] += part
            else:
                result.append(part)
            continue
        result.append(part)

    wrapped = []
    first_h2_seen = False
    for block in result:
        m = re.match(r'(<h2[^>]*>.*?</h2>)(.*)', block, re.DOTALL)
        if m:
            heading_html = m.group(1)
            body = m.group(2).strip()
            # 默认展开第一个 h2 章节
            if not first_h2_seen:
                open_attr = ' open'
                first_h2_seen = True
            else:
                open_attr = ''
            section_id = re.search(r'id="([^"]*)"', heading_html)
            sid = section_id.group(1) if section_id else f'section-{len(wrapped)}'
            wrapped.append(
                f'<section class="collapsible-section" data-section="{sid}">'
                f'<details{open_attr}><summary class="section-toggle">{heading_html}'
                f'<span class="toggle-icon"></span></summary>'
                f'<div class="section-body">{body}</div>'
                f'</details></section>'
            )
        else:
            wrapped.append(block)

    return '\n'.join(wrapped)


def extract_section_texts(html: str) -> dict:
    """从 HTML 中提取每个 h2/h3 章节的纯文本，用于详情页段内搜索"""
    sections = {}
    # 按 section 标签分割
    for match in re.finditer(
        r'<section[^>]*data-section="([^"]*)"[^>]*>.*?'
        r'<summary[^>]*>(.*?)</summary>\s*'
        r'<div class="section-body">(.*?)</div>\s*'
        r'</details>\s*</section>',
        html, re.DOTALL
    ):
        sid = match.group(1)
        summary = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        body = re.sub(r'<[^>]+>', '', match.group(3))
        body = re.sub(r'\s+', ' ', body).strip()
        sections[sid] = {'title': summary, 'text': body}
    return sections


def beautify_tables(html: str) -> str:
    """美化表格：智能识别表头行，包裹 thead/tbody，高亮标题"""
    def fix_table(match):
        table = match.group(0)
        rows = re.findall(r"<tr>(.*?)</tr>", table, re.DOTALL)

        if not rows:
            return table

        # 智能识别表头行数：
        # 规则1: 首行必为表头
        # 规则2: 若某行有 rowspan=N，则后面 N-1 行也纳入表头
        # 规则3: 若某行有 colspan，且该行已在表头区域，继续纳入
        head_count = 1
        i = 0
        while i < head_count and i < len(rows):
            row_text = rows[i]
            rowspan_match = re.search(r'rowspan\s*=\s*["\']?(\d+)', row_text, re.IGNORECASE)
            if rowspan_match:
                span = int(rowspan_match.group(1))
                head_count = max(head_count, i + span)  # rowspan 覆盖的行都是表头
            i += 1

        # 第2条规则补充：紧跟在表头区域后、含 colspan 的行也可能是子表头
        while head_count < len(rows):
            if re.search(r'colspan', rows[head_count], re.IGNORECASE):
                head_count += 1
            else:
                break

        # 保证不超过总行数
        head_count = min(head_count, len(rows))

        # 重建表格
        head_rows = rows[:head_count]
        body_rows = rows[head_count:]

        parts = ['<table>']
        if head_rows:
            parts.append('<thead>')
            for row in head_rows:
                # td → th
                row = re.sub(r"<td", "<th", row)
                row = re.sub(r"</td>", "</th>", row)
                parts.append(f'<tr>{row}</tr>')
            parts.append('</thead>')

        if body_rows:
            parts.append('<tbody>')
            for row in body_rows:
                parts.append(f'<tr>{row}</tr>')
            parts.append('</tbody>')

        parts.append('</table>')
        return ''.join(parts)

    return re.sub(r"<table>.*?</table>", fix_table, html, flags=re.DOTALL)


def md_to_html(md_text: str):
    """将 Markdown 转换为 HTML"""
    html = md_lib.markdown(
        md_text,
        extensions=["fenced_code", "tables", "nl2br"],
    )
    # 美化表格
    html = beautify_tables(html)
    return html


def read_template():
    """读取 HTML 模板"""
    return TEMPLATE_FILE.read_text(encoding="utf-8")


def fill_template(template: str, **kwargs) -> str:
    """填充模板占位符"""
    result = template
    for key, value in kwargs.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def category_icon(name: str) -> str:
    """获取分类图标"""
    return CATEGORY_ICONS.get(name, "📁")


# --- 构建主流程 ---
def build():
    print("=" * 50)
    print("📖 家庭说明书 — 网站构建工具")
    print("=" * 50)

    # 1. 清理输出目录
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    # 2. 复制静态资源
    output_static = OUTPUT_DIR / "static"
    shutil.copytree(STATIC_DIR, output_static)
    print("✅ 静态资源已复制")

    # 3. 扫描说明书
    print("🔍 扫描说明书文件…")
    manuals = []
    categories = {}

    # 扫描每个产品文件夹，优先找 index.md，否则取第一个 .md 文件
    for cat_dir in sorted(MANUALS_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name

        for prod_dir in sorted(cat_dir.iterdir()):
            if not prod_dir.is_dir():
                continue
            folder_name = prod_dir.name

            # 优先 index.md，否则找第一个 .md 文件
            md_file = prod_dir / "index.md"
            if not md_file.exists():
                candidates = sorted(prod_dir.glob("*.md"))
                if candidates:
                    md_file = candidates[0]
                else:
                    print(f"  ⚠️  跳过（无 .md 文件）: {category}/{folder_name}")
                    continue

            rel_path = md_file.parent.relative_to(MANUALS_DIR)

            # 读取内容
            content = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)

            # 检测是否为外部链接型说明书
            external_link = meta.get("link", "").strip()
            is_external = bool(external_link)

            # 从文件夹名推断信息
            folder_parts = folder_name.split("-") if folder_name else []

            title = meta.get("title", folder_name)
            brand = meta.get("brand", folder_parts[0] if len(folder_parts) > 0 else "")
            ptype = meta.get("type", folder_parts[1] if len(folder_parts) > 1 else "")
            ptype = meta.get("type", ptype)
            category = meta.get("category", category)

            if is_external:
                # 外部链接型：不渲染 markdown，只记录链接和简要说明
                headings = []
                body_html = f'<p>本说明书为在线版本，请点击下方链接查看：</p><p><a href="{escape(external_link)}" target="_blank" rel="noopener" class="external-link-btn">📖 查看说明书 →</a></p>'
                body_text = body
            else:
                # 先提取标题结构（从原始 Markdown），再渲染 HTML
                headings = extract_headings(body)

                # 渲染 Markdown
                body_html = md_to_html(body)
                # 给 HTML 中的标题添加 id，使目录锚点可跳转
                body_html = add_heading_ids(body_html, headings)
                # 移除正文中的第一个 h1 标题（已在页面头部显示，避免重复）
                body_html = re.sub(r"^<h1>.*?</h1>\s*", "", body_html, count=1)
                # 包裹 h2 章节为折叠块
                body_html = wrap_collapsible_sections(body_html)

            # 提取纯文本（用于搜索索引 — 详情页用分章节，全局索引用元数据）
            body_text = re.sub(r"<[^>]+>", "", body_html)
            body_text = re.sub(r"\s+", " ", body_text)

            # 提取分章节纯文本（用于详情页段内搜索）
            section_texts = extract_section_texts(body_html) if not is_external else {}

            manual = {
                "id": str(rel_path).replace("\\", "/"),
                "title": title,
                "category": category,
                "brand": brand,
                "type": ptype,
                "body_html": body_html,
                "body_text": body_text,
                "headings": headings,
                "path": str(rel_path).replace("\\", "/"),
                "source_dir": md_file.parent,
                "is_external": is_external,
                "external_link": external_link,
                "section_texts": section_texts,
            }

            manuals.append(manual)

            # 按分类分组
            if category not in categories:
                categories[category] = []
            categories[category].append(manual)

            print(f"  📄 {manual['path']} → {title}")

    if not manuals:
        print("⚠️  未找到任何说明书！请在 manuals/ 文件夹下按「分类/产品名/index.md」的格式放入文件。")
        return

    print(f"\n📊 共找到 {len(manuals)} 本说明书，分布在 {len(categories)} 个分类中。")

    # 排序分类
    sorted_categories = sorted(categories.items(), key=lambda x: x[0])

    # 4. 读取模板
    template = read_template()

    # 5. 生成说明书详情页
    print("\n📝 生成说明书详情页…")
    for m in manuals:
        # 构建面包屑
        breadcrumb_html = f"""
        <nav class="breadcrumb">
            <a href="../../index.html">首页</a><span>›</span>
            <a href="../index.html">{escape(m['category'])}</a><span>›</span>
            <span class="current">{escape(m['title'])}</span>
        </nav>"""

        # 构建目录侧边栏
        toc_html = ""
        if m["headings"]:
            toc_items = []
            for h in m["headings"]:
                cls = f"toc-h{h['level']}"
                toc_items.append(
                    f'<li class="{cls}"><a href="#{h["anchor"]}">{escape(h["title"])}</a></li>'
                )
            toc_html = f"""
            <aside class="detail-sidebar">
                <h3>📑 目录</h3>
                <ul class="toc-list">
                    {''.join(toc_items)}
                </ul>
            </aside>"""

        # 产品头部
        tags_html = ""
        if m["type"]:
            tags_html += f'<span class="tag tag-type">{escape(m["type"])}</span>'
        if m["brand"]:
            tags_html += f'<span class="tag tag-brand">{escape(m["brand"])}</span>'

        detail_header = f"""
        <div class="detail-header">
            <div class="tags">{tags_html}</div>
            <h1>{escape(m['title'])}</h1>
            <div class="brand-info">品牌：<strong>{escape(m['brand'])}</strong>　类型：{escape(m['type'])}</div>
        </div>"""

        # 分章节数据（用于详情页段内搜索）
        section_script = ""
        if m.get("section_texts"):
            section_json = json.dumps(m["section_texts"], ensure_ascii=False)
            section_script = f"<script>window.__MANUAL_SECTIONS__ = {section_json};</script>"

        # 内容区
        content_html = f"""
        {section_script}
        <div class="detail-wrapper">
            {toc_html if m['headings'] else ''}
            <div class="detail-content">
                {detail_header}
                {m['body_html']}
            </div>
        </div>"""

        page_html = fill_template(
            template,
            title=escape(m["title"]),
            root="../../",
            breadcrumb=breadcrumb_html,
            content=content_html,
        )

        # 写入文件
        out_page_dir = OUTPUT_DIR / m["path"]
        out_page_dir.mkdir(parents=True, exist_ok=True)
        (out_page_dir / "index.html").write_text(page_html, encoding="utf-8")

        # 复制图片
        source_images = m["source_dir"] / "images"
        if source_images.exists():
            dest_images = out_page_dir / "images"
            if dest_images.exists():
                shutil.rmtree(dest_images)
            shutil.copytree(source_images, dest_images)

    print(f"  ✅ 已生成 {len(manuals)} 个说明书页面")

    # 6. 生成分类列表页
    print("📁 生成分类页面…")
    for cat_name, cat_manuals in sorted_categories:
        product_cards = []
        for m in cat_manuals:
            tags_html = ""
            if m["type"]:
                tags_html += f'<span class="tag tag-type">{escape(m["type"])}</span>'
            if m["brand"]:
                tags_html += f'<span class="tag tag-brand">{escape(m["brand"])}</span>'

            # 分类页已经在分类文件夹内，链接只需产品名
            prod_folder = m['id'].rsplit('/', 1)[-1]
            if m.get("is_external"):
                href = m["external_link"]
                target = 'target="_blank" rel="noopener"'
            else:
                href = f"{prod_folder}/index.html"
                target = ""
            product_cards.append(f"""
            <a href="{href}" class="product-card" {target}>
                <div class="product-card-tags">{tags_html}</div>
                <div class="product-card-title">{escape(m['title'])}</div>
                <div class="product-card-model">{escape(m['brand'])}</div>
            </a>""")

        breadcrumb_html = f"""
        <nav class="breadcrumb">
            <a href="../index.html">首页</a><span>›</span>
            <span class="current">{escape(cat_name)}</span>
        </nav>"""

        content_html = f"""
        <h2 class="section-title">{category_icon(cat_name)} {escape(cat_name)}</h2>
        <p style="color: var(--color-text-light); margin-bottom: 1.5rem;">共 {len(cat_manuals)} 本说明书</p>
        <div class="product-list">
            {''.join(product_cards)}
        </div>"""

        page_html = fill_template(
            template,
            title=escape(cat_name),
            root="../",
            breadcrumb=breadcrumb_html,
            content=content_html,
        )

        out_cat_dir = OUTPUT_DIR / cat_name
        out_cat_dir.mkdir(parents=True, exist_ok=True)
        (out_cat_dir / "index.html").write_text(page_html, encoding="utf-8")

    print(f"  ✅ 已生成 {len(sorted_categories)} 个分类页面")

    # 7. 生成首页
    print("🏠 生成首页…")
    category_cards = []
    for cat_name, cat_manuals in sorted_categories:
        category_cards.append(f"""
        <a href="{cat_name}/index.html" class="category-card">
            <span class="category-icon">{category_icon(cat_name)}</span>
            <span class="category-name">{escape(cat_name)}</span>
            <span class="category-count">{len(cat_manuals)} 本说明书</span>
        </a>""")

    breadcrumb_html = ""  # 首页无面包屑

    content_html = f"""
    <div class="home-hero">
        <h1>📖 家庭说明书</h1>
        <p>所有家电、家具、数码产品说明书，一处查阅</p>
    </div>
    <div class="category-grid">
        {''.join(category_cards)}
    </div>"""

    page_html = fill_template(
        template,
        title="首页",
        root="./",
        breadcrumb=breadcrumb_html,
        content=content_html,
    )

    (OUTPUT_DIR / "index.html").write_text(page_html, encoding="utf-8")
    print("  ✅ 首页已生成")

    # 添加 root meta 标签到所有页面（用于 JS 定位资源）
    # 这个我们在模板中通过 root 变量已经处理了

    # 8. 生成搜索索引
    print("🔍 生成搜索索引…")
    search_data = []
    for m in manuals:
        search_data.append(
            {
                "id": m["id"],
                "title": m["title"],
                "brand": m["brand"],
                "type": m["type"],
                "category": m["category"],
                "path": m["path"],
            }
        )

    search_index_path = OUTPUT_DIR / "search-index.json"
    search_index_path.write_text(json.dumps(search_data, ensure_ascii=False), encoding="utf-8")
    print(f"  ✅ 搜索索引已生成 ({len(search_data)} 条记录)")

    # 9. 总结
    print("\n" + "=" * 50)
    print("🎉 构建完成！")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"📊 说明书数量: {len(manuals)}")
    print(f"📂 分类数量: {len(categories)}")
    print("\n💡 提示：用浏览器打开 output/index.html 即可预览网站。")
    print("=" * 50)


if __name__ == "__main__":
    build()
