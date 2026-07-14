#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_plain_text.py — story-to-video-master 普通模式 (Phase 0b)
解析用户粘贴的普通小说文本，提取角色/场景/道具特征卡，做输入校验。
借鉴 novel-to-storyboard/parse_novel.py 的实体提取思路 + ark-novel-to-tuiwen 的输入校验。

用法：
  python3 parse_plain_text.py <novel.txt> [--max-chars 20000]

输出 JSON：{ valid, reason, characters, scenes, props, episodes_est, warnings }
"""

import argparse
import json
import os
import re
import sys

# 常见中文人名/称谓代词（极简启发式）
NAME_HINTS = ["道", "先生", "小姐", "公子", "姑娘", "少爷", "师傅", "师兄",
              "师姐", "师弟", "师妹", "大人", "将军", "陛下", "王爷", "殿下",
              "长老", "城主", "教头", "教官", "队长", "老板", "掌柜", "医生", "护士"]


def validate(text):
    if len(text.strip()) < 200:
        return False, "原文太短（<200字），连一个完整高光段都撑不起来。请给至少一章内容。"
    if not re.search(r"[一-鿿]", text):
        return False, "未发现中文内容，本工具面向中文小说。"
    # 极简"是否像小说"：有引号对话 或 有人物称谓 或 场景描写词
    has_dialog = bool(re.search(r"[“\"『」「」『』][^”\"]{2,30}[”\"『」「」『』]", text))
    has_name = any(h in text for h in NAME_HINTS)
    has_scene = bool(re.search(r"(清晨|傍晚|黄昏|夜里|房间|街道|门外|山|海|城|殿|洞|林|院|厅|室|场)", text))
    if not (has_dialog or has_name or has_scene):
        return False, "这看起来不像是小说章节（缺对话/人物/场景描写），请确认原文。"
    return True, ""


def extract_characters(text):
    """极简角色提取：称谓+姓名 或 引号前主语。"""
    chars = {}
    # 1) 称谓前的人名：如「林渡道」「陆沉先生」
    for m in re.finditer(r"([一-龥]{1,4})(道|先生|小姐|公子|姑娘|少爷|师傅|师兄|师姐|将军|大人|陛下|王爷|殿下|长老|城主|教头|教官|队长|老板|掌柜|医生)", text):
        name = m.group(1)
        if 1 <= len(name) <= 4:
            chars.setdefault(name, {"mentions": 0, "first_scene": ""})
            chars[name]["mentions"] += 1
    # 2) 引号前主语「X说/问/道」
    for m in re.finditer(r"([一-龥]{1,4})(说道|说|问|答道|低声道|冷笑|怒道|轻声)", text):
        name = m.group(1)
        if 1 <= len(name) <= 4:
            chars.setdefault(name, {"mentions": 0, "first_scene": ""})
            chars[name]["mentions"] += 1
    # 过滤：出现≥2次（避免短样本误提取单字/动作片段作为角色）
    out = {}
    for n, d in chars.items():
        if d["mentions"] >= 2:
            out[n] = d
    return out


def extract_scenes_props(text):
    scene_words = ["房间", "街道", "门外", "山林", "院子", "大厅", "洞窟", "海边",
                   "城", "殿", "训练场", "工坊", "茶馆", "书房", "牢房", "山顶"]
    scenes = {}
    for w in scene_words:
        c = len(re.findall(re.escape(w), text))
        if c >= 1:
            scenes[w] = c
    # 道具：被动作作用的名词（极简）
    prop_words = ["铁片", "弩", "枪", "剑", "信", "信封", "长剑", "包裹", "布包", "玉佩", "令牌"]
    props = {}
    for w in prop_words:
        c = len(re.findall(re.escape(w), text))
        if c >= 1:
            props[w] = c
    return scenes, props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="小说文本文件")
    ap.add_argument("--max-chars", type=int, default=20000)
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(json.dumps({"valid": False, "reason": f"文件不存在 {args.input}"}, ensure_ascii=False))
        sys.exit(1)

    text = open(args.input, encoding="utf-8").read()
    if len(text) > args.max_chars:
        text = text[:args.max_chars]
        warn = f"文本超 {args.max_chars} 字，已截断（建议分章提交）"
    else:
        warn = ""

    valid, reason = validate(text)
    if not valid:
        print(json.dumps({"valid": False, "reason": reason}, ensure_ascii=False))
        sys.exit(0)

    chars = extract_characters(text)
    scenes, props = extract_scenes_props(text)
    # 估算集数：按 ~3000 字/集
    ep_est = max(1, round(len(text) / 3000))

    result = {
        "valid": True,
        "reason": "",
        "char_count": len(text),
        "episodes_est": ep_est,
        "characters": list(chars.keys()),
        "scenes": scenes,
        "props": props,
        "warnings": [warn] if warn else [],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
