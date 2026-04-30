---
title: Markdown 语法速查 · 写文章都能用到
description: 这个小屋支持的 Markdown 语法全集，发文章时打开这页抄就行。
pubDate: 2026-04-29
tags: [Markdown, 工具]
---

发文章的时候如果忘了语法，对着这篇抄就行 🍊。

## 标题

```markdown
# 一级标题（文章标题已自动生成，正文里别再用）
## 二级标题
### 三级标题
```

## 文字样式

**加粗**、*斜体*、~~删除线~~、`行内代码`。

```markdown
**加粗** *斜体* ~~删除线~~ `行内代码`
```

## 引用

> 这是一个引用块。可以写一些想强调的话，或者别人说过的话。
> 支持多行。

```markdown
> 这是一个引用块。
```

## 列表

### 无序列表

- 第一项
- 第二项
  - 嵌套子项
  - 另一个子项
- 第三项

### 有序列表

1. 先这样
2. 再那样
3. 最后搞定

### 任务清单

- [x] 做完的事
- [ ] 还没做的事

## 链接与图片

[这是一个链接](https://astro.build)

图片放在 `public/` 下，然后：

```markdown
![图片说明](/my-image.png)
```

## 代码块

带语言标记会有语法高亮：

```python
def hello(name):
    print(f"Hello, {name}! 🍊")

hello("纸橙")
```

```javascript
const greet = (name) => `Hello, ${name}! 🍊`;
console.log(greet('纸橙'));
```

## 表格

| 功能 | 支持 | 备注 |
|---|:---:|---|
| 标题 | ✅ | 一到六级 |
| 代码高亮 | ✅ | 几乎所有语言 |
| 数学公式 | ⚠️ | 需要装 remark-math |
| 评论系统 | ⏳ | 后续加 |

## 分隔线

```markdown
---
```

---

## 文章元信息（Frontmatter）

每篇 md 文件开头三条杠之间的部分：

```yaml
---
title: 文章标题          # 必填
description: 一句话描述   # 选填，会显示在卡片上
pubDate: 2026-04-29      # 必填，格式 YYYY-MM-DD
updatedDate: 2026-04-30  # 选填，更新时间
tags: [标签1, 标签2]      # 选填
draft: false             # 选填，设为 true 就不会发布
---
```

## 小技巧

💡 **不想发布但想保存草稿**：加一行 `draft: true`  
💡 **想加 emoji**：直接复制粘贴就行，Markdown 全面支持  
💡 **想嵌 HTML**：Markdown 原生支持 HTML，但建议少用

就这些啦，祝写文章愉快 ✨
