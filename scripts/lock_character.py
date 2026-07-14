#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lock_character.py —— 角色锁定闸门 + 生图提示词编排
================================================
职责(对应 references/character-locking.md):
  ① write-prompt : 从角色卡 JSON 生成三视图/情绪变体 T2I 提示词并落盘到 角色/<name>*.prompt.txt
  ② validate     : 冻结闸门——检查 registry 中每个角色三视图齐全+identity非空+约束存在 → locked
  ③ rebind       : 扫描分镜 JSON,校验每个 @角色名/@角色名-状态 都能解析到锁定参考图
  ④ list         : 列出当前锁定状态

本脚本只管"锁定元数据 + 提示词 + 校验",不调用任何视频平台 API(生图由 Phase 6 脚本完成)。
所有产物落在 output/<书籍名>/ 下,不污染源项目。

用法:
  python3 lock_character.py write-prompt --book <书籍名> --card assets/char_lindu.json
  python3 lock_character.py validate    --book <书籍名>
  python3 lock_character.py rebind      --book <书籍名> --storyboard <分镜.json>
  python3 lock_character.py list        --book <书籍名>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

OUT_ROOT = Path("output")


def _book_dir(book: str) -> Path:
    d = OUT_ROOT / book
    d.mkdir(parents=True, exist_ok=True)
    return d


def _registry_path(book: str) -> Path:
    return _book_dir(book) / "assets" / "character-registry.json"


