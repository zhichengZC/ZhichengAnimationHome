#!/usr/bin/env python3
"""
Blog Toolbox GUI - Modern sidebar navigation design for ZhichengBlog
Features: Upload MD (with images), New Post, Upload Images,
          Edit Site Info, Edit Page Content, Preview, Publish
"""

import os
import sys
import re
import json
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path

# ─── Project Paths ───
BLOG_ROOT = r"e:\ZhichengBlog"
POSTS_DIR = os.path.join(BLOG_ROOT, "src", "content", "posts")
PUBLIC_IMAGES_DIR = os.path.join(BLOG_ROOT, "public", "images")
CONSTS_FILE = os.path.join(BLOG_ROOT, "src", "consts.ts")
ABOUT_FILE = os.path.join(BLOG_ROOT, "src", "pages", "about.astro")
INDEX_FILE = os.path.join(BLOG_ROOT, "src", "pages", "index.astro")
FOOTER_FILE = os.path.join(BLOG_ROOT, "src", "components", "Footer.astro")
SITE_CONFIG_FILE = os.path.join(BLOG_ROOT, "src", "data", "site-config.json")
WORKBUDDY_DIR = r"e:\WorkBuddy\daily-learning"

# ─── Color Palette ───
C = {
    "bg_dark":      "#1a1b2e",   # sidebar bg
    "bg_darker":    "#151626",   # sidebar item hover
    "bg_main":      "#f0ede8",   # main content bg
    "bg_card":      "#ffffff",   # card bg
    "accent":       "#e07a2f",   # primary orange
    "accent_light": "#f5a623",   # lighter orange
    "accent_bg":    "#fef3e8",   # light orange bg for highlights
    "text_white":   "#ffffff",
    "text_light":   "#a0a3bd",   # sidebar secondary text
    "text_dark":    "#2c2c2c",   # main text
    "text_muted":   "#8c8c8c",   # muted text
    "border":       "#e5e1da",   # card border
    "input_bg":     "#f7f5f2",   # input field bg
    "success":      "#34c759",
    "error":        "#ff3b30",
    "log_bg":       "#1e1e2e",
    "log_fg":       "#cdd6f4",
}


# ═══════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def log_output(widget, msg):
    if widget and widget.winfo_exists():
        widget.configure(state="normal")
        widget.insert("end", msg + "\n")
        widget.see("end")
        widget.configure(state="disabled")


def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2]
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",")]
                fm[key.strip()] = items
            else:
                fm[key.strip()] = val
    return fm, body


def build_frontmatter(title, description, pub_date, tags, categories=None, draft=False):
    tag_str = ", ".join(f"{t}" for t in tags) if tags else ""
    cat_str = ", ".join(f"{c}" for c in categories) if categories else ""
    lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        f"pubDate: {pub_date}",
        f"tags: [{tag_str}]",
    ]
    if categories:
        lines.append(f"categories: [{cat_str}]")
    if draft:
        lines.append("draft: true")
    lines.append("---")
    return "\n".join(lines)


def find_images_in_md(content, md_dir):
    images = []
    seen = set()
    for m in re.finditer(r'!\[\[([^\]]+)\]\]', content):
        ref = m.group(1)
        # Try resolving relative to md_dir first
        abs_path = os.path.normpath(os.path.join(md_dir, ref))
        if os.path.isfile(abs_path) and abs_path not in seen:
            images.append((ref, abs_path))
            seen.add(abs_path)
            continue
        # Try just the filename (for Obsidian ![[images/fig.png]] → look in md_dir/images/fig.png)
        filename = os.path.basename(ref)
        abs_path2 = os.path.normpath(os.path.join(md_dir, ref))
        if os.path.isfile(abs_path2) and abs_path2 not in seen:
            images.append((ref, abs_path2))
            seen.add(abs_path2)
            continue
        # Try looking in common subdirectories
        for sub in ["", "images", "attachments", "assets"]:
            candidate = os.path.normpath(os.path.join(md_dir, sub, filename))
            if os.path.isfile(candidate) and candidate not in seen:
                images.append((ref, candidate))
                seen.add(candidate)
                break
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', content):
        alt = m.group(1)
        ref = m.group(2)
        if ref.startswith("http") or ref.startswith("data:"):
            continue
        abs_path = os.path.normpath(os.path.join(md_dir, ref))
        if os.path.isfile(abs_path) and abs_path not in seen:
            images.append((ref, abs_path))
            seen.add(abs_path)
    return images


def convert_obsidian_images(content, slug):
    def obsidian_repl(m):
        ref = m.group(1)
        # Use only the filename part (strip subdirectory like images/)
        filename = os.path.basename(ref)
        name_no_ext = os.path.splitext(filename)[0]
        return f"![{name_no_ext}](/images/{slug}/{filename})"
    result = re.sub(r'!\[\[([^\]]+)\]\]', obsidian_repl, content)
    def standard_repl(m):
        alt = m.group(1)
        ref = m.group(2)
        if ref.startswith("http") or ref.startswith("data:") or ref.startswith("/"):
            return m.group(0)
        filename = os.path.basename(ref)
        return f"![{alt}](/images/{slug}/{filename})"
    result = re.sub(r'!\[([^\]]*)\]\(([^)]+)\]', standard_repl, result)
    return result

def slug_from_title(title):
    slug = re.sub(r'[^\w\s-]', '', title)
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    return slug


def run_command(cmd, cwd=None, log_widget=None):
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd or BLOG_ROOT,
            capture_output=True, text=True, timeout=300,
            encoding='utf-8', errors='replace'
        )
        output = result.stdout + result.stderr
        if log_widget:
            for line in output.splitlines():
                log_output(log_widget, line)
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        if log_widget:
            log_output(log_widget, "[ERROR] Command timed out")
        return False, "Timeout"
    except Exception as e:
        if log_widget:
            log_output(log_widget, f"[ERROR] {e}")
        return False, str(e)


def read_file_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        try:
            with open(path, "r", encoding="gbk") as f:
                return f.read()
        except Exception:
            return None


def write_file_safe(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ═══════════════════════════════════════════════════════════════
# Custom Widgets
# ═══════════════════════════════════════════════════════════════

class SidebarButton(tk.Canvas):
    """A custom sidebar navigation button with hover effects."""
    def __init__(self, parent, text="", icon="", command=None, **kwargs):
        super().__init__(parent, height=44, highlightthickness=0,
                         bg=C["bg_dark"], **kwargs)
        self._text = text
        self._icon = icon
        self._command = command
        self._active = False
        self._hover = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._redraw)

    def set_active(self, active=True):
        self._active = active
        self._redraw()

    def _on_enter(self, e):
        self._hover = True
        self._redraw()

    def _on_leave(self, e):
        self._hover = False
        self._redraw()

    def _on_click(self, e):
        if self._command:
            self._command()

    def _redraw(self, e=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()

        # Background
        if self._active:
            self._draw_active_bg(w, h)
        elif self._hover:
            self.create_rectangle(0, 0, w, h, fill=C["bg_darker"], outline="")

        # Icon + Text
        x_text = 50
        if self._active:
            fill = C["text_white"]
        elif self._hover:
            fill = C["text_white"]
        else:
            fill = C["text_light"]

        self.create_text(24, h // 2, text=self._icon, font=("Segoe UI Emoji", 14),
                         fill=fill, anchor="w")
        self.create_text(x_text, h // 2, text=self._text,
                         font=("Segoe UI", 11), fill=fill, anchor="w")

    def _draw_active_bg(self, w, h):
        # Active indicator bar on the left
        self.create_rectangle(0, 0, w, h, fill=C["bg_darker"], outline="")
        self.create_rectangle(0, 8, 4, h - 8, fill=C["accent"], outline="")
        # Subtle gradient-like effect
        self.create_rectangle(4, 0, w, h, fill=C["bg_darker"], outline="")


class ActionButton(tk.Canvas):
    """A modern rounded button with hover effects."""
    def __init__(self, parent, text="", command=None, primary=True, **kwargs):
        bg = kwargs.pop("bg", C["bg_card"])
        super().__init__(parent, height=38, highlightthickness=0, bg=bg, **kwargs)
        self._text = text
        self._command = command
        self._primary = primary
        self._hover = False
        self._bg = bg

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._redraw)

    def _on_enter(self, e):
        self._hover = True
        self._redraw()

    def _on_leave(self, e):
        self._hover = False
        self._redraw()

    def _on_click(self, e):
        if self._command:
            self._command()

    def _redraw(self, e=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = 8  # border radius

        if self._primary:
            if self._hover:
                bg = C["accent_light"]
            else:
                bg = C["accent"]
            fg = C["text_white"]
        else:
            bg = C["input_bg"] if not self._hover else C["border"]
            fg = C["text_dark"]

        # Rounded rectangle
        self._round_rect(2, 2, w - 2, h - 2, r, fill=bg, outline="")
        self.create_text(w // 2, h // 2, text=self._text,
                         font=("Segoe UI", 10, "bold"), fill=fg)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class FormField(tk.Frame):
    """A form field with label and entry on a card background."""
    def __init__(self, parent, label="", placeholder="", width=40, **kwargs):
        bg = kwargs.pop("bg", C["bg_card"])
        super().__init__(parent, bg=bg, **kwargs)
        self._bg = bg

        lbl = tk.Label(self, text=label, font=("Segoe UI", 10),
                       bg=bg, fg=C["text_muted"], anchor="w", width=10)
        lbl.pack(side="left", padx=(0, 8))

        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self, textvariable=self.var, font=("Segoe UI", 10),
            bg=C["input_bg"], fg=C["text_dark"],
            relief="flat", bd=0, highlightthickness=1,
            highlightcolor=C["accent"], highlightbackground=C["border"],
            insertbackground=C["text_dark"]
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)

        if placeholder:
            self.entry.insert(0, placeholder)


