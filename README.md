# 📖 家庭说明书集合网站

所有家电、家具、数码产品说明书，一处查阅。

## 🚀 快速开始（只需3步）

### 第1步：准备说明书

1. 用 MinerU 将 PDF 说明书转换成 Markdown
2. 在 `manuals/` 文件夹下按分类创建文件夹，例如：

```
manuals/
├── 厨房电器/
│   └── 美的-微波炉-M1/
│       ├── index.md          ← 说明书内容（Markdown 格式）
│       └── images/           ← 说明书里的图片
│           └── panel.jpg
├── 清洁电器/
├── 家具/
├── 数码产品/
└── 其他/
```

3. 在 `index.md` 文件**最开头**填写基本信息：

```markdown
---
title: 美的微波炉 M1 使用说明书
category: 厨房电器
brand: 美的
type: 微波炉
model: M1-L201B
---

（这里开始是说明书正文内容……）
```

> **字段说明**：
> - `title`：产品标题（会显示在页面顶部）
> - `category`：产品分类（要和文件夹名一致）
> - `brand`：品牌名
> - `type`：产品类型（如"微波炉"、"吸尘器"）
> - `model`：型号（可选）

### 第2步：构建网站

打开终端（命令提示符），进入本项目文件夹，运行：

```bash
pip install -r requirements.txt   # 第一次需要安装依赖
python build.py                   # 构建网站
```

构建完成后，网站文件在 `output/` 文件夹中。

### 第3步：预览网站

用浏览器打开 `output/index.html` 即可预览。

---

## 🌐 部署到线上（GitHub Pages）

### 首次设置

1. 注册一个 [GitHub](https://github.com) 账号
2. 在 GitHub 上创建一个新仓库，命名为 `family-manuals`
3. 将本项目推送到 GitHub：

```bash
git init
git add .
git commit -m "初始化家庭说明书网站"
git branch -M main
git remote add origin https://github.com/你的用户名/family-manuals.git
git push -u origin main
```

4. 在 GitHub 仓库页面 → **Settings** → **Pages** → Source 选择 **GitHub Actions**
5. 推送代码后，GitHub Actions 会自动构建并部署网站
6. 网站地址：`https://你的用户名.github.io/family-manuals/`

### 日常更新

每次添加或修改说明书后：

```bash
python build.py          # 重新构建
git add .
git commit -m "更新说明书"
git push                 # 推送后自动部署
```

---

## 📂 项目结构

```
family-manuals/
├── manuals/                 ← 📁 你的说明书放在这里
│   └── 分类名/
│       └── 产品名/
│           ├── index.md     ← 说明书内容
│           └── images/      ← 说明书图片
├── build.py                 ← 构建脚本
├── template/base.html       ← 网页模板
├── static/                  ← 样式和脚本
├── output/                  ← 生成的网站（自动）
└── .github/workflows/       ← 自动部署配置
```

---

## 🎨 添加新分类

只需在 `manuals/` 下新建一个文件夹即可。构建脚本会自动识别新分类并添加到首页。

分类图标会自动匹配：
- 🍳 厨房电器
- 🧹 清洁电器
- 🪑 家具
- 📱 数码产品
- 🚿 卫浴设备
- 💡 照明电器
- 🌡️ 冷暖电器
- 🔒 安防设备
- 📦 其他（默认图标）

> 如果你的分类不在列表中，可以在 `build.py` 的 `CATEGORY_ICONS` 字典中添加。

---

## ❓ 常见问题

**Q: 搜索功能不工作？**
A: 搜索依赖 `search-index.json` 文件，请确保运行了 `python build.py`，并且用浏览器打开的是 `output/` 下的文件。

**Q: 图片不显示？**
A: 请确保图片放在 `images/` 文件夹中，Markdown 中引用时写 `images/xxx.jpg`（相对路径）。

**Q: Markdown 渲染不对？**
A: 请确保使用标准 Markdown 语法。MinerU 转换的 Markdown 通常可以直接使用。
