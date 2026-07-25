"""
批量导入 MinerU 输出 → 说明书项目
"""
import os, re, sys, shutil
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(r"c:\Users\DELL\Documents\VS\家庭说明书")
MD_FILES = BASE / "md files"
MANUALS = BASE / "manuals"

# === 产品识别映射 ===
# (源文件夹关键字, 产品目录名, 分类, 品牌, 类型, 型号)
PRODUCTS = [
    ("19f9945628a", "苏泊尔-空气炸锅-KJ60Y807", "厨房电器", "苏泊尔", "空气炸锅", "KJ60Y807"),
    ("165835", "三星-液晶电视-Q7F", "数码产品", "三星", "液晶电视", "QLED Q7F"),
    ("171448", "通用-干衣机-HGY901P", "清洁电器", "通用", "干衣机", "HGY901P"),
    ("172842", "浩泽-纯水机-JZY-A2B3", "厨房电器", "浩泽", "纯水机", "JZY-A2B3"),
    ("202958(1)", "格兰仕-电烤箱-iK2R", "厨房电器", "格兰仕", "电烤箱", "iK2R(TM)"),
    ("202958.pdf", "米家-无线吸尘器-1C", "清洁电器", "米家", "无线吸尘器", "1C"),
    ("204455", "苏泊尔-保温杯-真空", "厨房电器", "苏泊尔", "保温杯", "真空保温杯"),
    ("204758", "幸实科技-医用拐-手杖", "其他", "幸实科技", "医用拐", "手杖"),
    ("204900", "美的-电热水壶-通用", "厨房电器", "美的", "电热水壶", ""),
    ("210853", "通用-电热水瓶-通用", "厨房电器", "通用", "电热水瓶", ""),
    ("211031", "膳魔师-保温杯-高真空", "厨房电器", "膳魔师", "保温杯", "高真空不锈钢"),
    ("211155", "苏泊尔-电热水杯-液体加热", "厨房电器", "苏泊尔", "电热水杯", "液体加热器"),
    ("211506", "吉利来-料理机-充电式", "厨房电器", "吉利来", "食物料理机", "充电式"),
    ("211617", "通用-灭蚊灯-全自动", "其他", "通用", "灭蚊灯", "全自动"),
    ("211802", "方太-洗碗机-JBSD2T-Q3", "厨房电器", "方太", "水槽洗碗机", "JBSD2T-Q3"),
    ("212006", "老板-消毒柜-ZTD100C-817", "厨房电器", "老板", "食具消毒柜", "ZTD100C-817"),
]


def clean_markdown(text: str) -> str:
    """清洗 MinerU 输出的 Markdown，使其更美观"""
    # 1. 删除 LaTeX 数学公式标签，保留纯文本
    text = re.sub(r"\$\s*\\mathrm\s*\{\s*~?\s*(\w+)\s*\}", r"\1", text)
    text = re.sub(r"\$\s*\\text\s*\{([^}]*)\}\s*\$", r"\1", text)
    text = re.sub(r"\$\s*([^$]*?)\s*\$", r"\1", text)  # 剩余简单 $...$
    text = re.sub(r"\\textcircled\{[^}]*\}", "※", text)
    text = re.sub(r"\\leqslant", "<=", text)
    text = re.sub(r"\\geqslant", ">=", text)

    # 2. 清理 &#160; 等 HTML 实体残留
    text = text.replace("&#160;", " ")

    # 3. 合并 3 个以上连续空行为 2 个空行
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    # 4. 删除纯空格行
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)

    # 5. 修复行内过长的空格
    text = re.sub(r" {3,}", "  ", text)

    return text


def process():
    imported = 0

    for keyword, folder_name, category, brand, ptype, model in PRODUCTS:
        # 查找匹配的源文件夹
        src_dir = None
        for d in MD_FILES.iterdir():
            if d.is_dir() and keyword in d.name:
                src_dir = d
                break

        if not src_dir:
            print(f"  ⚠️  未找到匹配: {keyword}")
            continue

        md_src = src_dir / "full.md"
        if not md_src.exists():
            # 尝试其他 .md 文件
            candidates = list(src_dir.glob("*.md"))
            if candidates:
                md_src = candidates[0]
            else:
                print(f"  ⚠️  无 md 文件: {src_dir.name}")
                continue

        # 目标目录
        dest_dir = MANUALS / category / folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        # 读取并清洗 Markdown
        content = md_src.read_text(encoding="utf-8")
        body = clean_markdown(content)

        # 构建 frontmatter
        title = f"{brand} {ptype} {model} 使用说明书".replace("  ", " ").strip()
        frontmatter = f"""---
title: {title}
category: {category}
brand: {brand}
type: {ptype}
model: {model}
---

"""
        # 写入 index.md
        dest_md = dest_dir / "index.md"
        dest_md.write_text(frontmatter + body, encoding="utf-8")

        # 复制图片
        src_images = src_dir / "images"
        dest_images = dest_dir / "images"
        if src_images.exists() and any(src_images.iterdir()):
            if dest_images.exists():
                shutil.rmtree(dest_images)
            shutil.copytree(src_images, dest_images)

        img_count = len(list(dest_images.glob("*"))) if dest_images.exists() else 0
        print(f"  ✅ {category}/{folder_name} ({img_count}张图)")
        imported += 1

    print(f"\n🎉 共导入 {imported} 本说明书")


if __name__ == "__main__":
    process()