class LogPanel(tk.Frame):
    """Dark-themed log output panel."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C["log_bg"], bd=0, **kwargs)
        self.text = tk.Text(
            self, wrap="word", font=("Cascadia Code", 9),
            bg=C["log_bg"], fg=C["log_fg"],
            insertbackground=C["log_fg"], state="disabled",
            relief="flat", bd=0, padx=12, pady=8,
            selectbackground="#45475a"
        )
        scrollbar = tk.Scrollbar(self, command=self.text.yview,
                                 bg=C["log_bg"], troughcolor=C["log_bg"],
                                 activebackground=C["accent"])
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

    def append(self, msg):
        log_output(self.text, msg)

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════
# Flow Layout Frame - auto-wraps child widgets
# ═══════════════════════════════════════════════════════════════

class _FlowFrame(tk.Frame):
    """A Frame that arranges its children in a flow layout (auto-wrap)."""

    def __init__(self, parent, **kw):
        kw.setdefault("bg", C["bg_card"])
        super().__init__(parent, **kw)
        self._reflow_scheduled = False
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event=None):
        """Schedule a reflow on resize (debounced)."""
        if not self._reflow_scheduled:
            self._reflow_scheduled = True
            self.after(100, self._do_reflow)

    def _do_reflow(self):
        self._reflow_scheduled = False
        self.reflow()

    def reflow(self):
        """Re-arrange all children in flow layout using grid."""
        children = self.winfo_children()
        # Remove all children from current grid positions
        for child in children:
            child.grid_forget()

        if not children:
            return

        frame_width = self.winfo_width()
        if frame_width <= 1:
            # Widget not yet rendered, schedule a retry
            self.after(50, self.reflow)
            return

        col = 0
        row = 0
        x_offset = 0

        for child in children:
            child.update_idletasks()
            w = child.winfo_reqwidth()
            h = child.winfo_reqheight()

            if x_offset + w > frame_width and col > 0:
                col = 0
                row += 1
                x_offset = 0

            child.grid(row=row, column=col, padx=2, pady=1, sticky="w")
            x_offset += w + 4
            col += 1


# ═══════════════════════════════════════════════════════════════
# Main Application
# ═══════════════════════════════════════════════════════════════

class BlogToolbox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("纸橙博客工具箱")
        self.geometry("1280x800")
        self.minsize(1100, 750)
        self.configure(bg=C["bg_main"])

        # Remove default title bar decorations on Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self._dev_process = None
        self._nav_buttons = []
        self._current_page = None
        self._pages = {}

        self._build_layout()

    # ─── Main Layout ───
    def _build_layout(self):
        # ── Sidebar ──
        self.sidebar = tk.Frame(self, bg=C["bg_dark"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar header (branding)
        header = tk.Frame(self.sidebar, bg=C["bg_dark"])
        header.pack(fill="x", padx=20, pady=(24, 8))
        tk.Label(header, text="🍊", font=("Segoe UI Emoji", 22),
                 bg=C["bg_dark"], fg=C["accent"]).pack(side="left")
        tk.Label(header, text="纸橙博客", font=("Segoe UI", 16, "bold"),
                 bg=C["bg_dark"], fg=C["text_white"]).pack(side="left", padx=(8, 0))

        # Separator
        tk.Frame(self.sidebar, bg="#2a2b40", height=1).pack(fill="x", padx=16, pady=(12, 8))

        # Navigation buttons
        nav_items = [
            ("📄", "上传文章", "upload"),
            ("✏️", "新建文章", "newpost"),
            ("🖼️", "上传图片", "images"),
            ("🗑️", "管理文章", "manage"),
            ("⚙️", "网站信息", "siteinfo"),
            ("📝", "页面内容", "editpage"),
            ("👁️", "本地预览", "preview"),
            ("🚀", "一键发布", "publish"),
        ]

        for icon, text, key in nav_items:
            btn = SidebarButton(self.sidebar, text=text, icon=icon,
                                command=lambda k=key: self._show_page(k))
            btn.pack(fill="x", padx=8, pady=2)
            self._nav_buttons.append((key, btn))

        # Sidebar footer
        footer = tk.Frame(self.sidebar, bg=C["bg_dark"])
        footer.pack(side="bottom", fill="x", padx=16, pady=16)
        tk.Label(footer, text="ZhichengBlog Manager",
                 font=("Segoe UI", 8), bg=C["bg_dark"],
                 fg="#4a4b60").pack()

        # ── Main Content Area ──
        self.main_area = tk.Frame(self, bg=C["bg_main"])
        self.main_area.pack(side="right", fill="both", expand=True)

        # Page container
        self.page_container = tk.Frame(self.main_area, bg=C["bg_main"])
        self.page_container.pack(fill="both", expand=True, padx=24, pady=20)

        # Build all pages
        self._build_upload_page()
        self._build_newpost_page()
        self._build_images_page()
        self._build_manage_page()
        self._build_siteinfo_page()
        self._build_editpage_page()
        self._build_preview_page()
        self._build_publish_page()

        # Show default page
        self._show_page("upload")

    def _show_page(self, key):
        """Switch to a page and update sidebar active state."""
        for k, btn in self._nav_buttons:
            btn.set_active(k == key)
        for k, frame in self._pages.items():
            if k == key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
        self._current_page = key

    def _create_page(self, key):
        """Create a page frame in the container."""
        page = tk.Frame(self.page_container, bg=C["bg_main"])
        self._pages[key] = page
        return page

    def _section_title(self, parent, title, subtitle=""):
        """Create a section title with optional subtitle."""
        frame = tk.Frame(parent, bg=C["bg_main"])
        frame.pack(fill="x", pady=(0, 16))
        tk.Label(frame, text=title, font=("Segoe UI", 20, "bold"),
                 bg=C["bg_main"], fg=C["text_dark"]).pack(anchor="w")
        if subtitle:
            tk.Label(frame, text=subtitle, font=("Segoe UI", 10),
                     bg=C["bg_main"], fg=C["text_muted"]).pack(anchor="w", pady=(4, 0))
        return frame

    def _card(self, parent, **kwargs):
        """Create a white card frame."""
        card = tk.Frame(parent, bg=C["bg_card"], highlightbackground=C["border"],
                        highlightthickness=1, **kwargs)
        return card

    def _form_row(self, parent, label, var, width=None, combobox_vals=None):
        """Create a labeled form row inside a card."""
        row = tk.Frame(parent, bg=C["bg_card"])
        row.pack(fill="x", pady=6)

        tk.Label(row, text=label, font=("Segoe UI", 10),
                 bg=C["bg_card"], fg=C["text_muted"], width=10,
                 anchor="w").pack(side="left", padx=(0, 12))

        if combobox_vals is not None:
            widget = ttk.Combobox(row, textvariable=var, values=combobox_vals,
                                  font=("Segoe UI", 10), state="readonly")
        else:
            widget = tk.Entry(row, textvariable=var, font=("Segoe UI", 10),
                              bg=C["input_bg"], fg=C["text_dark"],
                              relief="flat", bd=0, highlightthickness=1,
                              highlightcolor=C["accent"], highlightbackground=C["border"],
                              insertbackground=C["text_dark"])

        widget.pack(side="left", fill="x", expand=True, ipady=6)
        if width:
            widget.configure(width=width)
        return widget

    def _checkbox(self, parent, text, var):
        """Create a styled checkbox."""
        cb = tk.Checkbutton(parent, text=text, variable=var,
                            font=("Segoe UI", 10), bg=C["bg_card"],
                            fg=C["text_dark"], selectcolor=C["input_bg"],
                            activebackground=C["bg_card"], activeforeground=C["text_dark"],
                            highlightthickness=0)
        cb.pack(side="left", padx=(0, 20))
        return cb

    def _button_row(self, parent):
        """Create a row for action buttons."""
        row = tk.Frame(parent, bg=C["bg_card"])
        row.pack(fill="x", pady=(16, 0))
        return row

    def _add_btn(self, parent, text, command, primary=True):
        """Add an ActionButton to a row."""
        btn = ActionButton(parent, text=text, command=command, primary=primary,
                           bg=C["bg_card"])
        btn.pack(side="left", padx=(0, 10))
        # Set min width
        btn.update_idletasks()
        btn.configure(width=max(120, len(text) * 12 + 40))
        return btn

    def _add_log(self, parent):
        """Add a log panel to the page."""
        log = LogPanel(parent)
        log.pack(fill="both", expand=True, pady=(16, 0))
        return log

    def _run_in_thread(self, func, *args):
        t = threading.Thread(target=func, args=args, daemon=True)
        t.start()

    def _get_all_tags(self):
        """Get all unique tags from existing posts."""
        tags = set()
        if os.path.isdir(POSTS_DIR):
            for f in os.listdir(POSTS_DIR):
                if f.endswith(".md"):
                    fp = os.path.join(POSTS_DIR, f)
                    content = read_file_safe(fp)
                    if content:
                        fm, _ = parse_frontmatter(content)
                        post_tags = fm.get("tags", [])
                        if isinstance(post_tags, list):
                            for t in post_tags:
                                if isinstance(t, str) and t.strip():
                                    tags.add(t.strip())
        return sorted(tags)

    def _get_all_categories(self):
        """Get all unique categories from existing posts."""
        cats = set()
        if os.path.isdir(POSTS_DIR):
            for f in os.listdir(POSTS_DIR):
                if f.endswith(".md"):
                    fp = os.path.join(POSTS_DIR, f)
                    content = read_file_safe(fp)
                    if content:
                        fm, _ = parse_frontmatter(content)
                        post_cats = fm.get("categories", [])
                        if isinstance(post_cats, list):
                            for c in post_cats:
                                if isinstance(c, str) and c.strip():
                                    cats.add(c.strip())
        return sorted(cats)

    def _get_all_posts(self):
        """Get all posts with their metadata."""
        posts = []
        if os.path.isdir(POSTS_DIR):
            for f in sorted(os.listdir(POSTS_DIR), reverse=True):
                if f.endswith(".md"):
                    fp = os.path.join(POSTS_DIR, f)
                    content = read_file_safe(fp)
                    if content:
                        fm, _ = parse_frontmatter(content)
                        posts.append({
                            "filename": f,
                            "path": fp,
                            "title": fm.get("title", f[:-3]),
                            "description": fm.get("description", ""),
                            "pubDate": fm.get("pubDate", ""),
                            "tags": fm.get("tags", []),
                            "draft": fm.get("draft", False),
                        })
        return posts

    def _get_current_tags(self, tags_var):
        text = tags_var.get().strip()
        if not text:
            return []
        return [t.strip() for t in text.split(",") if t.strip()]

    def _toggle_tag(self, tag, tags_var, cloud_frame):
        current = self._get_current_tags(tags_var)
        if tag in current:
            current.remove(tag)
        else:
            current.append(tag)
        tags_var.set(", ".join(current))
        self._refresh_tag_cloud(cloud_frame, tags_var)

    def _refresh_tag_cloud(self, cloud_frame, tags_var):
        for w in cloud_frame.winfo_children():
            w.destroy()
        all_tags = self._get_all_tags()
        current = self._get_current_tags(tags_var)
        # Merge custom tags from the input field into the cloud
        for t in current:
            if t not in all_tags:
                all_tags.append(t)
        all_tags = sorted(all_tags)
        if not all_tags:
            tk.Label(cloud_frame, text="暂无已有标签（首次使用请手动输入）",
                     font=("Segoe UI", 9), bg=C["bg_card"],
                     fg=C["text_muted"]).grid(row=0, column=0, sticky="w")
            return
        row, col, x_off = 0, 0, 0
        frame_w = cloud_frame.winfo_width() or 600
        for tag in all_tags:
            is_selected = tag in current
            is_custom = tag not in self._get_all_tags()
            bg = C["accent_bg"] if is_selected else C["input_bg"]
            fg = C["accent"] if is_selected else C["text_dark"]
            chip = tk.Label(cloud_frame, text=tag, font=("Segoe UI", 9),
                           bg=bg, fg=fg, cursor="hand2", padx=8, pady=3)
            chip.grid(row=row, column=col, padx=2, pady=1, sticky="w")
            chip.update_idletasks()
            x_off += chip.winfo_reqwidth() + 4
            col += 1
            if x_off > frame_w and col > 1:
                row += 1
                col = 0
                x_off = 0
            chip.bind("<Button-1>",
                      lambda e, t=tag: self._toggle_tag(t, tags_var, cloud_frame))

    def _build_tag_cloud_area(self, parent, tags_var):
        """Build a tag cloud area with existing tags as clickable chips."""
        container = tk.Frame(parent, bg=C["bg_card"])
        container.pack(fill="x", pady=(2, 0))
        tk.Label(container, text="", bg=C["bg_card"], width=10).pack(side="left", padx=(0, 12))
        chips_inner = _FlowFrame(container, bg=C["bg_card"])
        chips_inner.pack(side="left", fill="x", expand=True)
        self._refresh_tag_cloud(chips_inner, tags_var)
        return chips_inner

    def _build_cat_cloud_area(self, parent, cats_var):
        """Build a category cloud area with existing categories as clickable chips."""
        container = tk.Frame(parent, bg=C["bg_card"])
        container.pack(fill="x", pady=(2, 0))
        tk.Label(container, text="", bg=C["bg_card"], width=10).pack(side="left", padx=(0, 12))
        chips_inner = _FlowFrame(container, bg=C["bg_card"])
        chips_inner.pack(side="left", fill="x", expand=True)
        self._refresh_cat_cloud(chips_inner, cats_var)
        return chips_inner

    def _refresh_cat_cloud(self, cloud_frame, cats_var):
        for w in cloud_frame.winfo_children():
            w.destroy()
        all_cats = self._get_all_categories()
        current = self._get_current_categories(cats_var)
        # Merge custom categories from the input field
        for c in current:
            if c not in all_cats:
                all_cats.append(c)
        # Always include "其他" as a default option
        if "其他" not in all_cats:
            all_cats.append("其他")
        all_cats = sorted(all_cats, key=lambda x: (x == "其他", x))
        if not all_cats:
            tk.Label(cloud_frame, text="暂无已有分类",
                     font=("Segoe UI", 9), bg=C["bg_card"],
                     fg=C["text_muted"]).grid(row=0, column=0, sticky="w")
            return
        row, col, x_off = 0, 0, 0
        frame_w = cloud_frame.winfo_width() or 600
        for cat in all_cats:
            is_selected = cat in current
            is_other = cat == "其他"
            bg = C["accent_bg"] if is_selected else C["input_bg"]
            fg = C["accent"] if is_selected else (C["text_muted"] if is_other else C["text_dark"])
            chip = tk.Label(cloud_frame, text=cat, font=("Segoe UI", 9),
                           bg=bg, fg=fg, cursor="hand2", padx=8, pady=3)
            chip.grid(row=row, column=col, padx=2, pady=1, sticky="w")
            chip.update_idletasks()
            x_off += chip.winfo_reqwidth() + 4
            col += 1
            if x_off > frame_w and col > 1:
                row += 1
                col = 0
                x_off = 0
            chip.bind("<Button-1>",
                      lambda e, c=cat: self._toggle_category(c, cats_var, cloud_frame))

    def _get_current_categories(self, cats_var):
        text = cats_var.get().strip()
        if not text:
            return []
        return [c.strip() for c in text.split(",") if c.strip()]

    def _toggle_category(self, cat, cats_var, cloud_frame):
        current = self._get_current_categories(cats_var)
        if cat in current:
            current.remove(cat)
        else:
            current.append(cat)
        cats_var.set(", ".join(current))
        self._refresh_cat_cloud(cloud_frame, cats_var)

    def _add_social_row(self, parent, label="", href="", handle=""):
        """Add a row of social/contact entry fields."""
        row = tk.Frame(parent, bg=C["bg_card"])
        row.pack(fill="x", pady=2)

        tk.Label(row, text="标签", font=("Segoe UI", 9),
                 bg=C["bg_card"], fg=C["text_muted"], width=4,
                 anchor="w").pack(side="left", padx=(0, 4))
        label_var = tk.StringVar(value=label)
        label_entry = tk.Entry(row, textvariable=label_var, font=("Segoe UI", 9),
                               bg=C["input_bg"], fg=C["text_dark"],
                               relief="flat", bd=0, highlightthickness=1,
                               highlightcolor=C["accent"], highlightbackground=C["border"],
                               insertbackground=C["text_dark"], width=10)
        label_entry.pack(side="left", padx=(0, 8), ipady=4)

        tk.Label(row, text="链接", font=("Segoe UI", 9),
                 bg=C["bg_card"], fg=C["text_muted"], width=4,
                 anchor="w").pack(side="left", padx=(0, 4))
        href_var = tk.StringVar(value=href)
        href_entry = tk.Entry(row, textvariable=href_var, font=("Segoe UI", 9),
                              bg=C["input_bg"], fg=C["text_dark"],
                              relief="flat", bd=0, highlightthickness=1,
                              highlightcolor=C["accent"], highlightbackground=C["border"],
                              insertbackground=C["text_dark"], width=22)
        href_entry.pack(side="left", padx=(0, 8), ipady=4)

        tk.Label(row, text="显示", font=("Segoe UI", 9),
                 bg=C["bg_card"], fg=C["text_muted"], width=4,
                 anchor="w").pack(side="left", padx=(0, 4))
        handle_var = tk.StringVar(value=handle)
        handle_entry = tk.Entry(row, textvariable=handle_var, font=("Segoe UI", 9),
                                bg=C["input_bg"], fg=C["text_dark"],
                                relief="flat", bd=0, highlightthickness=1,
                                highlightcolor=C["accent"], highlightbackground=C["border"],
                                insertbackground=C["text_dark"], width=12)
        handle_entry.pack(side="left", ipady=4)

        self.si_social_entries.append({"label_var": label_var, "href_var": href_var,
                                       "handle_var": handle_var, "row_frame": row})

    def _remove_last_social_row(self, parent):
        """Remove the last social/contact entry row."""
        if self.si_social_entries:
            entry = self.si_social_entries.pop()
            entry["row_frame"].destroy()

    # ═════════════════════════════════════════════════════════════
    # Page 1: Upload MD File    # ═══════════════════════════════════════════════════════════
    def _build_upload_page(self):
        page = self._create_page("upload")
        self._section_title(page, "上传文章",
                            "将已有的 Markdown 文件连同引用图片一起上传到博客")

        # Card
        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # File selection row
        file_row = tk.Frame(inner, bg=C["bg_card"])
        file_row.pack(fill="x", pady=(0, 8))

        tk.Label(file_row, text="MD 文件", font=("Segoe UI", 10),
                 bg=C["bg_card"], fg=C["text_muted"], width=10,
                 anchor="w").pack(side="left", padx=(0, 12))

        self.upload_path_var = tk.StringVar()
        path_entry = tk.Entry(file_row, textvariable=self.upload_path_var,
                              font=("Segoe UI", 10),
                              bg=C["input_bg"], fg=C["text_dark"],
                              relief="flat", bd=0, highlightthickness=1,
                              highlightcolor=C["accent"], highlightbackground=C["border"],
                              insertbackground=C["text_dark"])
        path_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        ActionButton(file_row, text="浏览...", command=self._browse_md,
                     primary=False, bg=C["bg_card"]).pack(side="left", padx=(0, 6))
        ActionButton(file_row, text="WorkBuddy", command=self._browse_workbuddy,
                     primary=False, bg=C["bg_card"]).pack(side="left")

        # Fix button widths
        for w in file_row.winfo_children():
            if isinstance(w, ActionButton):
                w.configure(width=90 if w._text == "浏览..." else 100)

        # Form fields
        self.upload_slug_var = tk.StringVar()
        self._form_row(inner, "URL Slug", self.upload_slug_var)

        self.upload_desc_var = tk.StringVar()
        self._form_row(inner, "描述", self.upload_desc_var)

        self.upload_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self._form_row(inner, "发布日期", self.upload_date_var, width=20)

        self.upload_tags_var = tk.StringVar()
        self._form_row(inner, "标签", self.upload_tags_var)
        self.upload_tag_cloud = self._build_tag_cloud_area(inner, self.upload_tags_var)
        # Auto-refresh tag cloud when user types custom tags
        self.upload_tags_var.trace_add("write", lambda *_: self._refresh_tag_cloud(
            self.upload_tag_cloud, self.upload_tags_var))
        # Tag hint
        tags_hint = tk.Frame(inner, bg=C["bg_card"])
        tags_hint.pack(fill="x")
        tk.Label(tags_hint, text="", bg=C["bg_card"], width=10).pack(side="left")
        tk.Label(tags_hint, text="多个标签用英文逗号分隔，点击上方标签可快速选择",
                 font=("Segoe UI", 9), bg=C["bg_card"], fg=C["text_muted"]).pack(side="left")

        # Categories
        self.upload_cats_var = tk.StringVar()
        self._form_row(inner, "分类", self.upload_cats_var)
        self.upload_cat_cloud = self._build_cat_cloud_area(inner, self.upload_cats_var)
        # Category hint
        cat_hint = tk.Frame(inner, bg=C["bg_card"])
        cat_hint.pack(fill="x")
        tk.Label(cat_hint, text="", bg=C["bg_card"], width=10).pack(side="left")
        tk.Label(cat_hint, text="多个分类用英文逗号分隔，未分类将默认为「其他」",
                 font=("Segoe UI", 9), bg=C["bg_card"], fg=C["text_muted"]).pack(side="left")

        # Options
        opt_row = tk.Frame(inner, bg=C["bg_card"])
        opt_row.pack(fill="x", pady=(8, 0))

        self.upload_images_var = tk.BooleanVar(value=True)
        self._checkbox(opt_row, "自动上传引用图片", self.upload_images_var)

        self.upload_convert_var = tk.BooleanVar(value=True)
        self._checkbox(opt_row, "转换 Obsidian 图片语法", self.upload_convert_var)

        self.upload_override_fm_var = tk.BooleanVar(value=False)
        self._checkbox(opt_row, "覆盖原 Frontmatter", self.upload_override_fm_var)

        # Buttons
        btn_row = self._button_row(inner)
        self._add_btn(btn_row, "📋 预览检查", self._preview_upload, primary=False)
        self._add_btn(btn_row, "🚀 上传到博客", self._do_upload, primary=True)

        # Log
        self.upload_log = self._add_log(inner)

    def _browse_md(self):
        path = filedialog.askopenfilename(
            title="选择 Markdown 文件",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")]
        )
        if path:
            self.upload_path_var.set(path)
            self._auto_fill_upload_fields(path)

    def _browse_workbuddy(self):
        path = filedialog.askopenfilename(
            title="从 WorkBuddy 选择",
            initialdir=WORKBUDDY_DIR,
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")]
        )
        if path:
            self.upload_path_var.set(path)
            self._auto_fill_upload_fields(path)

    def _auto_fill_upload_fields(self, path):
        basename = os.path.splitext(os.path.basename(path))[0]
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', basename)
        if date_match:
            self.upload_date_var.set(date_match.group(1))
            slug_part = basename[10:].lstrip("-")
            self.upload_slug_var.set(slug_part if slug_part else basename)
        else:
            self.upload_slug_var.set(slug_from_title(basename))
        # Try to extract description and tags from frontmatter
        content = read_file_safe(path)
        if content:
            fm, _ = parse_frontmatter(content)
            if fm.get("description"):
                self.upload_desc_var.set(fm["description"])
            else:
                self.upload_desc_var.set("")
            if fm.get("tags"):
                tags = fm["tags"]
                if isinstance(tags, list):
                    self.upload_tags_var.set(", ".join(tags))
                else:
                    self.upload_tags_var.set(str(tags))
            else:
                self.upload_tags_var.set("")
            # Refresh tag cloud
            if hasattr(self, 'upload_tag_cloud'):
                self._refresh_tag_cloud(self.upload_tag_cloud, self.upload_tags_var)
            # Load categories from frontmatter
            if fm.get("categories"):
                cats = fm["categories"]
                if isinstance(cats, list):
                    self.upload_cats_var.set(", ".join(cats))
                else:
                    self.upload_cats_var.set(str(cats))
            else:
                self.upload_cats_var.set("")
            # Refresh category cloud
            if hasattr(self, 'upload_cat_cloud'):
                self._refresh_cat_cloud(self.upload_cat_cloud, self.upload_cats_var)

    def _preview_upload(self):
        path = self.upload_path_var.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning("提示", "请先选择一个有效的 MD 文件")
            return
        self.upload_log.clear()
        content = read_file_safe(path)
        if content is None:
            self.upload_log.append("[ERROR] 无法读取文件")
            return
        md_dir = os.path.dirname(os.path.abspath(path))
        fm, body = parse_frontmatter(content)
        images = find_images_in_md(content, md_dir)
        self.upload_log.append(f"📄 文件: {os.path.basename(path)}")
        self.upload_log.append(f"📏 大小: {len(content)} 字符")
        self.upload_log.append("")
        if fm:
            self.upload_log.append("📋 Frontmatter:")
            for k, v in fm.items():
                self.upload_log.append(f"   {k}: {v}")
        else:
            self.upload_log.append("📋 未检测到 Frontmatter（将自动生成）")
        self.upload_log.append(f"\n🖼️ 发现 {len(images)} 个图片引用:")
        for ref, abs_path in images:
            size_kb = os.path.getsize(abs_path) / 1024
            mark = "✅" if os.path.isfile(abs_path) else "❌"
            self.upload_log.append(f"   {mark} {ref} ({size_kb:.0f} KB)")
        if not images:
            self.upload_log.append("   （无图片引用）")
        slug = self.upload_slug_var.get().strip()
        if self.upload_convert_var.get() and images:
            self.upload_log.append(f"\n🔄 图片将转换为: /images/{slug}/<filename>")

    def _do_upload(self):
        path = self.upload_path_var.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning("提示", "请先选择一个有效的 MD 文件")
            return
        slug = self.upload_slug_var.get().strip()
        if not slug:
            messagebox.showwarning("提示", "请填写 URL Slug")
            return
        self._run_in_thread(self._upload_worker, path, slug)

    def _upload_worker(self, path, slug):
        log = self.upload_log
        log.clear()
        content = read_file_safe(path)
        if content is None:
            log.append("[ERROR] 无法读取文件")
            return
        md_dir = os.path.dirname(os.path.abspath(path))
        pub_date = self.upload_date_var.get().strip()

        fm, body = parse_frontmatter(content)
        if self.upload_override_fm_var.get() or not fm:
            title = fm.get("title", slug.replace("-", " "))
            # Use GUI fields, fallback to frontmatter values
            description = self.upload_desc_var.get().strip() or fm.get("description", "")
            tags_text = self.upload_tags_var.get().strip()
            if tags_text:
                tags = [t.strip() for t in tags_text.split(",") if t.strip()]
            else:
                tags = fm.get("tags", [])
            cats_text = self.upload_cats_var.get().strip()
            if cats_text:
                categories = [c.strip() for c in cats_text.split(",") if c.strip()]
            else:
                categories = fm.get("categories", [])
            if not categories:
                categories = ["其他"]
            new_fm = build_frontmatter(title, description, pub_date, tags, categories)
            final_content = new_fm + "\n" + body
            log.append("✅ Frontmatter 已生成/覆盖")
        else:
            final_content = content
            log.append("✅ 保留原 Frontmatter")

        if self.upload_convert_var.get():
            final_content = convert_obsidian_images(final_content, slug)
            log.append("✅ 图片引用已转换为博客格式")

        if self.upload_images_var.get():
            images = find_images_in_md(content, md_dir)
            img_dest_dir = os.path.join(PUBLIC_IMAGES_DIR, slug)
            copied = 0
            for ref, abs_path in images:
                filename = os.path.basename(abs_path)
                dest = os.path.join(img_dest_dir, filename)
                ensure_dir(img_dest_dir)
                try:
                    shutil.copy2(abs_path, dest)
                    copied += 1
                    log.append(f"  📎 {ref} → public/images/{slug}/{filename}")
                except Exception as e:
                    log.append(f"  ❌ {filename}: {e}")
            log.append(f"✅ 已复制 {copied}/{len(images)} 个图片")
        else:
            log.append("⏭️ 跳过图片上传")

        dest_filename = f"{pub_date}-{slug}.md"
        dest_path = os.path.join(POSTS_DIR, dest_filename)
        try:
            write_file_safe(dest_path, final_content)
            log.append(f"✅ 文章已保存: src/content/posts/{dest_filename}")
        except Exception as e:
            log.append(f"❌ 保存失败: {e}")
            return
        log.append("")
        log.append("🎉 上传完成！使用「本地预览」查看效果，或「一键发布」部署。")

    # ═══════════════════════════════════════════════════════════
    # Page 2: New Post
    # ═══════════════════════════════════════════════════════════
    def _build_newpost_page(self):
        page = self._create_page("newpost")
        self._section_title(page, "新建文章", "创建一篇新的博客文章")

        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        self.np_title_var = tk.StringVar()
        self._form_row(inner, "标题", self.np_title_var)

        self.np_desc_var = tk.StringVar()
        self._form_row(inner, "描述", self.np_desc_var)

        self.np_slug_var = tk.StringVar()
        self._form_row(inner, "URL Slug", self.np_slug_var)

        self.np_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self._form_row(inner, "发布日期", self.np_date_var, width=20)

        self.np_tags_var = tk.StringVar()
        tags_row = self._form_row(inner, "标签", self.np_tags_var)

        # Tag cloud
        self.np_tag_cloud = self._build_tag_cloud_area(inner, self.np_tags_var)

        # Auto-refresh tag cloud when user types custom tags
        self.np_tags_var.trace_add("write", lambda *_: self._refresh_tag_cloud(
            self.np_tag_cloud, self.np_tags_var))

        # Hint for tags
        hint_row = tk.Frame(inner, bg=C["bg_card"])
        hint_row.pack(fill="x")
        tk.Label(hint_row, text="", bg=C["bg_card"], width=10).pack(side="left")
        tk.Label(hint_row, text="多个标签用英文逗号分隔，点击上方标签可快速选择", font=("Segoe UI", 9),
                 bg=C["bg_card"], fg=C["text_muted"]).pack(side="left")

        # Categories
        self.np_cats_var = tk.StringVar()
        self._form_row(inner, "分类", self.np_cats_var)
        self.np_cat_cloud = self._build_cat_cloud_area(inner, self.np_cats_var)
        # Category hint
        cat_hint = tk.Frame(inner, bg=C["bg_card"])
        cat_hint.pack(fill="x")
        tk.Label(cat_hint, text="", bg=C["bg_card"], width=10).pack(side="left")
        tk.Label(cat_hint, text="多个分类用英文逗号分隔，未分类将默认为「其他」",
                 font=("Segoe UI", 9), bg=C["bg_card"], fg=C["text_muted"]).pack(side="left")

        self.np_draft_var = tk.BooleanVar(value=True)
        opt_row = tk.Frame(inner, bg=C["bg_card"])
        opt_row.pack(fill="x", pady=(8, 0))
        self._checkbox(opt_row, "标记为草稿（不会在网站显示）", self.np_draft_var)

        self.np_title_var.trace_add("write", self._auto_slug_from_title)

        btn_row = self._button_row(inner)
        self._add_btn(btn_row, "🆕 创建文章", self._create_new_post)
        self._add_btn(btn_row, "📂 打开文章目录", self._open_posts_dir, primary=False)

        self.newpost_log = self._add_log(inner)

    def _auto_slug_from_title(self, *args):
        self.np_slug_var.set(slug_from_title(self.np_title_var.get()))

    def _create_new_post(self):
        title = self.np_title_var.get().strip()
        if not title:
            messagebox.showwarning("提示", "请输入文章标题")
            return
        slug = self.np_slug_var.get().strip() or slug_from_title(title)
        desc = self.np_desc_var.get().strip()
        pub_date = self.np_date_var.get().strip()
        tags_str = self.np_tags_var.get().strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        cats_str = self.np_cats_var.get().strip()
        categories = [c.strip() for c in cats_str.split(",") if c.strip()] if cats_str else []
        if not categories:
            categories = ["其他"]
        draft = self.np_draft_var.get()

        fm = build_frontmatter(title, desc, pub_date, tags, categories, draft)
        content = fm + f"\n# {title}\n\n开始写你的文章...\n"

        filename = f"{pub_date}-{slug}.md"
        filepath = os.path.join(POSTS_DIR, filename)
        if os.path.exists(filepath):
            if not messagebox.askyesno("文件已存在", f"{filename} 已存在，是否覆盖？"):
                return
        try:
            write_file_safe(filepath, content)
            self.newpost_log.append(f"✅ 已创建: src/content/posts/{filename}")
            self.newpost_log.append(f"   标题: {title} | 草稿: {'是' if draft else '否'}")
            if messagebox.askyesno("提示", "文章已创建！是否打开编辑？"):
                os.startfile(filepath)
        except Exception as e:
            self.newpost_log.append(f"❌ 创建失败: {e}")

    def _open_posts_dir(self):
        os.startfile(POSTS_DIR)

    # ═══════════════════════════════════════════════════════════
    # Page 3: Upload Images
    # ═══════════════════════════════════════════════════════════
    def _build_images_page(self):
        page = self._create_page("images")
        self._section_title(page, "上传图片", "上传图片文件到博客的公共资源目录")

        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Slug
        self.img_slug_var = tk.StringVar()
        slug_row = tk.Frame(inner, bg=C["bg_card"])
        slug_row.pack(fill="x", pady=(0, 8))
        tk.Label(slug_row, text="目标文章", font=("Segoe UI", 10),
                 bg=C["bg_card"], fg=C["text_muted"], width=10,
                 anchor="w").pack(side="left", padx=(0, 12))
        self.img_slug_cb = ttk.Combobox(slug_row, textvariable=self.img_slug_var,
                                         font=("Segoe UI", 10))
        self.img_slug_cb.pack(side="left", fill="x", expand=True, ipady=4)
        self._refresh_post_slugs()
        self.img_slug_cb.bind("<ButtonPress>", lambda e: self._refresh_post_slugs())

        # File selection
        file_row = tk.Frame(inner, bg=C["bg_card"])
        file_row.pack(fill="x", pady=6)

        tk.Label(file_row, text="图片文件", font=("Segoe UI", 10),
                 bg=C["bg_card"], fg=C["text_muted"], width=10,
                 anchor="w").pack(side="left", padx=(0, 12))

        self.img_files_var = tk.StringVar()
        tk.Entry(file_row, textvariable=self.img_files_var, font=("Segoe UI", 10),
                 bg=C["input_bg"], fg=C["text_dark"],
                 relief="flat", bd=0, highlightthickness=1,
                 highlightcolor=C["accent"], highlightbackground=C["border"],
                 insertbackground=C["text_dark"]
                 ).pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        ActionButton(file_row, text="选择文件", command=self._browse_images,
                     primary=False, bg=C["bg_card"]).pack(side="left", padx=(0, 6))
        ActionButton(file_row, text="选择文件夹", command=self._browse_image_folder,
                     primary=False, bg=C["bg_card"]).pack(side="left")
        for w in file_row.winfo_children():
            if isinstance(w, ActionButton):
                w.configure(width=100)

        # Hint
        hint = tk.Frame(inner, bg=C["bg_card"])
        hint.pack(fill="x", pady=(4, 0))
        tk.Label(hint, text="", bg=C["bg_card"], width=10).pack(side="left")
        tk.Label(hint, text="💡 在文章中引用: ![描述](/images/{slug}/文件名.png)",
                 font=("Segoe UI", 9), bg=C["bg_card"], fg=C["text_muted"]).pack(side="left")

        btn_row = self._button_row(inner)
        self._add_btn(btn_row, "📤 上传图片", self._upload_images)
        self._add_btn(btn_row, "📂 打开图片目录", self._open_images_dir, primary=False)

        self.images_log = self._add_log(inner)

    def _refresh_post_slugs(self):
        slugs = []
        if os.path.isdir(POSTS_DIR):
            for f in os.listdir(POSTS_DIR):
                if f.endswith(".md"):
                    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', f[:-3])
                    slugs.append(name)
        if os.path.isdir(PUBLIC_IMAGES_DIR):
            for d in os.listdir(PUBLIC_IMAGES_DIR):
                if os.path.isdir(os.path.join(PUBLIC_IMAGES_DIR, d)) and d not in slugs:
                    slugs.append(d)
        if hasattr(self, 'img_slug_cb'):
            self.img_slug_cb["values"] = sorted(slugs)

    def _browse_images(self):
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.svg *.webp"), ("All", "*.*")]
        )
        if files:
            self.img_files_var.set("; ".join(files))

    def _browse_image_folder(self):
        folder = filedialog.askdirectory(title="选择图片文件夹")
        if folder:
            images = []
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp"):
                images.extend(Path(folder).glob(ext))
            self.img_files_var.set("; ".join(str(p) for p in images))

    def _upload_images(self):
        slug = self.img_slug_var.get().strip()
        if not slug:
            messagebox.showwarning("提示", "请填写目标文章 Slug")
            return
        files_str = self.img_files_var.get().strip()
        if not files_str:
            messagebox.showwarning("提示", "请选择图片文件")
            return

        files = [f.strip() for f in files_str.split(";") if f.strip()]
        dest_dir = os.path.join(PUBLIC_IMAGES_DIR, slug)
        ensure_dir(dest_dir)
        self.images_log.clear()
        copied = 0
        for f in files:
            if not os.path.isfile(f):
                self.images_log.append(f"❌ 文件不存在: {f}")
                continue
            filename = os.path.basename(f)
            dest = os.path.join(dest_dir, filename)
            try:
                shutil.copy2(f, dest)
                copied += 1
                self.images_log.append(f"✅ {filename} → /images/{slug}/")
            except Exception as e:
                self.images_log.append(f"❌ {filename}: {e}")
        self.images_log.append(f"\n🎉 已上传 {copied}/{len(files)} 个图片")

    def _open_images_dir(self):
        ensure_dir(PUBLIC_IMAGES_DIR)
        os.startfile(PUBLIC_IMAGES_DIR)

    # ═══════════════════════════════════════════════════════════
    # Page: Manage Posts
    # ═══════════════════════════════════════════════════════════
    def _build_manage_page(self):
        page = self._create_page("manage")
        self._section_title(page, "管理文章", "查看、编辑、删除已发布的文章")

        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Filter row
        filter_row = tk.Frame(inner, bg=C["bg_card"])
        filter_row.pack(fill="x", pady=(0, 8))

        self.manage_filter_var = tk.StringVar()
        self.manage_filter_var.trace_add("write", lambda *_: self._refresh_post_list())
        tk.Label(filter_row, text="🔍 搜索:", font=("Segoe UI", 10),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(side="left")
        filter_entry = tk.Entry(filter_row, textvariable=self.manage_filter_var,
                                font=("Segoe UI", 10), bg=C["input_bg"],
                                fg=C["text_dark"], relief="flat", bd=0, width=30)
        filter_entry.pack(side="left", padx=(8, 16), ipady=6)

        self._add_btn(filter_row, "🔄 刷新列表", self._refresh_post_list, primary=False)

        # Post list with Treeview
        list_frame = tk.Frame(inner, bg=C["bg_card"])
        list_frame.pack(fill="both", expand=True, pady=(4, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Manage.Treeview",
                        background=C["bg_card"],
                        foreground=C["text_dark"],
                        fieldbackground=C["bg_card"],
                        font=("Segoe UI", 10),
                        rowheight=36)
        style.configure("Manage.Treeview.Heading",
                        background=C["input_bg"],
                        foreground=C["text_dark"],
                        font=("Segoe UI", 10, "bold"))
        style.map("Manage.Treeview",
                  background=[("selected", C["accent_bg"])],
                  foreground=[("selected", C["accent"])])

        cols = ("title", "date", "tags", "status")
        self.post_tree = ttk.Treeview(list_frame, columns=cols, show="headings",
                                       style="Manage.Treeview", selectmode="browse")
        self.post_tree.heading("title", text="标题")
        self.post_tree.heading("date", text="日期")
        self.post_tree.heading("tags", text="标签")
        self.post_tree.heading("status", text="状态")
        self.post_tree.column("title", width=280, minwidth=150)
        self.post_tree.column("date", width=120, minwidth=80)
        self.post_tree.column("tags", width=200, minwidth=100)
        self.post_tree.column("status", width=80, minwidth=60)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.post_tree.yview)
        self.post_tree.configure(yscrollcommand=scrollbar.set)
        self.post_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action buttons
        btn_row = self._button_row(inner)
        self._add_btn(btn_row, "📂 打开文件", self._manage_open, primary=False)
        self._add_btn(btn_row, "✏️ 编辑文章", self._manage_edit, primary=False)
        self._add_btn(btn_row, "🔄 切换草稿/发布", self._manage_toggle_draft, primary=False)
        self._add_btn(btn_row, "🗑️ 删除文章", self._manage_delete, primary=True)

        self.manage_log = self._add_log(inner)

        # Store all posts data
        self._all_posts_data = []
        self._refresh_post_list()

    def _refresh_post_list(self):
        if not hasattr(self, 'post_tree'):
            return
        # Clear tree
        for item in self.post_tree.get_children():
            self.post_tree.delete(item)
        # Get posts
        self._all_posts_data = self._get_all_posts()
        filter_text = self.manage_filter_var.get().strip().lower() if hasattr(self, 'manage_filter_var') else ""
        for post in self._all_posts_data:
            # Apply filter
            if filter_text:
                searchable = f"{post['title']} {post['description']} {' '.join(post['tags'])} {post['filename']}".lower()
                if filter_text not in searchable:
                    continue
            status = "草稿" if post["draft"] else "已发布"
            tags_str = ", ".join(post["tags"]) if post["tags"] else "-"
            self.post_tree.insert("", "end", values=(
                post["title"], post["pubDate"], tags_str, status
            ))

    def _get_selected_post(self):
        selection = self.post_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先在列表中选择一篇文章")
            return None
        idx = self.post_tree.index(selection[0])
        # Need to account for filtering
        filter_text = self.manage_filter_var.get().strip().lower() if hasattr(self, 'manage_filter_var') else ""
        filtered = []
        for post in self._all_posts_data:
            if filter_text:
                searchable = f"{post['title']} {post['description']} {' '.join(post['tags'])} {post['filename']}".lower()
                if filter_text not in searchable:
                    continue
            filtered.append(post)
        if idx < len(filtered):
            return filtered[idx]
        return None

    def _manage_open(self):
        post = self._get_selected_post()
        if post:
            os.startfile(post["path"])

    def _manage_edit(self):
        post = self._get_selected_post()
        if post:
            os.startfile(post["path"])

    def _manage_toggle_draft(self):
        post = self._get_selected_post()
        if not post:
            return
        content = read_file_safe(post["path"])
        if content is None:
            self.manage_log.append(f"❌ 无法读取文件: {post['filename']}")
            return
        fm, body = parse_frontmatter(content)
        if not fm:
            self.manage_log.append(f"❌ 文件没有 Frontmatter: {post['filename']}")
            return
        current_draft = fm.get("draft", False)
        new_draft = not current_draft
        # Rebuild frontmatter
        title = fm.get("title", "")
        description = fm.get("description", "")
        pub_date = fm.get("pubDate", datetime.now().strftime("%Y-%m-%d"))
        tags = fm.get("tags", [])
        new_fm = build_frontmatter(title, description, pub_date, tags, draft=new_draft)
        new_content = new_fm + "\n" + body
        write_file_safe(post["path"], new_content)
        status = "草稿" if new_draft else "已发布"
        self.manage_log.append(f"✅ {post['title']} → {status}")
        self._refresh_post_list()

    def _manage_delete(self):
        post = self._get_selected_post()
        if not post:
            return
        if not messagebox.askyesno("确认删除",
                f"确定要删除文章吗？\n\n标题: {post['title']}\n文件: {post['filename']}\n\n此操作不可撤销！"):
            return
        try:
            os.remove(post["path"])
            self.manage_log.append(f"🗑️ 已删除: {post['filename']}")
            # Also check for associated images directory
            slug = post["filename"].replace(".md", "")
            # Extract slug from filename (remove date prefix)
            slug_match = re.match(r'\d{4}-\d{2}-\d{2}-(.+)', slug)
            if slug_match:
                slug = slug_match.group(1)
            img_dir = os.path.join(PUBLIC_IMAGES_DIR, slug)
            if os.path.isdir(img_dir):
                if messagebox.askyesno("删除图片",
                        f"检测到关联图片目录: public/images/{slug}/\n是否一并删除？"):
                    shutil.rmtree(img_dir)
                    self.manage_log.append(f"🗑️ 已删除图片目录: public/images/{slug}/")
            self._refresh_post_list()
        except Exception as e:
            self.manage_log.append(f"❌ 删除失败: {e}")

    # ═══════════════════════════════════════════════════════════
    # Page 4: Site Info
    # ═══════════════════════════════════════════════════════════
    def _build_siteinfo_page(self):
        page = self._create_page("siteinfo")
        self._section_title(page, "网站信息", "修改博客的全局配置信息")

        # Scrollable canvas for the entire page content
        canvas = tk.Canvas(page, bg=C["bg_main"], highlightthickness=0)
        scrollbar = tk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=C["bg_main"])
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        card = self._card(scroll_frame)
        card.pack(fill="both", expand=True, padx=(0, 16), pady=0)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Load current values
        consts_content = read_file_safe(CONSTS_FILE)
        current = self._parse_consts(consts_content) if consts_content else {}
        footer_content = read_file_safe(FOOTER_FILE)
        current_footer = self._parse_footer(footer_content) if footer_content else {}
        # Load site-config.json
        site_cfg = self._load_site_config()

        # ── Basic Info Section ──
        tk.Label(inner, text="基本配置", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(0, 8))
        sep = tk.Frame(inner, bg=C["accent"], height=2)
        sep.pack(fill="x", pady=(0, 12))

        self.si_title_var = tk.StringVar(value=current.get("SITE_TITLE", ""))
        self._form_row(inner, "网站标题", self.si_title_var)

        self.si_desc_var = tk.StringVar(value=current.get("SITE_DESCRIPTION", ""))
        self._form_row(inner, "网站描述", self.si_desc_var)

        self.si_author_var = tk.StringVar(value=current.get("SITE_AUTHOR", ""))
        self._form_row(inner, "作者", self.si_author_var)

        self.si_url_var = tk.StringVar(value=current.get("SITE_URL", ""))
        self._form_row(inner, "网站 URL", self.si_url_var)

        # ── Hero Section ──
        tk.Label(inner, text="首页 Hero", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(16, 8))
        sep_hero = tk.Frame(inner, bg=C["accent"], height=2)
        sep_hero.pack(fill="x", pady=(0, 12))

        self.si_hero_title = tk.StringVar(value=site_cfg.get("hero", {}).get("title", ""))
        self._form_row(inner, "大标题", self.si_hero_title)

        self.si_hero_lede = tk.StringVar(value=site_cfg.get("hero", {}).get("lede", ""))
        self._form_row(inner, "导语", self.si_hero_lede)

        self.si_hero_subtitle = tk.StringVar(value=site_cfg.get("hero", {}).get("chapter_subtitle", ""))
        self._form_row(inner, "副标题", self.si_hero_subtitle)

        self.si_hero_vol = tk.StringVar(value=site_cfg.get("hero", {}).get("chapter_vol", ""))
        self._form_row(inner, "卷号", self.si_hero_vol)

        # Imprint fields
        tk.Label(inner, text="Imprint（印记）", font=("Segoe UI", 10, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(8, 4))
        self.si_imprint_air = tk.StringVar(value=site_cfg.get("hero", {}).get("imprint", {}).get("air", {}).get("value", ""))
        self._form_row(inner, "Air", self.si_imprint_air)
        self.si_imprint_sound = tk.StringVar(value=site_cfg.get("hero", {}).get("imprint", {}).get("sound", {}).get("value", ""))
        self._form_row(inner, "Sound", self.si_imprint_sound)
        self.si_imprint_tea = tk.StringVar(value=site_cfg.get("hero", {}).get("imprint", {}).get("tea", {}).get("value", ""))
        self._form_row(inner, "Tea", self.si_imprint_tea)
        self.si_imprint_temp = tk.StringVar(value=site_cfg.get("hero", {}).get("imprint", {}).get("temp", {}).get("value", ""))
        self._form_row(inner, "Temp", self.si_imprint_temp)

        # Meta row fields
        tk.Label(inner, text="Meta 行（状态栏）", font=("Segoe UI", 10, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(8, 4))
        self.si_hero_now = tk.StringVar(value=site_cfg.get("hero", {}).get("now", {}).get("value", ""))
        self._form_row(inner, "Now", self.si_hero_now)
        self.si_hero_desk = tk.StringVar(value=site_cfg.get("hero", {}).get("desk", {}).get("value", ""))
        self._form_row(inner, "Desk", self.si_hero_desk)
        self.si_hero_mood = tk.StringVar(value=site_cfg.get("hero", {}).get("mood", {}).get("value", ""))
        self._form_row(inner, "Mood", self.si_hero_mood)
        self.si_hero_role = tk.StringVar(value=site_cfg.get("hero", {}).get("role", {}).get("value", ""))
        self._form_row(inner, "Role", self.si_hero_role)

        # ── Recent Section ──
        tk.Label(inner, text="最近文章区", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(16, 8))
        sep_recent = tk.Frame(inner, bg=C["accent"], height=2)
        sep_recent.pack(fill="x", pady=(0, 12))

        self.si_recent_quote = tk.StringVar(value=site_cfg.get("recent", {}).get("marginalia", {}).get("quote", ""))
        self._form_row(inner, "Marginalia", self.si_recent_quote)

        self.si_recent_author = tk.StringVar(value=site_cfg.get("recent", {}).get("marginalia", {}).get("author", ""))
        self._form_row(inner, "引用作者", self.si_recent_author)

        self.si_recent_reading_title = tk.StringVar(value=site_cfg.get("recent", {}).get("reading", {}).get("title", ""))
        self._form_row(inner, "在读", self.si_recent_reading_title)

        self.si_recent_reading_author = tk.StringVar(value=site_cfg.get("recent", {}).get("reading", {}).get("author", ""))
        self._form_row(inner, "读作者", self.si_recent_reading_author)

        # ── Colophon Section ──
        tk.Label(inner, text="Colophon（版本说明）", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(16, 8))
        sep_colo = tk.Frame(inner, bg=C["accent"], height=2)
        sep_colo.pack(fill="x", pady=(0, 12))

        self.si_colophon_typeset = tk.StringVar(value=site_cfg.get("colophon", {}).get("typeset", ""))
        self._form_row(inner, "字体", self.si_colophon_typeset)

        self.si_colophon_written = tk.StringVar(value=site_cfg.get("colophon", {}).get("written_from", ""))
        self._form_row(inner, "写作地点", self.si_colophon_written)

        # ── About Section ──
        tk.Label(inner, text="关于页", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(16, 8))
        sep_about = tk.Frame(inner, bg=C["accent"], height=2)
        sep_about.pack(fill="x", pady=(0, 12))

        self.si_about_role = tk.StringVar(value=site_cfg.get("about", {}).get("role", ""))
        self._form_row(inner, "角色", self.si_about_role)

        self.si_about_based = tk.StringVar(value=site_cfg.get("about", {}).get("based", ""))
        self._form_row(inner, "所在地", self.si_about_based)

        self.si_about_writes = tk.StringVar(value=site_cfg.get("about", {}).get("writes", ""))
        self._form_row(inner, "写作方向", self.si_about_writes)

        self.si_about_drinks = tk.StringVar(value=site_cfg.get("about", {}).get("drinks", ""))
        self._form_row(inner, "饮料", self.si_about_drinks)

        # ── Social / Contact Section ──
        tk.Label(inner, text="联系方式", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(16, 8))
        sep_social = tk.Frame(inner, bg=C["accent"], height=2)
        sep_social.pack(fill="x", pady=(0, 12))

        self.social_frame = tk.Frame(inner, bg=C["bg_card"])
        self.social_frame.pack(fill="x")

        self.si_social_entries = []  # list of dicts: {label_var, href_var, handle_var, row_frame}

        # Populate existing social links from config
        for s in site_cfg.get("about", {}).get("social", []):
            self._add_social_row(self.social_frame, s.get("label", ""), s.get("href", ""), s.get("handle", ""))

        # Add / Remove buttons
        social_btn_row = tk.Frame(inner, bg=C["bg_card"])
        social_btn_row.pack(fill="x", pady=(8, 0))
        self._add_btn(social_btn_row, "➕ 添加联系方式", lambda: self._add_social_row(self.social_frame))
        self._add_btn(social_btn_row, "➖ 删除最后一行", lambda: self._remove_last_social_row(self.social_frame), primary=False)

        # ── Footer Section ──
        tk.Label(inner, text="页脚配置", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(16, 8))
        sep2 = tk.Frame(inner, bg=C["accent"], height=2)
        sep2.pack(fill="x", pady=(0, 12))

        self.si_footer_author = tk.StringVar(value=site_cfg.get("footer", {}).get("author", ""))
        self._form_row(inner, "页脚作者", self.si_footer_author)

        self.si_footer_var = tk.StringVar(value=site_cfg.get("footer", {}).get("tagline", current_footer.get("slogan", "")))
        self._form_row(inner, "页脚标语", self.si_footer_var)

        self.si_github_var = tk.StringVar(value=current_footer.get("github", ""))
        self._form_row(inner, "GitHub", self.si_github_var)

        btn_row = self._button_row(inner)
        self._add_btn(btn_row, "💾 保存所有修改", self._save_site_info)
        self._add_btn(btn_row, "🔄 恢复原值", self._reload_site_info, primary=False)

        self.siteinfo_log = self._add_log(inner)

    def _parse_consts(self, content):
        result = {}
        for m in re.finditer(r"export\s+const\s+(\w+)\s*=\s*'([^']*)'", content):
            result[m.group(1)] = m.group(2)
        for m in re.finditer(r'export\s+const\s+(\w+)\s*=\s*"([^"]*)"', content):
            result[m.group(1)] = m.group(2)
        return result

    def _parse_footer(self, content):
        result = {}
        m = re.search(r'a quiet notebook for slow thoughts', content)
        if m:
            result["slogan"] = "a quiet notebook for slow thoughts."
        m = re.search(r'href="(https://github\.com/[^"]+)"', content)
        if m:
            result["github"] = m.group(1)
        return result

    def _load_site_config(self):
        """Load site-config.json and return as dict."""
        content = read_file_safe(SITE_CONFIG_FILE)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_site_info(self):
        try:
            # Save consts.ts
            content = read_file_safe(CONSTS_FILE)
            if content:
                content = re.sub(r"export const SITE_TITLE = '[^']*'",
                                 f"export const SITE_TITLE = '{self.si_title_var.get().strip()}'", content)
                content = re.sub(r"export const SITE_DESCRIPTION = '[^']*'",
                                 f"export const SITE_DESCRIPTION = '{self.si_desc_var.get().strip()}'", content)
                content = re.sub(r"export const SITE_AUTHOR = '[^']*'",
                                 f"export const SITE_AUTHOR = '{self.si_author_var.get().strip()}'", content)
                content = re.sub(r'export const SITE_URL = "[^"]*"',
                                 f'export const SITE_URL = "{self.si_url_var.get().strip()}"', content)
                write_file_safe(CONSTS_FILE, content)
                self.siteinfo_log.append("✅ consts.ts 已更新")

            # Save Footer.astro
            footer = read_file_safe(FOOTER_FILE)
            if footer:
                slogan = self.si_footer_var.get().strip()
                if slogan:
                    footer = re.sub(r'a quiet notebook for slow thoughts\.', slogan, footer)
                github = self.si_github_var.get().strip()
                if github:
                    footer = re.sub(r'https://github\.com/[^"]+', github, footer)
                write_file_safe(FOOTER_FILE, footer)
                self.siteinfo_log.append("✅ Footer 已更新")

            # Save site-config.json
            cfg = self._load_site_config()
            if not cfg:
                self.siteinfo_log.append("⚠️ site-config.json 读取失败，跳过")
            else:
                # Hero
                hero = cfg.setdefault("hero", {})
                hero["title"] = self.si_hero_title.get().strip()
                hero["lede"] = self.si_hero_lede.get().strip()
                hero["chapter_subtitle"] = self.si_hero_subtitle.get().strip()
                hero["chapter_vol"] = self.si_hero_vol.get().strip()
                # Imprint
                imprint = hero.setdefault("imprint", {})
                imprint.setdefault("air", {})["value"] = self.si_imprint_air.get().strip()
                imprint.setdefault("sound", {})["value"] = self.si_imprint_sound.get().strip()
                imprint.setdefault("tea", {})["value"] = self.si_imprint_tea.get().strip()
                imprint.setdefault("temp", {})["value"] = self.si_imprint_temp.get().strip()
                # Meta row
                hero.setdefault("now", {})["value"] = self.si_hero_now.get().strip()
                hero.setdefault("desk", {})["value"] = self.si_hero_desk.get().strip()
                hero.setdefault("mood", {})["value"] = self.si_hero_mood.get().strip()
                hero.setdefault("role", {})["value"] = self.si_hero_role.get().strip()
                # Recent
                recent = cfg.setdefault("recent", {})
                recent.setdefault("marginalia", {})["quote"] = self.si_recent_quote.get().strip()
                recent["marginalia"]["author"] = self.si_recent_author.get().strip()
                recent.setdefault("reading", {})["title"] = self.si_recent_reading_title.get().strip()
                recent["reading"]["author"] = self.si_recent_reading_author.get().strip()
                # Colophon
                colophon = cfg.setdefault("colophon", {})
                colophon["typeset"] = self.si_colophon_typeset.get().strip()
                colophon["written_from"] = self.si_colophon_written.get().strip()
                # About
                about = cfg.setdefault("about", {})
                about["role"] = self.si_about_role.get().strip()
                about["based"] = self.si_about_based.get().strip()
                about["writes"] = self.si_about_writes.get().strip()
                about["drinks"] = self.si_about_drinks.get().strip()
                # Social / Contact
                social_list = []
                for entry in self.si_social_entries:
                    label = entry["label_var"].get().strip()
                    href = entry["href_var"].get().strip()
                    handle = entry["handle_var"].get().strip()
                    if label and href:
                        social_item = {"label": label, "href": href}
                        if handle:
                            social_item["handle"] = handle
                        social_list.append(social_item)
                about["social"] = social_list
                # Footer in site-config
                footer_cfg = cfg.setdefault("footer", {})
                footer_cfg["author"] = self.si_footer_author.get().strip()
                footer_cfg["tagline"] = self.si_footer_var.get().strip()

                write_file_safe(SITE_CONFIG_FILE, json.dumps(cfg, indent=2, ensure_ascii=False))
                self.siteinfo_log.append("✅ site-config.json 已更新")

            self.siteinfo_log.append("🎉 网站信息保存完成！")
        except Exception as e:
            self.siteinfo_log.append(f"❌ 保存失败: {e}")

    def _reload_site_info(self):
        consts = read_file_safe(CONSTS_FILE)
        if consts:
            current = self._parse_consts(consts)
            self.si_title_var.set(current.get("SITE_TITLE", ""))
            self.si_desc_var.set(current.get("SITE_DESCRIPTION", ""))
            self.si_author_var.set(current.get("SITE_AUTHOR", ""))
            self.si_url_var.set(current.get("SITE_URL", ""))
        footer = read_file_safe(FOOTER_FILE)
        if footer:
            current_footer = self._parse_footer(footer)
            self.si_footer_var.set(current_footer.get("slogan", ""))
            self.si_github_var.set(current_footer.get("github", ""))
        # Reload site-config.json
        cfg = self._load_site_config()
        if cfg:
            hero = cfg.get("hero", {})
            self.si_hero_title.set(hero.get("title", ""))
            self.si_hero_lede.set(hero.get("lede", ""))
            self.si_hero_subtitle.set(hero.get("chapter_subtitle", ""))
            self.si_hero_vol.set(hero.get("chapter_vol", ""))
            imprint = hero.get("imprint", {})
            self.si_imprint_air.set(imprint.get("air", {}).get("value", ""))
            self.si_imprint_sound.set(imprint.get("sound", {}).get("value", ""))
            self.si_imprint_tea.set(imprint.get("tea", {}).get("value", ""))
            self.si_imprint_temp.set(imprint.get("temp", {}).get("value", ""))
            self.si_hero_now.set(hero.get("now", {}).get("value", ""))
            self.si_hero_desk.set(hero.get("desk", {}).get("value", ""))
            self.si_hero_mood.set(hero.get("mood", {}).get("value", ""))
            self.si_hero_role.set(hero.get("role", {}).get("value", ""))
            recent = cfg.get("recent", {})
            self.si_recent_quote.set(recent.get("marginalia", {}).get("quote", ""))
            self.si_recent_author.set(recent.get("marginalia", {}).get("author", ""))
            self.si_recent_reading_title.set(recent.get("reading", {}).get("title", ""))
            self.si_recent_reading_author.set(recent.get("reading", {}).get("author", ""))
            colophon = cfg.get("colophon", {})
            self.si_colophon_typeset.set(colophon.get("typeset", ""))
            self.si_colophon_written.set(colophon.get("written_from", ""))
            about = cfg.get("about", {})
            self.si_about_role.set(about.get("role", ""))
            self.si_about_based.set(about.get("based", ""))
            self.si_about_writes.set(about.get("writes", ""))
            self.si_about_drinks.set(about.get("drinks", ""))
            # Social / Contact
            for w in self.social_frame.winfo_children():
                w.destroy()
            self.si_social_entries.clear()
            for s in about.get("social", []):
                self._add_social_row(self.social_frame, s.get("label", ""), s.get("href", ""), s.get("handle", ""))
            footer_cfg = cfg.get("footer", {})
            self.si_footer_author.set(footer_cfg.get("author", ""))
        self.siteinfo_log.append("🔄 已恢复为当前文件中的值")

    # ═══════════════════════════════════════════════════════════
    # Page 5: Edit Page Content
    # ═══════════════════════════════════════════════════════════
    def _build_editpage_page(self):
        page = self._create_page("editpage")
        self._section_title(page, "页面内容", "编辑首页和关于页的源代码")

        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Page selector row
        sel_row = tk.Frame(inner, bg=C["bg_card"])
        sel_row.pack(fill="x", pady=(0, 12))

        tk.Label(sel_row, text="选择页面", font=("Segoe UI", 10),
                 bg=C["bg_card"], fg=C["text_muted"], width=10,
                 anchor="w").pack(side="left", padx=(0, 12))

        self.ep_page_var = tk.StringVar(value="首页 (index)")
        page_cb = ttk.Combobox(sel_row, textvariable=self.ep_page_var,
                               values=["首页 (index)", "关于页 (about)"],
                               font=("Segoe UI", 10), state="readonly")
        page_cb.pack(side="left", ipady=4)
        page_cb.bind("<<ComboboxSelected>>", self._load_page_content)

        ActionButton(sel_row, text="📂 加载", command=lambda: self._load_page_content(None),
                     primary=False, bg=C["bg_card"]).pack(side="left", padx=(16, 0))
        for w in sel_row.winfo_children():
            if isinstance(w, ActionButton):
                w.configure(width=80)

        # Editor
        self.ep_editor_frame = tk.Frame(inner, bg=C["log_bg"], bd=0)
        self.ep_editor_frame.pack(fill="both", expand=True)

        self.ep_editor = tk.Text(
            self.ep_editor_frame, wrap="word", font=("Cascadia Code", 10),
            bg=C["log_bg"], fg=C["log_fg"],
            insertbackground=C["log_fg"], relief="flat", bd=0,
            padx=12, pady=10, selectbackground="#45475a",
            undo=True
        )
        editor_sb = tk.Scrollbar(self.ep_editor_frame, command=self.ep_editor.yview,
                                  bg=C["log_bg"], troughcolor=C["log_bg"],
                                  activebackground=C["accent"])
        self.ep_editor.configure(yscrollcommand=editor_sb.set)
        editor_sb.pack(side="right", fill="y")
        self.ep_editor.pack(side="left", fill="both", expand=True)

        self._ep_file_path = None

        # Buttons at bottom
        btn_row = tk.Frame(inner, bg=C["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._add_btn(btn_row, "💾 保存修改", self._save_page_content)

    def _load_page_content(self, event=None):
        page = self.ep_page_var.get()
        filepath = INDEX_FILE if "首页" in page else ABOUT_FILE
        content = read_file_safe(filepath)
        if not content:
            return
        self._ep_file_path = filepath
        self.ep_editor.delete("1.0", "end")
        self.ep_editor.insert("1.0", content)

    def _save_page_content(self):
        if not self._ep_file_path:
            messagebox.showwarning("提示", "请先加载页面内容")
            return
        try:
            write_file_safe(self._ep_file_path, self.ep_editor.get("1.0", "end-1c"))
            messagebox.showinfo("成功", "页面内容已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    # ═══════════════════════════════════════════════════════════
    # Page 6: Local Preview
    # ═══════════════════════════════════════════════════════════
    def _build_preview_page(self):
        page = self._create_page("preview")
        self._section_title(page, "本地预览", "启动 Astro 开发服务器，在浏览器中预览博客")

        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Status indicator
        status_frame = tk.Frame(inner, bg=C["bg_card"])
        status_frame.pack(fill="x", pady=(0, 16))

        self.dev_status_indicator = tk.Canvas(status_frame, width=14, height=14,
                                               bg=C["bg_card"], highlightthickness=0)
        self.dev_status_indicator.pack(side="left", padx=(0, 8))
        self.dev_status_indicator.create_oval(2, 2, 12, 12, fill="#888", outline="", tags="dot")

        self.dev_status_var = tk.StringVar(value="服务器未运行")
        tk.Label(status_frame, textvariable=self.dev_status_var,
                 font=("Segoe UI", 12, "bold"), bg=C["bg_card"],
                 fg=C["text_dark"]).pack(side="left")

        # URL display
        url_frame = tk.Frame(inner, bg=C["input_bg"], highlightbackground=C["border"],
                             highlightthickness=1)
        url_frame.pack(fill="x", pady=(0, 16))
        tk.Label(url_frame, text="http://localhost:4321", font=("Cascadia Code", 11),
                 bg=C["input_bg"], fg=C["accent"]).pack(padx=12, pady=10, anchor="w")

        # Action buttons
        btn_row = tk.Frame(inner, bg=C["bg_card"])
        btn_row.pack(fill="x", pady=(0, 16))

        self._add_btn(btn_row, "▶️ 启动服务器", self._start_dev)
        self._add_btn(btn_row, "⏹️ 停止服务器", self._stop_dev, primary=False)
        self._add_btn(btn_row, "🌐 打开浏览器",
                      lambda: os.startfile("http://localhost:4321"), primary=False)

        # Log
        self.dev_log = self._add_log(inner)

    def _update_dev_status(self, status, color):
        """Update the status indicator dot and text."""
        self.dev_status_var.set(status)
        self.dev_status_indicator.delete("dot")
        self.dev_status_indicator.create_oval(2, 2, 12, 12, fill=color, outline="", tags="dot")

    def _start_dev(self):
        if self._dev_process and self._dev_process.poll() is None:
            self.dev_log.append("⚠️ 服务器已在运行中")
            return
        self._update_dev_status("正在启动...", C["accent_light"])

        def run():
            try:
                self._dev_process = subprocess.Popen(
                    "npm run dev", shell=True, cwd=BLOG_ROOT,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", bufsize=1
                )
                self.after(0, lambda: self._update_dev_status("服务器运行中", C["success"]))
                for line in self._dev_process.stdout:
                    self.after(0, lambda l=line: self.dev_log.append(l.rstrip()))
                self._dev_process.wait()
                self.after(0, lambda: self._update_dev_status("服务器已停止", "#888"))
            except Exception as e:
                self.after(0, lambda: self.dev_log.append(f"❌ 启动失败: {e}"))
                self.after(0, lambda: self._update_dev_status("启动失败", C["error"]))

        threading.Thread(target=run, daemon=True).start()

    def _stop_dev(self):
        if self._dev_process and self._dev_process.poll() is None:
            self._dev_process.terminate()
            self._update_dev_status("服务器已停止", "#888")
            self.dev_log.append("🛑 服务器已停止")
        else:
            self.dev_log.append("⚠️ 服务器未在运行")

    # ═══════════════════════════════════════════════════════════
    # Page 7: One-Click Publish
    # ═══════════════════════════════════════════════════════════
    def _build_publish_page(self):
        page = self._create_page("publish")
        self._section_title(page, "一键发布", "将修改提交到 Git 并推送到远程仓库，自动触发部署")

        card = self._card(page)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Checklist
        tk.Label(inner, text="发布前检查清单", font=("Segoe UI", 12, "bold"),
                 bg=C["bg_card"], fg=C["text_dark"]).pack(anchor="w", pady=(0, 8))

        checks = [
            "✅ 已用本地预览确认效果",
            "✅ 文章的 draft 标记已移除",
            "✅ 图片资源已正确上传",
        ]
        for c in checks:
            tk.Label(inner, text=f"   {c}", font=("Segoe UI", 10),
                     bg=C["bg_card"], fg=C["text_muted"]).pack(anchor="w")

        sep = tk.Frame(inner, bg=C["border"], height=1)
        sep.pack(fill="x", pady=16)

        # Commit message
        self.pub_msg_var = tk.StringVar(value=f"update: {datetime.now().strftime('%Y-%m-%d')}")
        self._form_row(inner, "提交信息", self.pub_msg_var)

        # Options
        opt_row = tk.Frame(inner, bg=C["bg_card"])
        opt_row.pack(fill="x", pady=(8, 0))
        self.pub_build_var = tk.BooleanVar(value=True)
        self._checkbox(opt_row, "发布前先构建 (astro build)", self.pub_build_var)
        self.pub_draft_rm_var = tk.BooleanVar(value=False)
        self._checkbox(opt_row, "自动移除草稿标记", self.pub_draft_rm_var)

        btn_row = self._button_row(inner)
        self._add_btn(btn_row, "📋 查看变更", self._show_changes, primary=False)
        self._add_btn(btn_row, "🚀 一键发布", self._do_publish)

        self.pub_log = self._add_log(inner)

    def _show_changes(self):
        self.pub_log.clear()
        ok, output = run_command("git status --short", cwd=BLOG_ROOT)
        if ok:
            if output.strip():
                self.pub_log.append("📋 文件变更:")
                for line in output.strip().splitlines():
                    self.pub_log.append(f"   {line}")
            else:
                self.pub_log.append("✅ 没有未提交的变更")
        else:
            self.pub_log.append(f"❌ 查询失败: {output}")

    def _do_publish(self):
        msg = self.pub_msg_var.get().strip()
        if not msg:
            messagebox.showwarning("提示", "请填写提交信息")
            return
        self._run_in_thread(self._publish_worker, msg)

    def _publish_worker(self, msg):
        log = self.pub_log
        log.clear()

        if self.pub_draft_rm_var.get():
            log.append("🔄 移除草稿标记...")
            if os.path.isdir(POSTS_DIR):
                for f in os.listdir(POSTS_DIR):
                    if f.endswith(".md"):
                        fp = os.path.join(POSTS_DIR, f)
                        content = read_file_safe(fp)
                        if content and "draft: true" in content:
                            content = content.replace("draft: true\n", "")
                            write_file_safe(fp, content)
                            log.append(f"  ✅ {f} - 已移除 draft 标记")

        if self.pub_build_var.get():
            log.append("🔄 构建项目...")
            ok, output = run_command("npm run build", cwd=BLOG_ROOT)
            if not ok:
                log.append(f"❌ 构建失败:\n{output}")
                return
            log.append("✅ 构建成功")

        log.append("🔄 暂存文件...")
        ok, _ = run_command("git add -A", cwd=BLOG_ROOT)
        if not ok:
            log.append("❌ git add 失败")
            return

        log.append(f"🔄 提交: {msg}")
        ok, _ = run_command(f'git commit -m "{msg}"', cwd=BLOG_ROOT)
        if not ok:
            log.append("⚠️ 没有新的变更需要提交，或提交失败")
            return

        log.append("🔄 推送到远程仓库...")
        ok, output = run_command("git push", cwd=BLOG_ROOT)
        if ok:
            log.append("🎉 发布成功！网站将自动部署。")
        else:
            log.append(f"❌ 推送失败:\n{output}")


# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = BlogToolbox()
    app.mainloop()
