"""
开发日志工具 — 自动创建每日日志，汇总待办事项
用法:
    python devlog/log.py            # 创建今天的日志（如不存在）
    python devlog/log.py --summary  # 汇总所有待办事项
    python devlog/log.py --recent 5 # 查看最近 5 天的日志
"""

import os
import sys
import re
from pathlib import Path
from datetime import date, timedelta

# Windows 终端 UTF-8 编码兼容
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DEVL_DIR = Path(__file__).parent
TEMPLATE_FILE = DEVL_DIR / "template.md"


def today_str() -> str:
    return date.today().isoformat()


def log_path(day: str = None) -> Path:
    return DEVL_DIR / f"{day or today_str()}.md"


def create_today_log() -> Path:
    """基于模板创建今天的日志（如已存在则跳过）"""
    dest = log_path()
    if dest.exists():
        return dest

    if TEMPLATE_FILE.exists():
        template = TEMPLATE_FILE.read_text(encoding="utf-8")
        content = template.replace("YYYY-MM-DD", today_str())
    else:
        content = f"# 📝 {today_str()}\n\n### ✅ 已完成\n- \n\n### 🔧 进行中\n- \n\n### 📋 待办\n- \n\n### 💡 备注\n- \n"

    dest.write_text(content, encoding="utf-8")
    return dest


def parse_todos(file_path: Path) -> dict:
    """解析日志文件中的待办和完成事项"""
    text = file_path.read_text(encoding="utf-8")
    result = {"date": file_path.stem, "done": [], "ongoing": [], "todo": [], "notes": []}

    current_section = None
    for line in text.split("\n"):
        m = re.match(r"^###\s+(✅\s*已完成|🔧\s*进行中|📋\s*待办|💡\s*备注)", line)
        if m:
            section = m.group(1)
            if "已完成" in section:
                current_section = "done"
            elif "进行中" in section:
                current_section = "ongoing"
            elif "待办" in section:
                current_section = "todo"
            elif "备注" in section:
                current_section = "notes"
            continue

        if current_section and line.startswith("- "):
            item = line[2:].strip()
            if item:
                result[current_section].append(item)

    return result


def show_summary():
    """汇总所有日志中未完成的待办"""
    all_todos = []
    log_files = sorted(DEVL_DIR.glob("20*.md"), reverse=True)
    for f in log_files:
        parsed = parse_todos(f)
        for item in parsed["todo"]:
            all_todos.append((parsed["date"], item))
        for item in parsed["ongoing"]:
            all_todos.append((parsed["date"], f"[进行中] {item}"))

    print("📋 待办事项汇总\n" + "=" * 40)
    if not all_todos:
        print("  ✅ 没有待办事项")
    else:
        for d, item in all_todos:
            print(f"  📅 {d}  →  {item}")
    print(f"\n共 {len(all_todos)} 项待办")


def show_recent(n: int = 5):
    """查看最近 N 天的日志概况"""
    log_files = sorted(DEVL_DIR.glob("20*.md"), reverse=True)[:n]
    for f in log_files:
        parsed = parse_todos(f)
        print(f"📅 {parsed['date']}")
        print(f"  ✅ 完成: {len(parsed['done'])} 项")
        print(f"  📋 待办: {len(parsed['todo'])} 项")
        for item in parsed["done"][:3]:
            print(f"    ✓ {item}")
        if len(parsed["done"]) > 3:
            print(f"    … 还有 {len(parsed['done']) - 3} 项")
        print()


# --- CLI ---
if __name__ == "__main__":
    if "--summary" in sys.argv or "-s" in sys.argv:
        show_summary()
    elif "--recent" in sys.argv or "-r" in sys.argv:
        idx = sys.argv.index("--recent") if "--recent" in sys.argv else sys.argv.index("-r")
        n = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 5
        show_recent(n)
    else:
        dest = create_today_log()
        print(f"📝 今日开发日志: {dest}")
        if dest.stat().st_size < 100:
            print("💡 日志已创建，请打开文件填写今日计划。")
