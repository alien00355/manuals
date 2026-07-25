# 🔧 技术规范

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 构建工具 | Python 3.10+ | 扫描说明书、渲染 Markdown、生成静态页面 |
| Markdown 渲染 | Python `markdown` 库 | 服务端渲染 Markdown → HTML |
| 前端框架 | 无框架，原生 HTML/CSS/JS | 保持简单，零运行时依赖 |
| 搜索 | FlexSearch 0.7 (CDN) | 客户端全文搜索，支持中文 |
| 部署 | GitHub Pages + GitHub Actions | 自动构建部署 |
| 样式 | 纯 CSS（CSS Variables） | 温暖色调主题 |

## 项目结构规范

```
family-manuals/
├── manuals/                    # 说明书源文件（用户维护）
│   └── {分类名}/
│       └── {品牌}-{类型}-{型号}/
│           ├── index.md        # 说明书 Markdown 内容
│           └── images/         # 说明书图片
├── template/
│   └── base.html               # 全局 HTML 模板
├── static/
│   ├── style.css               # 样式文件
│   └── search.js               # 搜索功能
├── docs/                       # 项目文档
├── devlog/                     # 开发日志
├── build.py                    # 构建脚本（入口）
├── requirements.txt            # Python 依赖
├── CLAUDE.md                   # AI 助手指引
└── output/                     # 构建输出（不提交到 Git）
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
---
```

### 正文规范

- 使用标准 Markdown 语法
- 图片放在 `images/` 子文件夹，引用时用相对路径 `images/xxx.jpg`
- 层级标题用 `#` `##` `###`（会自动生成侧边栏目录）
- 表格可用于参数、故障排除等内容

## 构建流程

```
build.py 执行流程：
1. 清空 output/ 目录
2. 复制 static/ 到 output/static/
3. 扫描 manuals/ 下所有 index.md
4. 解析 frontmatter → 提取元数据
5. Markdown → HTML 渲染
6. 移除正文中的首个 h1（避免与页面标题重复）
7. 生成详情页、分类页、首页
8. 复制图片到对应 output 路径
9. 生成 search-index.json
```

## 搜索实现

- **索引格式**：JSON 文件，包含所有说明书的纯文本内容
- **搜索库**：FlexSearch Document 索引
- **索引字段**：title, brand, type, content
- **搜索方式**：正向分词（`tokenize: 'forward'`），适合中文
- **结果展示**：标题 + 匹配片段高亮 + 分类/品牌标签

## URL 结构

| 页面 | URL 路径 |
|------|----------|
| 首页 | `/` |
| 分类页 | `/{分类名}/` |
| 详情页 | `/{分类名}/{产品文件夹}/` |
| 搜索索引 | `/search-index.json` |
| 静态资源 | `/static/style.css`, `/static/search.js` |