def _load_registry(book: str) -> dict:
    p = _registry_path(book)
    if not p.exists():
        return {"schema": "character-registry/v1", "characters": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _save_registry(book: str, reg: dict):
    p = _registry_path(book)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


def _ok(cmd: str, data=None, error=None) -> int:
    out = {"ok": error is None, "command": cmd}
    if data is not None:
        out["data"] = data
    if error is not None:
        out["error"] = error
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if error is None else 1


# ---- 三视图 / 变体提示词模板(与 Phase 3.1 模板一致) ----
THREE_VIEW_TMPL = (
    "16:9 横版构图,[画风要求,如:电影写实/3D国漫CG]。\n"
    "左半边区域居中展示角色面部特写(强调记忆点与辨识度特征),"
    "右半边区域整齐排布角色三张全身设定图(正面/侧面/背面),所有角度比例严格一致。\n"
    "画面不得出现任何文字、水印;背景纯白干净。\n"
    "{identity}\n"
    "反模板反套路:拒绝完美比例,保留有记忆点的'不完美'特征;避免标签化。"
)

EXP_TMPL = (
    "基于参考图(角色正面三视图)严格保持人物身份与五官身材不变,仅改变神态与表情:\n"
    "角色:{name},状态:{state}。\n"
    "{identity}\n"
    "纯白或简洁背景,电影级光影,8K,禁止换脸/改变发型/改变服饰。"
)


def cmd_write_prompt(args) -> int:
    card_path = Path(args.card)
    if not card_path.exists():
        return _ok("write-prompt", error="角色卡不存在: %s" % card_path)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    book_dir = _book_dir(args.book)
    char_dir = book_dir / "角色"
    char_dir.mkdir(parents=True, exist_ok=True)
    name = card.get("name") or card.get("character_id") or "unknown"
    identity = card.get("canonical_identity") or card.get("appearance", {}).get("description") or ""
    # 三视图提示词
    tv_prompt = THREE_VIEW_TMPL.format(identity=identity)
    (char_dir / f"{name}.prompt.txt").write_text(tv_prompt, encoding="utf-8")
    # 情绪变体提示词(从 card.expression_list 或默认集)
    exp_list = card.get("expression_list") or ["neutral", "angry", "sad", "tense", "excited", "hesitant"]
    written = []
    for st in exp_list:
        ep = EXP_TMPL.format(name=name, state=st, identity=identity)
        (char_dir / f"{name}_exp_{st}.prompt.txt").write_text(ep, encoding="utf-8")
        written.append(f"{name}_exp_{st}.prompt.txt")
    # 回写 registry(若已有则补 identity,否则新增)
    reg = _load_registry(args.book)
    chars = reg.setdefault("characters", [])
    found = next((c for c in chars if c.get("name") == name), None)
    if found is None:
        seed = card.get("seed", 12345)
        found = {"char_id": card.get("character_id", "char_" + name),
                 "name": name, "canonical_identity": identity, "seed": seed,
                 "three_view": {"front": "", "side": "", "back": ""},
                 "expressions": {}, "negative_constraints": [], "locked": False}
        chars.append(found)
    else:
        if identity and not found.get("canonical_identity"):
            found["canonical_identity"] = identity
    _save_registry(args.book, reg)
    return _ok("write-prompt", data={"name": name, "three_view_prompt": f"{name}.prompt.txt",
                                     "expressions": written, "registry": str(_registry_path(args.book))})


def _validate_char(c: dict) -> list:
    msgs = []
    tv = c.get("three_view", {})
    if not (tv.get("front") and tv.get("side") and tv.get("back")):
        missing = [k for k in ("front", "side", "back") if not tv.get(k)]
        msgs.append("三视图缺失: " + "/".join(missing))
    if not c.get("canonical_identity"):
        msgs.append("canonical_identity 为空")
    if not c.get("negative_constraints"):
        msgs.append("negative_constraints 为空")
    return msgs


def cmd_validate(args) -> int:
    reg = _load_registry(args.book)
    chars = reg.get("characters", [])
    if not chars:
        return _ok("validate", error="注册表为空,请先 write-prompt")
    results = []
    all_ok = True
    for c in chars:
        issues = _validate_char(c)
        ok = not issues
        c["locked"] = ok
        results.append({"name": c.get("name"), "locked": ok, "issues": issues})
        if not ok:
            all_ok = False
    _save_registry(args.book, reg)
    return _ok("validate", data={"all_locked": all_ok, "characters": results})


# ---- 解析 @角色名 / @角色名-状态 ----
ATAG_RE = re.compile(r"@([A-Za-z0-9_一-龥]+)(?:-([A-Za-z0-9_一-龥]+))?")


def cmd_rebind(args) -> int:
    reg = _load_registry(args.book)
    chars = {c.get("name"): c for c in reg.get("characters", [])}
    sb_path = Path(args.storyboard)
    if not sb_path.exists():
        return _ok("rebind", error="分镜文件不存在: %s" % sb_path)
    sb = json.loads(sb_path.read_text(encoding="utf-8"))
    shots = sb.get("shots", [])
    problems = []
    used = []
    for sh in shots:
        text = json.dumps(sh, ensure_ascii=False)
        for m in ATAG_RE.findall(text):
            nm, st = m[0], m[1]
            used.append((nm, st))
            c = chars.get(nm)
            if c is None:
                problems.append("分镜 %s 引用未注册角色 @%s" % (sh.get("shotId"), nm))
                continue
            if not c.get("locked"):
                problems.append("角色 @%s 未锁定(front/side/back 未齐),禁止生图" % nm)
                continue
            if st:
                exp = c.get("expressions", {}).get(st)
                if not exp:
                    problems.append("角色 @%s 缺情绪变体 %s(需先生成)" % (nm, st))
    # 去重统计
    uniq = sorted(set(used))
    return _ok("rebind", data={"referenced": uniq, "problems": problems, "passed": not problems})


def cmd_list(args) -> int:
    reg = _load_registry(args.book)
    chars = reg.get("characters", [])
    if not chars:
        return _ok("list", data=[])
    data = [{"name": c.get("name"), "locked": c.get("locked"),
             "tv": c.get("three_view"), "exps": list(c.get("expressions", {}).keys())} for c in chars]
    return _ok("list", data=data)


def main():
    ap = argparse.ArgumentParser(description="角色锁定闸门 + 生图提示词编排")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_w = sub.add_parser("write-prompt"); p_w.add_argument("--book", required=True); p_w.add_argument("--card", required=True)
    p_w.set_defaults(func=cmd_write_prompt)
    p_v = sub.add_parser("validate"); p_v.add_argument("--book", required=True); p_v.set_defaults(func=cmd_validate)
    p_r = sub.add_parser("rebind"); p_r.add_argument("--book", required=True); p_r.add_argument("--storyboard", required=True)
    p_r.set_defaults(func=cmd_rebind)
    p_l = sub.add_parser("list"); p_l.add_argument("--book", required=True); p_l.set_defaults(func=cmd_list)
    args = ap.parse_args()
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return _ok(args.cmd, error="用户中断")


if __name__ == "__main__":
    raise SystemExit(main())
