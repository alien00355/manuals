"""
说明书内容整理 — 修复标题层级 + 加粗强调 + 清理格式
"""
import re, sys
from pathlib import Path

MANUALS_DIR = Path(r"c:\Users\DELL\Documents\VS\家庭说明书\manuals")

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def fix_content(text: str) -> str:
    """整理一份 Markdown 说明书"""
    lines = text.split("\n")
    result = []
    in_frontmatter = False
    fm_done = False

    for i, line in enumerate(lines):
        # 保留 frontmatter 不动
        if line.strip() == "---" and not fm_done:
            result.append(line)
            in_frontmatter = not in_frontmatter
            if not in_frontmatter:
                fm_done = True
            continue
        if in_frontmatter:
            result.append(line)
            continue

        # === 1. 删除冗余的通用标题 ===
        stripped = line.strip()
        boring_titles = [
            "使用说明书", "用户手册", "保留备用", "亲爱的用户",
            "使用产品前请仔细阅读本使用说明书，并妥善保管",
            "使用前请仔细阅读本手册并妥善保管",
            "请妥善保管，以备参阅",
            "使用产品前请仔细阅读", "本说明书",
            "使用说明",
        ]
        if stripped.startswith("#"):
            hashes, title = re.match(r"^(#{1,4})\s*(.*)$", stripped).groups()
            title_clean = title.strip()
            # 跳过无聊标题
            if title_clean in boring_titles or len(title_clean) < 2:
                continue
            # 产品品牌 + 分隔符（如 "ROBAM老板 | 食具消毒柜"）
            if re.match(r"^[A-Za-z\u4e00-\u9fff]+\s*\|", title_clean):
                continue
            # 纯品牌名重复
            if title_clean in ["FOTILE 方太", "SUPOR 苏泊尔", "SAMSUNG",
                               "OZNER浩泽", "YAMAHA", "THERMOS 隧康師",
                               "ROBAM老板", "JILILAI 吉利来"]:
                continue
            # 把"注意"从 h3 降为粗体段落
            if title_clean in ["注意", "注", "警告", "危险", "建议", "禁止事项"]:
                emoji = {"注意": "📌", "注": "📌", "警告": "⚠️", "危险": "🚨",
                         "建议": "💡", "禁止事项": "🚫"}.get(title_clean, "📌")
                result.append(f"\n**{emoji} {title_clean}**\n")
                continue
            # h1 太多了，降级：h1→h2, h2→h3, h3→h4, 但至少保留 h2
            level = len(hashes)
            if level == 1:
                result.append(f"## {title_clean}")
            elif level <= 4:
                result.append(line)
            else:
                result.append(line)
        else:
            # === 2. 行内加粗处理 ===
            # 【警告】→ 粗体
            line = re.sub(r"【(警告|注意|危险|建议|重要)】", r"**⚠️ \1**", line)
            # 按键名称加粗（中文按键）
            line = re.sub(r"(按下|按|点击|轻按)\s*(【?\w+/?\+\-】?|[\u4e00-\u9fff]+键)", r"\1 **\2**", line)

            # === 3. 清理残留格式 ===
            # LaTeX 公式
            line = re.sub(r"\$\s*\\mathrm\s*\{\s*~?\s*(\w+)\s*\}", r"\1", line)
            line = re.sub(r"\$\s*\\text\s*\{([^}]*)\}\s*\$", r"\1", line)
            line = re.sub(r"\$\s*([\d.,\s]+)\s*\$", r"\1", line)
            # 多余空格
            line = re.sub(r" {3,}", "  ", line)

            result.append(line)

    return "\n".join(result)


def process_all():
    processed = 0
    for md_file in sorted(MANUALS_DIR.rglob("index.md")):
        content = md_file.read_text(encoding="utf-8")
        fixed = fix_content(content)
        if fixed != content:
            md_file.write_text(fixed, encoding="utf-8")
            print(f"  ✅ {md_file.parent.relative_to(MANUALS_DIR)}")
            processed += 1
    print(f"\n📊 整理了 {processed} 本说明书")


if __name__ == "__main__":
    process_all()
