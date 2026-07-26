# 技术规范

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 构建工具 | Python 3.10+ | 扫描说明书、渲染 Markdown、生成静态页面 |
| Markdown 渲染 | Python `markdown` 库 | 服务端渲染 Markdown → HTML |
| 前端框架 | 无框架，原生 HTML/CSS/JS | 保持简单，零运行时依赖 |
| 搜索 | 纯 JavaScript（自研） | 零外部依赖，客户端全文搜索，支持中文 |
| 图片灯箱 | 纯 JavaScript（自研） | 点击图片全屏放大，ESC 关闭 |
| 字体 | Noto Sans SC (Google Fonts) | 简体中文优化，非阻塞加载 |
| 部署 | GitHub Pages + GitHub Actions | 自动构建部署 |
| 样式 | 纯 CSS（CSS Variables） | Bento Grids + Book & Reading 暖色主题 |
| 设计系统 | ui-ux-pro-max | 色彩/字体/风格推荐来源 |

## 项目结构

```
manuals/
├── manuals/                     # 说明书源文件（用户维护）
│   ├── 厨房电器/                # 11 本
│   ├── 清洁电器/                # 4 本（含 1 本外部链接）
│   ├── 数码产品/                # 2 本
│   ├── 安防设备/                # 1 本
│   └── 其他/                    # 2 本
├── template/
│   └── base.html                # 全局 HTML 模板
├── static/
│   ├── style.css                # 样式文件
│   └── search.js                # 搜索 + 图片灯箱
├── docs/                        # 项目文档
├── devlog/                      # 开发日志
├── build.py                     # 构建脚本（入口）
├── batch_import.py              # 批量导入 MinerU 输出
├── cleanup_content.py           # Markdown 内容整理
├── requirements.txt             # Python 依赖
├── CLAUDE.md                    # AI 助手指引
├── .github/workflows/deploy.yml # GitHub Actions 部署
└── output/                      # 构建输出（不提交到 Git）
```

## Markdown 文件规范

### 必填元数据（Frontmatter）

```yaml
---
title: 产品名称 + 型号 + "使用说明书"
category: 所属分类（与文件夹名一致）
brand: 品牌名
type: 产品类型
model: 产品型号（可选）
link: https://外部链接（可选，有此字段则为外部链接型）
---
```

### 两种说明书类型

| 类型 | frontmatter | 渲染方式 |
|------|-------------|----------|
| 本地 Markdown | 有正文内容 | Python markdown → HTML，含目录侧边栏 |
| 外部链接 | `link` 字段不为空 | 产品卡片直链外部 URL，详情页显示跳转按钮 |

### 正文规范

- 使用标准 Markdown 语法
- 图片放在 `images/` 子文件夹，引用时用相对路径 `images/xxx.jpg`
- 层级标题用 `##` `###`（会自动生成侧边栏目录）
- 安全警告使用加粗标记：`**⚠️ 警告**`、`**📌 注意**`
- 表格可用于参数、故障排除等内容（自动识别表头、斑马纹）

## 构建流程

```
build.py 执行流程：
1. 清空 output/ 目录
2. 复制 static/ 到 output/static/
3. 扫描 manuals/ 下所有 index.md
4. 解析 frontmatter → 提取元数据 + 检测外部链接
5. 对本地类型：提取标题 → 渲染 Markdown → 注入标题锚点 id
6. 对外部链接：生成跳转引导页
7. 移除正文首个 h1（避免与页面头部重复）
8. 智能识别表格表头（rowspan/colspan）→ 包裹 thead/tbody
9. 生成详情页、分类页、首页
10. 复制图片到对应 output 路径
11. 生成 search-index.json
```

## 搜索实现

- **索引格式**：JSON 文件，包含所有说明书的纯文本内容
- **搜索方式**：纯 JavaScript 遍历 + 关键词匹配，零外部依赖
- **评分权重**：标题匹配 100 > 品牌/类型匹配 50 > 正文匹配 10
- **结果展示**：标题 + 匹配片段高亮 + 类型/品牌标签
- **交互**：输入防抖 200ms、↑↓ 键选择、Enter 跳转

## URL 结构

| 页面 | URL 路径 |
|------|----------|
| 首页 | `/` |
| 分类页 | `/{分类名}/` |
| 详情页（本地） | `/{分类名}/{产品文件夹}/` |
| 详情页（外部链接） | 直接跳转目标 URL（新标签页） |
| 搜索索引 | `/search-index.json` |
| 静态资源 | `/static/style.css`, `/static/search.js` |
