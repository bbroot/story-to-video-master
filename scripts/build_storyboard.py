#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_storyboard.py — story-to-video-master Phase 4
读取 Phase 0 的 data-summary.json + 钩子规划，渲染分镜 JSON + Markdown。

用法：
  python3 build_storyboard.py <data-summary.json> [--episode "第1集"] [--out <dir>]

输出：
  <out>/storyboard-第N集.json
  <out>/storyboard-第N集.md
"""

import argparse
import json
import os
import re
import sys


def estimate_shots(text_len):
    """字数/规模 → 镜头数（近似，单集正文长度）。"""
    if text_len <= 1200:
        return (6, 8)
    elif text_len <= 2500:
        return (8, 12)
    else:
        return (12, 16)


def build_shots(episode, fps_plan=None):
    """基于切分单元生成占位分镜骨架（真实内容由 LLM 在 Phase 4 填充）。"""
    raw = episode.get("raw_len", 0)
    lo, hi = estimate_shots(raw)
    n = (lo + hi) // 2
    shots = []
    for i in range(1, n + 1):
        seg = "起因" if i <= n * 0.25 else ("经过" if i <= n * 0.75 else "结果")
        shots.append({
            "shotId": f"{episode.get('episode','X')[:1]}.{i}",
            "durationSec": 2,
            "narrativeGoal": f"待填充（段落：{seg}）",
            "subjectAnchors": [],
            "scene": "待定",
            "camera": "待定",
            "actionChain": "待填充（从章节正文转译）",
            "dramaticBeat": seg,
            "dialogue": "",
            "emotion": "待定",
            "prompt": "待填充",
        })
    return shots, lo, hi


def render_markdown(episode, shots, lo, hi):
    lines = []
    lines.append(f"# 分镜表 · {episode.get('title','')}\n")
    lines.append(f"- 源章节：`{episode.get('file','')}` / `{episode.get('episode','')}`")
    lines.append(f"- 预估镜头数：{lo}-{hi}（实际 {len(shots)}）\n")
    lines.append("| 镜号 | 时长 | 段落 | 景别 | 运镜 | 场景 | 角色 | 动作/情绪 | 对白/音效 | 钩子 | 源 |")
    lines.append("|------|------|------|------|------|------|------|----------|-----------|------|----|")
    for s in shots:
        lines.append("| {shotId} | {durationSec}s | {beat} | | | | | {action} | | | |".format(
            shotId=s["shotId"], durationSec=s["durationSec"],
            beat=s["dramaticBeat"], action=s["actionChain"]))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("summary", help="Phase 0 的 data-summary.json")
    ap.add_argument("--episode", default=None, help="只渲染指定集（如 '第1集'）")
    ap.add_argument("--out", default=None, help="输出目录")
    args = ap.parse_args()

    summary = json.load(open(args.summary, encoding="utf-8"))
    episodes = summary.get("episodes") or summary.get("episodes_sample", [])
    # 若 summary 含完整 episodes 则优先；否则需要外部传完整数据
    out_dir = args.out or os.path.join(
        os.path.dirname(os.path.dirname(args.summary)), "output", "storyboard")
    os.makedirs(out_dir, exist_ok=True)

    if not episodes:
        print("⚠️ summary 未含 episodes 明细（Phase 0 仅取样）。"
              "请用 load_novel.py 输出完整 episodes 后再渲染。", file=sys.stderr)
        sys.exit(1)

    targets = [e for e in episodes if not args.episode or args.episode in e.get("episode", "")]
    if args.episode and not targets:
        # 尝试匹配 '第1集' 子串
        targets = [e for e in episodes if args.episode in e.get("episode", "")
                   or e.get("episode", "").replace(" ", "") == args.episode]

    count = 0
    for ep in targets:
        shots, lo, hi = build_shots(ep)
        ep_tag = re.sub(r"[^\w一-鿿]", "_", ep.get("episode", "X"))[:20]
        sb = {
            "schemaVersion": "storyboard-director/v1.1",
            "chapter": ep.get("episode", ""),
            "sourceChapter": f"{ep.get('file','')} / {ep.get('episode','')}",
            "globalStyle": "电影写实",
            "cast": [],
            "shots": shots,
        }
        jpath = os.path.join(out_dir, f"storyboard-{ep_tag}.json")
        mpath = os.path.join(out_dir, f"storyboard-{ep_tag}.md")
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump(sb, f, ensure_ascii=False, indent=2)
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(render_markdown(ep, shots, lo, hi))
        count += 1
        print(f"✅ {ep.get('episode','')} → {jpath}（{len(shots)} 镜）")
    print(f"共生成 {count} 个分镜单元。")


if __name__ == "__main__":
    main()
