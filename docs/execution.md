# 📐 执行步骤标准

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
- 提交代码（如有 Git）

```bash
git add .
git commit -m "描述今天的改动"
```

## 添加新产品说明书

### 标准操作步骤

1. 用 MinerU 将 PDF 说明书转换为 Markdown
2. 在 `manuals/{分类名}/` 下创建产品文件夹
3. 将 Markdown 文件命名为 `index.md` 放入文件夹
4. 将图片放入 `images/` 子文件夹
5. 在 `index.md` 开头添加 frontmatter 元数据
6. 运行 `python build.py` 构建
7. 预览 `output/index.html` 确认效果
8. Git 提交并推送

### 文件夹命名规范

```
{品牌名}-{产品类型}-{型号}
```

示例：
- `美的-微波炉-M1-L201B`
- `戴森-吸尘器-V8`
- `宜家-书柜-BILLY`

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

## 网站部署流程

### 首次部署

1. 在 GitHub 创建仓库
2. 本地初始化 Git 并关联远程仓库
3. 推送代码到 GitHub
4. 在仓库 Settings → Pages 中启用 GitHub Actions
5. 等待 Actions 完成构建部署
6. 访问 `https://{用户名}.github.io/{仓库名}/`

### 日常更新部署

```bash
python build.py      # 重新构建
git add .
git commit -m "更新说明书"
git push             # 推送后 GitHub Actions 自动部署
```

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

## 故障排查

| 问题 | 检查项 |
|------|--------|
| 搜索不工作 | 检查 `output/search-index.json` 是否存在 |
| 图片不显示 | 检查 Markdown 中图片路径是否为 `images/xxx.jpg` |
| 构建报错 | 检查 `pip install -r requirements.txt` 是否运行 |
| 样式异常 | 检查 `output/static/style.css` 是否存在 |
| 中文乱码 | 确保所有 `.md` 文件是 UTF-8 编码 |
