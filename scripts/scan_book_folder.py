#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_book_folder.py —— 通用书籍文件夹理解器
============================================
不再只依赖 novel-master 的产物,而是能读取任意用户的书籍文件夹,
自动理解所有文件的关系:自动分类、推断每个文件的角色、建立文件关系图,
输出 book-manifest.json 供 Phase 0 引用。

设计原则(借鉴 chunpu/novel-reader 的分段读取 + 资产抽取思想,但改为"文件夹关系理解"):
- 不强制任何固定目录结构(兼容 novel-master,也兼容任意乱序文件夹)
- 通过文件名 + 扩展名 + 内容指纹 三层信号推断文件角色
- 纯标准库,UTF-8 安全,跨平台

用法:
  python3 scan_book_folder.py <书籍文件夹路径> [--json]
  python3 scan_book_folder.py <书籍文件夹路径> --plain    # 人类可读摘要
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------- 文件角色推断(三层信号) ----------
# 1) 扩展名信号
TEXT_EXTS = {".txt", ".md", ".markdown", ".epub", ".doc", ".docx", ".rtf", ".pdf", ".mobi", ".azw", ".azw3"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".svg"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m3u8"}
DATA_EXTS = {".json", ".yaml", ".yml", ".csv", ".toml", ".xml"}

# 2) 文件名关键词 → 角色(中文/英文混合)
ROLE_PATTERNS = {
    "novel_body": [r"正文", r"小说", r"全文", r"story", r"novel", r"manuscript", r"原始", r"草稿"],
    "outline": [r"大纲", r"outline", r"细纲", r"分卷", r"卷纲"],
    "character": [r"角色", r"人物", r"人设", r"character", r"char", r"profile"],
    "setting_world": [r"世界", r"世界观", r"设定", r"背景", r"world", r"setting", r"lore"],
    "geography": [r"地图", r"地理", r"场景设定", r"地点", r"geograph", r"map"],
    "foreshadow": [r"伏笔", r"悬念", r"flag", r"foreshadow"],
    "conflict": [r"冲突", r"矛盾", r"conflict"],
    "storyboard": [r"分镜", r"storyboard", r"镜头表", r"shot"],
    "prompt_file": [r"prompt", r"提示词", r"\.prompt"],
    "style_log": [r"文风", r"风格日志", r"style", r"log"],
    "plot_bus": [r"情节总线", r"plot.?bus", r"时间线", r"timeline", r"事件"],
    "ncg": [r"叙事因果", r"ncg", r"causal", r"节点"],
    "progress": [r"state\.json", r"进度", r"progress", r"writing_status"],
    "report": [r"报告", r"bug", r"report", r"审计", r"audit", r"虫检"],
}

# 3) 内容指纹(针对文本文件,读取前 2KB 判断)
CONTENT_SIGNALS = {
    "foreshadow": [("伏笔列表",), ("埋入章节",), ("回收状态",), ("foreshadow",)],
    "conflict": [("冲突列表",), ("冲突双方",), ("conflict",)],
    "character": [("角色定位",), ("外貌特征",), ("口头禅",), ("身份：",), ("identity",)],
    "setting_world": [("世界观",), ("世界设定",), ("地理",), ("势力",)],
    "outline": [("第一卷",), ("第1卷",), ("分卷",), ("大纲",), ("卷一",)],
    "storyboard": [("镜号",), ("景别",), ("运镜",), ("shot",), ("scene",)],
    "plot_bus": [("情节总线",), ("plot_bus",), ("时间线",), ("事件清单",)],
    "ncg": [("叙事因果",), ("ncg",), ("节点",), ("cause",), ("effect",)],
    "novel_body": [("第", "章"), ("第", "集"), ("壹·",), ("贰·",), ("叁·",), ("## 第",), ("# 第",)],
}

# 排除的系统/噪声文件
SKIP_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
# 正文命名启发式(无关键词时也倾向为正文)
NOVEL_NAME_HINT = [r"^e\d", r"^arc\d", r"chapters/.*\.md$", r"第.{1,3}(章|集|卷)", r"\.md$" if False else r"^chapter"]


def detect_role(name: str, head_text: str = "") -> str:
    """三层信号综合推断文件角色。返回 role 字符串。
    优先级: 报告/进度 等显式排除 → 强信号角色 → 正文启发式 → unknown
    """
    low = name.lower()
    # 层2:文件名关键词(报告/进度优先于通用正文,避免误判)
    for role in ("report", "progress", "outline", "character", "setting_world",
                "geography", "foreshadow", "conflict", "storyboard", "style_log",
                "plot_bus", "ncg"):
        for p in ROLE_PATTERNS[role]:
            if re.search(p, low):
                return role
    # 层3:内容指纹(强信号)
    if head_text:
        for role, sigs in CONTENT_SIGNALS.items():
            for sig in sigs:
                if len(sig) == 1:
                    if sig[0].lower() in head_text.lower():
                        return role
                else:  # 多 token 需全部出现
                    if all(s.lower() in head_text.lower() for s in sig):
                        return role
    # 层2b:正文命名启发式(chapters/ 下 md、E1.md、arc1-*.md、含「第X章/集」名)
    if re.search(r"chapters/", name) and low.endswith(".md"):
        return "novel_body"
    if re.search(r"(^|/)(e\d+|arc\d+|chapter\d+)", low) and low.endswith(".md"):
        return "novel_body"
    if re.search(r"第.{1,3}(章|集|卷)", low):
        return "novel_body"
    # 层2c: 通用正文关键词
    for p in ROLE_PATTERNS["novel_body"]:
        if re.search(p, low):
            return "novel_body"
    return "unknown"


def read_head(path: Path, limit: int = 2048) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except Exception:
        return ""


def ext_of(name: str) -> str:
    return os.path.splitext(name)[1].lower()


def classify_file(path: Path) -> dict:
    ext = ext_of(path.name)
    if path.name.lower() in SKIP_NAMES:
        return {"name": path.name, "rel": str(path), "size": path.stat().st_size,
                "ext": ext, "category": "skip", "role": "system"}
    role = "unknown"
    category = "other"
    if ext in TEXT_EXTS:
        category = "text"
        role = detect_role(path.name, read_head(path))
    elif ext in IMAGE_EXTS:
        category = "image"
        # 图片按文件名猜是角色/场景/道具/其他参考
        low = path.name.lower()
        if re.search(r"角色|char|人设|人物", low):
            role = "ref_character"
        elif re.search(r"场景|scene|地图|地点|地理", low):
            role = "ref_scene"
        elif re.search(r"道具|prop|物品", low):
            role = "ref_prop"
        else:
            role = "ref_other"
    elif ext in AUDIO_EXTS:
        category = "audio"
        role = "audio_bgm" if re.search(r"bgm|音乐|配乐|ost", path.name.lower()) else "audio_other"
    elif ext in VIDEO_EXTS:
        category = "video"
        role = "video_clip"
    elif ext in DATA_EXTS:
        category = "data"
        role = detect_role(path.name, read_head(path))
    return {
        "name": path.name,
        "rel": str(path),
        "size": path.stat().st_size if path.exists() else 0,
        "ext": ext,
        "category": category,
        "role": role,
    }


def infer_relationships(files: list[dict]) -> list[dict]:
    """推断文件之间的关系(轻量启发式)。"""
    rels = []
    char_files = [f for f in files if "character" in f["role"] or f["role"] == "ref_character"]
    scene_files = [f for f in files if "geography" in f["role"] or f["role"] == "ref_scene" or "setting" in f["role"]]
    body_files = [f for f in files if f["role"] == "novel_body"]
    outline_files = [f for f in files if f["role"] == "outline"]
    board_files = [f for f in files if f["role"] == "storyboard"]
    # 正文 ↔ 大纲
    for b in body_files:
        for o in outline_files:
            rels.append({"from": b["name"], "to": o["name"], "type": "正文-被大纲规划"})
    # 角色/场景设定 → 正文(设定服务于正文)
    for c in char_files + scene_files:
        for b in body_files:
            rels.append({"from": c["name"], "to": b["name"], "type": "设定-供正文改编"})
    # 分镜 ← 正文/大纲
    for s in board_files:
        for src in body_files + outline_files:
            rels.append({"from": s["name"], "to": src["name"], "type": "分镜-衍生自"})
    return rels


def scan(folder: str) -> dict:
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        return {"ok": False, "error": f"目录不存在或不是文件夹: {folder}"}
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            # 跳过明显的非书籍文件
            if any(skip in p.parts for skip in (".git", "node_modules", "__pycache__", "output", ".qclaw")):
                continue
            info = classify_file(p)
            if info.get("category") == "skip":
                continue
            files.append(info)
    # 汇总
    by_role = {}
    for f in files:
        by_role.setdefault(f["role"], []).append(f["name"])
    rels = infer_relationships(files)
    manifest = {
        "ok": True,
        "root": str(root.resolve()),
        "file_count": len(files),
        "roles": by_role,
        "files": files,
        "relationships": rels,
        "has_novel_master_signature": any(
            "character" in f["role"] or f["role"] == "foreshadow" for f in files
        ) or (root / "settings" / "characters").exists(),
    }
    return manifest


def main():
    ap = argparse.ArgumentParser(description="通用书籍文件夹理解器")
    ap.add_argument("folder")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--plain", action="store_true", help="人类可读摘要")
    args = ap.parse_args()
    m = scan(args.folder)
    if args.json:
        print(json.dumps(m, ensure_ascii=False, indent=2))
        return
    if args.plain or not args.json:
        if not m.get("ok"):
            print("❌", m.get("error"))
            sys.exit(1)
        print(f"📁 书籍文件夹理解结果: {m['root']}")
        print(f"   文件总数: {m['file_count']}")
        print(f"   疑似 novel-master 项目: {'是' if m['has_novel_master_signature'] else '否(通用文件夹)'}")
        print("\n--- 按角色分类 ---")
        for role, names in m["roles"].items():
            print(f"  [{role}] {len(names)} 个")
            for n in names[:8]:
                print(f"      · {n}")
            if len(names) > 8:
                print(f"      · …(共 {len(names)})")
        print("\n--- 推断的文件关系 ---")
        for r in m["relationships"][:20]:
            print(f"  {r['from']}  →({r['type']})→  {r['to']}")
        if len(m["relationships"]) > 20:
            print(f"  …(共 {len(m['relationships'])} 条关系)")


if __name__ == "__main__":
    main()
