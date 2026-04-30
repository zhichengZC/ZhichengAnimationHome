# 🍊 纸橙的动画小屋

> 一个温馨简约的个人博客，用 Astro 搭建，托管在 GitHub Pages。

**在线地址**：https://zhichengzc.github.io

---

## ✨ 特点

- 🎨 **温馨橙子主题** — 奶油米色 + 暖橙渐变，护眼清新
- ✍️ **Markdown / MDX 写作** — 拖一个 `.md` 文件进 `src/content/posts/` 就能发文
- 🎬 **交互动画** — 首页打字机、滚动入场、浮动图标、渐变标题
- 📱 **完全响应式** — 手机、平板、桌面三端自适应
- 🚀 **一键发布** — 双击 `publish.bat` 自动部署
- 📡 **RSS / 站点地图** — 自动生成，便于订阅与 SEO
- 🔒 **静态站点** — 访问飞快，无服务器成本

---

## 🚀 首次启动（只需做一次）

### 1. 安装 Node.js

去 https://nodejs.org 下载 **LTS 版（20.x 或以上）** 并安装。

### 2. 安装项目依赖

在本文件夹打开终端（右键 → "在终端中打开"），执行：

```bash
npm install
```

### 3. 本地预览

```bash
npm run dev
```

浏览器打开 http://localhost:4321 就能看到小屋了 🍊

---

## 🌐 部署到 GitHub Pages（只需做一次）

### 1. 在 GitHub 创建仓库

- 仓库名必须是：**`zhichengZC.github.io`**（这是 GitHub 用户主页特殊规则）
- 设为 **Public**（这样 Pages 才免费）
- 不要勾选 "Add a README"（本地已有）

### 2. 开启 Pages

进入仓库 → **Settings → Pages** → **Source** 选 **GitHub Actions**（不是 Branch！）

### 3. 关联本地仓库并首次推送

在本文件夹的终端执行：

```bash
git init
git branch -M main
git add -A
git commit -m "init: hello, 纸橙的动画小屋 🍊"
git remote add origin https://github.com/zhichengZC/zhichengZC.github.io.git
git push -u origin main
```

第一次推送后，GitHub Actions 会自动构建并部署，**1–2 分钟**后访问：

👉 **https://zhichengzc.github.io**

---

## ✍️ 日常发文章（超简单）

### 第 1 步：新建一个 md 文件

在 [src/content/posts/](src/content/posts/) 里新建 `我的第一篇文章.md`，内容：

```markdown
---
title: 我的第一篇文章
description: 简短描述，会显示在列表卡片
pubDate: 2026-04-30
tags: [随笔, 动画]
---

# 正文开始

随便写什么，Markdown 所有语法都支持。

- 列表
- **加粗**
- `代码`

\`\`\`python
print("hello")
\`\`\`
```

### 第 2 步：双击 `publish.bat` 一键发布

就这么简单。脚本会：
1. `git add` 所有变更
2. 让你输入更新说明（直接回车用默认时间戳）
3. `git push` 到 GitHub
4. GitHub Actions 自动构建并部署

1–2 分钟后刷新网站就能看到新文章 ✨

---

## 📁 目录说明

```
ZhichengBlog/
├── src/
│   ├── pages/                  # 页面路由（每个文件就是一个 URL）
│   │   ├── index.astro         # 首页
│   │   ├── about.astro         # 关于页
│   │   ├── 404.astro           # 找不到页面
│   │   ├── rss.xml.js          # RSS 订阅
│   │   └── blog/
│   │       ├── index.astro     # 文章列表页
│   │       └── [...slug].astro # 文章详情页（自动生成）
│   ├── content/posts/          # ⭐ 你写的 md/mdx 文章都放这里
│   ├── layouts/                # 页面骨架
│   ├── components/             # 可复用组件（卡片、打字机等）
│   ├── styles/global.css       # 全局样式
│   └── consts.ts               # 站点标题、导航链接
├── public/                     # 图片、favicon 等原样拷贝
├── .github/workflows/deploy.yml # 自动部署配置
├── publish.bat                 # 🚀 一键发布脚本
├── astro.config.mjs            # Astro 配置
└── tailwind.config.mjs         # 主题颜色配置
```

---

## 🎨 想改点什么？

| 想改什么 | 改哪个文件 |
|---|---|
| 站点标题、标语 | [src/consts.ts](src/consts.ts) |
| 顶部导航链接 | [src/consts.ts](src/consts.ts) 中的 `NAV_LINKS` |
| 颜色主题 | [tailwind.config.mjs](tailwind.config.mjs) 中的 `paper`/`ink` |
| 首页打字机文案 | [src/pages/index.astro](src/pages/index.astro) 中的 `Typewriter phrases` |
| 关于页内容 | [src/pages/about.astro](src/pages/about.astro) |
| 页脚版权 | [src/components/Footer.astro](src/components/Footer.astro) |

---

## 🛠️ 常用命令

```bash
npm run dev       # 本地启动（端口 4321）
npm run build     # 构建静态文件到 dist/
npm run preview   # 预览构建结果
```

---

## ❓ 常见问题

**Q: 网站一直显示 404？**  
A: 检查 Settings → Pages 的 Source 是否选了 **GitHub Actions**（不是 Branch）。也要等 Actions 跑完。

**Q: 文章不显示？**  
A: 检查 md 文件头的 `pubDate` 格式是否是 `YYYY-MM-DD`，以及 `draft: true` 的文章不会显示。

**Q: 想加评论系统？**  
A: 推荐用 [Giscus](https://giscus.app)（基于 GitHub Discussions），告诉纸橙我再帮你集成。

---

© 2026 纸橙 🍊 · Made with Astro + ❤️
