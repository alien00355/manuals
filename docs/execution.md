# 执行步骤标准

## 日常开发流程

### 1. 开始工作前

```bash
# 创建今日开发日志
python devlog/log.py
```

打开 `devlog/YYYY-MM-DD.md`，填写今日计划。

### 2. 开发中

- 修改代码后运行 `python build.py` 验证构建
- 用浏览器打开 `output/index.html` 检查效果
- 在日志中更新进行中和已完成事项

### 3. 结束工作前

- 更新开发日志，勾选已完成项
- 如有未完成项，移到"待办"或备注原因
- 提交代码并推送

```bash
git add .
git commit -m "描述今天的改动"
git push
```

---

## 添加新产品说明书

### 方式一：手动添加单个说明书

1. 用 MinerU 将 PDF 转换为 Markdown
2. 在 `manuals/{分类名}/` 下创建产品文件夹
3. 将 Markdown 文件命名为 `index.md` 放入文件夹
4. 将图片放入 `images/` 子文件夹
5. 在 `index.md` 开头添加 frontmatter
6. 运行 `python build.py` 构建
7. 预览 `output/index.html` 确认效果
8. Git 提交并推送

### 方式二：批量导入 MinerU 输出

1. 将 MinerU 输出文件夹放入 `md files/`
2. 更新 `batch_import.py` 中的 `PRODUCTS` 映射表
3. 运行 `python batch_import.py`
4. 运行 `python build.py` 构建
5. Git 提交并推送

### 方式三：添加外部链接说明书

适用于在线版说明书（如海尔官网），无需 Markdown 内容：

1. 创建 `manuals/{分类}/{品牌-类型-型号}/index.md`
2. frontmatter 中使用 `link` 字段：

```yaml
---
title: 产品名称
category: 分类名
brand: 品牌
type: 类型
link: https://外部目标网址
---
```

### 文件夹命名规范

```
{品牌名}-{产品类型}-{型号}
```

示例：
- `美的-微波炉-M1-L201B`
- `戴森-吸尘器-V8`
- `海尔-洗衣机-网页链接`

### Frontmatter 模板

```yaml
---
title: {品牌} {类型} {型号} 使用说明书
category: {所属分类}
brand: {品牌名}
type: {产品类型}
model: {型号}
---
```

---

## 内容整理

运行 `python cleanup_content.py` 可自动：
- 删除冗余标题（"使用说明书"、"保留备用"等）
- 安全警告加粗（注意 → **📌 注意**、警告 → **⚠️ 警告**）
- 清理 LaTeX 公式残留（`$\mathrm{}$` 等）
- 删除 `$$` OCR 乱码块
- 重复标题去重（维护与保养 → 维护与保养(2)）
- 修复已知 OCR 截断文本

---

## 网站部署流程

### 当前部署信息

- **仓库**：`alien00355/manuals`
- **网址**：`https://alien00355.github.io/manuals/`
- **构建方式**：GitHub Actions 自动（推送 `main` 分支即触发）
- **构建命令**：`python build.py`
- **输出目录**：`output/`

### 日常更新部署

```bash
python build.py      # 重新构建
git add .
git commit -m "更新说明书"
git push             # 推送后 GitHub Actions 自动部署
```

---

## 构建脚本扩展

### 添加新分类图标

编辑 `build.py` 中的 `CATEGORY_ICONS` 字典：

```python
CATEGORY_ICONS = {
    ...
    "新分类名": "🔧",  # 选择合适的 Emoji
}
```

### 自定义模板

编辑 `template/base.html`，修改布局或添加新元素。模板变量：
- `{{title}}` — 页面标题
- `{{root}}` — 相对根路径（`./`, `../`, `../../`）
- `{{breadcrumb}}` — 面包屑导航 HTML
- `{{content}}` — 页面主体 HTML

### 修改样式

编辑 `static/style.css`，遵循 `:root` 中的 CSS 变量体系。

---

## 故障排查

| 问题 | 检查项 |
|------|--------|
| 搜索不工作 | 检查 `output/search-index.json` 是否存在 |
| 图片不显示 | 检查 Markdown 中图片路径是否为 `images/xxx.jpg`；确认图片文件夹存在 |
| 构建报错 | 运行 `pip install -r requirements.txt` 安装依赖 |
| 样式异常 | 检查 `output/static/style.css` 是否存在 |
| 中文乱码 | 确保所有 `.md` 文件是 UTF-8 编码 |
| GitHub Pages 部署失败 | 检查 Settings → Pages 中 Source 是否为 GitHub Actions |
| 构建成功但线上不更新 | GitHub Actions 需 1-2 分钟，刷新后等待 |
