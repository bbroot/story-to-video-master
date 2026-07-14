#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
load_novel.py — story-to-video-master Phase 0
读取 novel-master 真实 v2 项目结构，输出 data-summary.json。

支持：
- 角色子目录（settings/characters/<名>/{voice.md,state.json,bias_pack.json}）
- 整卷章节文件（chapters/arcN-*.md），按 '## 第N集' / '### 壹·一' 切分
- 中文键名兼容：foreshadowing.json（伏笔列表）、conflicts.json（冲突列表）
- 英文键名兼容：Foreshadowing / Conflicts
- v2 模式检测：plot_bus.json + characters/*/state.json

用法：
  python3 load_novel.py <novel_project_dir> [--out <output_json>]

输出：<project>/output/phase0/data-summary.json
"""

import argparse
import json
import os
import re
import sys


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_characters(chars_dir):
    """加载每个角色子目录的 voice.md + state.json + bias_pack.json。"""
    characters = []
    if not os.path.isdir(chars_dir):
        return characters
    for name in sorted(os.listdir(chars_dir)):
        cdir = os.path.join(chars_dir, name)
        if not os.path.isdir(cdir):
            continue
        voice = read_text(os.path.join(cdir, "voice.md"))
        state = read_json(os.path.join(cdir, "state.json"))
        bias = read_json(os.path.join(cdir, "bias_pack.json"))
        characters.append({
            "name": name,
            "voice_md": voice[:4000],  # 截断，避免 summary 过大
            "state": state,
            "bias_pack": bias,
            "has_voice": bool(voice),
            "has_state": state is not None,
            "has_bias": bias is not None,
        })
    return characters


def split_chapters(chapters_dir):
    """
    读取 chapters/ 下所有整卷 .md，按 '## 第N集' 切分为可改编单元。
    返回 [{ 'file', 'arc', 'episode', 'title', 'sections':[{'mark','text'}], 'raw_len' }]
    """
    episodes = []
    if not os.path.isdir(chapters_dir):
        return episodes
    for fn in sorted(os.listdir(chapters_dir)):
        if not fn.endswith(".md"):
            continue
        raw = read_text(os.path.join(chapters_dir, fn))
        if not raw.strip():
            continue
        arc = re.sub(r"\.md$", "", fn)
        # 按 '## 第N集' 切分
        parts = re.split(r"(?m)^##\s*第\s*\d+\s*集[^\n]*", raw)
        heads = re.findall(r"(?m)^##\s*(第\s*\d+\s*集[^\n]*)", raw)
        if not heads:
            # 无集标记：整卷作为单集
            episodes.append({
                "file": fn, "arc": arc, "episode": "整卷",
                "title": arc, "sections": [], "raw_len": len(raw),
            })
            continue
        for i, head in enumerate(heads):
            body = parts[i + 1] if i + 1 < len(parts) else ""
            # 小节切分 ### 壹·一
            sub = re.split(r"(?m)^###\s*[^\n]*", body)
            sub_heads = re.findall(r"(?m)^###\s*([^\n]*)", body)
            sections = []
            for j, sh in enumerate(sub_heads):
                stext = sub[j + 1] if j + 1 < len(sub) else ""
                sections.append({"mark": sh.strip(), "text_len": len(stext)})
            episodes.append({
                "file": fn, "arc": arc,
                "episode": head.strip(),
                "title": head.strip(),
                "sections": sections,
                "raw_len": len(body),
            })
    return episodes


def load_tracker(tracker_dir):
    foreshadowing = read_json(os.path.join(tracker_dir, "foreshadowing.json")) or {}
    conflicts = read_json(os.path.join(tracker_dir, "conflicts.json")) or {}
    plot_bus = read_json(os.path.join(tracker_dir, "plot_bus.json")) or []
    ncg = read_json(os.path.join(tracker_dir, "ncg.json")) or {}
    style_log = read_text(os.path.join(tracker_dir, "style-log.md"))

    # 兼容中文键
    fs_list = (foreshadowing.get("伏笔列表")
               or foreshadowing.get("Foreshadowing")
               or foreshadowing.get("foreshadow")
               or [])
    cf_list = (conflicts.get("冲突列表")
               or conflicts.get("Conflicts")
               or conflicts.get("conflict")
               or [])
    has_style_anime = "日漫" in style_log or "慢镜头" in style_log or "内心独白" in style_log

    return {
        "foreshadowing_count": len(fs_list) if isinstance(fs_list, list) else 0,
        "foreshadowing_sample": (fs_list[:5] if isinstance(fs_list, list) else []),
        "conflicts_count": len(cf_list) if isinstance(cf_list, list) else 0,
        "conflicts_sample": (cf_list[:5] if isinstance(cf_list, list) else []),
        "plot_bus_chapters": len(plot_bus) if isinstance(plot_bus, list) else 0,
        "ncg_nodes": len(ncg.get("nodes", [])) if isinstance(ncg, dict) else 0,
        "ncg_super_nodes": len(ncg.get("super_nodes", [])) if isinstance(ncg, dict) else 0,
        "style_anime_enhanced": has_style_anime,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", help="novel-master 项目目录")
    ap.add_argument("--out", default=None, help="输出 json 路径")
    args = ap.parse_args()

    root = args.project
    if not os.path.isdir(root):
        print(f"错误：项目目录不存在 {root}", file=sys.stderr)
        sys.exit(1)

    chars_dir = os.path.join(root, "settings", "characters")
    chapters_dir = os.path.join(root, "chapters")
    outline_dir = os.path.join(root, "outline")
    tracker_dir = os.path.join(root, "tracker")
    state = read_json(os.path.join(root, "state.json")) or {}

    characters = load_characters(chars_dir)
    episodes = split_chapters(chapters_dir)
    tracker = load_tracker(tracker_dir)

    # v2 检测：有 plot_bus 且角色普遍有 state.json
    v2 = (tracker["plot_bus_chapters"] > 0
          and sum(1 for c in characters if c["has_state"]) > 0)

    outlines = []
    if os.path.isdir(outline_dir):
        outlines = [f for f in sorted(os.listdir(outline_dir)) if f.endswith(".md")]

    complete_chars = sum(1 for c in characters if c["has_voice"] and c["has_state"] and c["has_bias"])
    completeness = (complete_chars / len(characters) * 100) if characters else 0

    summary = {
        "project": root,
        "book": state.get("book", os.path.basename(root.rstrip("/"))),
        "v2_mode": v2,
        "current_arc": state.get("current_arc"),
        "current_chapter": state.get("current_chapter"),
        "total_words": state.get("total_words"),
        "characters_total": len(characters),
        "characters_complete": complete_chars,
        "character_completeness_pct": round(completeness, 1),
        "outlines": outlines,
        "episodes_count": len(episodes),
        # 存全量 episodes（每集含 sections 但截断正文长度统计），供 Phase 4 渲染全集
        "episodes": [
            {
                "file": e["file"], "arc": e["arc"],
                "episode": e["episode"], "title": e["title"],
                "raw_len": e["raw_len"],
                "sections_count": len(e.get("sections", [])),
            } for e in episodes
        ],
        "episodes_sample": episodes[:3],
        "tracker": tracker,
        "data_warnings": [],
    }
    if completeness < 70:
        summary["data_warnings"].append(
            f"角色卡完整度仅 {completeness:.0f}%（<70%），建议补充 voice/state/bias")
    if tracker["foreshadowing_count"] == 0:
        summary["data_warnings"].append("未检测到伏笔数据，钩子设计将退化为独立模式")
    if len(episodes) == 0:
        summary["data_warnings"].append("未切分到任何集，将退化为仅大纲模式")

    out = args.out or os.path.join(root, "output", "phase0", "data-summary.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"✅ Phase 0 完成：{out}")
    print(f"   书名={summary['book']} v2={v2} 角色={len(characters)} "
          f"集={len(episodes)} 伏笔={tracker['foreshadowing_count']} "
          f"冲突={tracker['conflicts_count']}")
    for w in summary["data_warnings"]:
        print(f"   ⚠️ {w}")


if __name__ == "__main__":
    main()
