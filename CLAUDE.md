# CLAUDE.md — 家庭说明书项目指引

## 项目概述

这是一个**家庭说明书集合网页**项目。用户将 PDF 说明书通过 MinerU 转为 Markdown，放入 `manuals/` 文件夹，运行 `python build.py` 即可生成静态网站。网站部署到 GitHub Pages 线上访问。

**当前状态**：19 本说明书，5 个分类，约 441 张图片，在线访问 `https://alien00355.github.io/manuals/`。

**用户是非技术背景的小白**，所有操作需保持简单明了。

---

## 标准文件路径

| 文件 | 路径 | 说明 |
|------|------|------|
| 开发需求 | [docs/requirements.md](docs/requirements.md) | 项目核心需求，优先级和状态 |
| 技术规范 | [docs/technical.md](docs/technical.md) | 技术栈、目录结构、构建流程、URL 规范 |
| 设计规范 | [docs/design.md](docs/design.md) | 色彩、字体、组件、间距、响应式断点 |
| 执行步骤 | [docs/execution.md](docs/execution.md) | 日常操作流程、部署步骤、故障排查 |
| 开发日志 | [devlog/](devlog/) | 按日期归档的开发记录 |
| 日志模板 | [devlog/template.md](devlog/template.md) | 每日日志模板 |
| 日志工具 | [devlog/log.py](devlog/log.py) | 自动创建日志、汇总待办 |
| 构建脚本 | [build.py](build.py) | 网站构建入口 |
| 批量导入 | [batch_import.py](batch_import.py) | 从 MinerU 输出批量导入说明书 |
| 内容整理 | [cleanup_content.py](cleanup_content.py) | 清洗 Markdown：LaTeX/乱码/标题/加粗 |
| HTML 模板 | [template/base.html](template/base.html) | 全局页面模板（含 Noto Sans SC 字体） |
| CSS 样式 | [static/style.css](static/style.css) | Bento Grids + Book & Reading 暖色主题 |
| 搜索脚本 | [static/search.js](static/search.js) | 纯 JS 搜索（零外部依赖）+ 图片灯箱 |
| 部署配置 | [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | GitHub Actions 自动部署 |
| 用户说明 | [README.md](README.md) | 给用户的操作指南 |

---

## 工作指引

### 每次开始工作前

1. **创建今日开发日志**：
   ```bash
   python devlog/log.py
   ```
   这会基于模板自动创建 `devlog/YYYY-MM-DD.md`（如已存在则跳过）。

2. **阅读标准文件**：根据任务类型，参考对应的标准文件：
   - 新增功能 → 先看 [docs/requirements.md](docs/requirements.md) 确认需求
   - 修改样式 → 先看 [docs/design.md](docs/design.md) 确认设计规范
   - 修改架构 → 先看 [docs/technical.md](docs/technical.md) 确认技术约束
   - 执行操作 → 先看 [docs/execution.md](docs/execution.md) 确认标准流程

### 修改代码后

1. **运行构建验证**：`python build.py`
2. **检查输出**：确认 `output/` 目录正常生成
3. **更新日志**：在今日 `devlog/` 文件中记录改动

### 结束工作前

- 更新 `devlog/` 中今日日志的完成状态
- 汇总待办事项：`python devlog/log.py --summary`

---

## 关键约定

### 代码风格
- Python 代码使用 UTF-8 编码，注释用中文，需处理 Windows GBK 终端兼容
- CSS 使用 CSS Variables，定义在 `:root` 中，遵循 ui-ux-pro-max 设计系统
- JavaScript 使用 IIFE 包裹，避免全局污染；搜索为纯 JS 零外部依赖
- HTML 模板使用 `{{placeholder}}` 占位符

### 构建产物
- `output/` 目录不提交到 Git（已在 `.gitignore` 中）
- GitHub Actions 在部署时自动构建
- 搜索索引文件：`output/search-index.json`

### 说明书规范
- 文件夹结构：`manuals/{分类}/{品牌-类型-型号}/index.md`
- 图片路径：相对于 `index.md`，放在 `images/` 子文件夹
- Frontmatter 必填：`title`, `category`, `brand`, `type`
- Frontmatter 可选：`model`, `link`（外部链接型说明书）

### 两种说明书类型
| 类型 | 识别方式 | 行为 |
|------|----------|------|
| 本地 Markdown | 有正文内容 | 渲染为详情页，含目录导航 |
| 外部链接 | frontmatter 中有 `link` 字段 | 产品卡片直接跳转外部 URL，生成引导页 |

### 设计系统
- **风格**：Bento Grids（模块化卡片网格，大圆角 18-28px，柔和 4 级阴影）
- **配色**：Book & Reading Tracker（暖棕 `#78716C` + 琥珀 `#D97706` + 纸色背景 `#FFFBEB`）
- **字体**：Noto Sans SC（Google Fonts，300/400/500/600/700/800 字重）
- **来源**：ui-ux-pro-max 设计数据库推荐

### 内容质量
- 安全警告必须加粗：`**⚠️ 警告**`、`**📌 注意**`、`**🚨 危险**`
- 标题层级合理，不跳级，不重复
- LaTeX 公式残留需清理（`$\mathrm{}$` 等）
- MinerU 输出的 `$$` 乱码块需删除

### 兼容性
- 构建脚本需兼容 Windows（处理 GBK/UTF-8 编码问题）
- 网站兼容主流浏览器（Chrome, Edge, Safari, Firefox）
- 响应式适配桌面端（1024px+）、平板（768px）、手机（375-480px）
- 尊重 `prefers-reduced-motion` 系统偏好

---

## 常用命令

```bash
# 构建网站
python build.py

# 安装/更新依赖
pip install -r requirements.txt

# 创建今日日志
python devlog/log.py

# 查看待办汇总
python devlog/log.py --summary

# 查看最近5天日志
python devlog/log.py --recent 5

# 批量导入 MinerU 输出
python batch_import.py

# 整理说明书内容
python cleanup_content.py

# 部署到线上
git add . && git commit -m "更新描述" && git push
```
