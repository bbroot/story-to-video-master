#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dreamina_gen.py —— 即梦(Dreamina/Seedance) 薄封装调用器
=====================================================
基于真实研读 `chunpu/jimeng-skill` + `yuyou-dev/dreamina-cli-skill` 的 wrapper 范式:
- 稳定 JSON 返回 {ok, command, cli_args, data/error}
- --dry-run 先预览命令不执行
- 路径校验、参考图绑定(图1/图2 顺序)
- 缺失 CLI 时优雅提示安装方式

注意:本机需先安装即梦 CLI:
  curl -fsSL https://jimeng.jianying.com/cli | bash
  dreamina login

子命令:
  text2image   文生图
  image2video  图生视频(单图动画)
  multiframe2video  多帧故事(2-20张)
  multimodal2video  全能参考(图片+文字+可选音视频)
  text2video   文生视频
  query        查询异步任务(submit_id)
  credit       查积分

用法:
  python3 dreamina_gen.py text2image --prompt "..." --ratio 16:9 --dry-run
  python3 dreamina_gen.py multimodal2video --image a.jpg --image b.jpg --prompt "$(cat p.txt)" --ratio 16:9
  python3 dreamina_gen.py query --submit-id xxx
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _which() -> str | None:
    return shutil.which("dreamina")


def _ok(command: str, cli_args: list, data: dict | None = None, error: str | None = None) -> int:
    out = {"ok": error is None, "command": command, "cli_args": cli_args}
    if data is not None:
        out["data"] = data
    if error is not None:
        out["error"] = error
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if error is None else 1


def _build(sub: str, args: argparse.Namespace, dry_run: bool) -> int:
    cli = _which()
    if not cli:
        return _ok(sub, [], error="未检测到 dreamina CLI。请先安装: curl -fsSL https://jimeng.jianying.com/cli | bash ; 然后 dreamina login")
    cli_args = [cli, sub]
    # 通用参数
    if getattr(args, "prompt", None):
        cli_args += ["--prompt", args.prompt]
    if getattr(args, "ratio", None):
        cli_args += ["--ratio", args.ratio]
    if getattr(args, "model_version", None):
        cli_args += ["--model-version", args.model_version]
    if getattr(args, "duration", None):
        cli_args += ["--duration", str(args.duration)]
    if getattr(args, "video_resolution", None):
        cli_args += ["--video-resolution", args.video_resolution]
    # 参考图
    for img in getattr(args, "image", []) or []:
        p = Path(img)
        if not p.exists():
            return _ok(sub, cli_args, error=f"参考图不存在: {img}")
        cli_args += ["--image", str(p.resolve())]
    for vid in getattr(args, "video", []) or []:
        cli_args += ["--video", vid]
    for aud in getattr(args, "audio", []) or []:
        cli_args += ["--audio", aud]
    if getattr(args, "submit_id", None):
        cli_args += ["--submit_id", args.submit_id]

    if dry_run:
        return _ok(sub, cli_args, data={"dry_run": True, "note": "未实际执行,预览命令如上"})
    try:
        r = subprocess.run(cli_args, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return _ok(sub, cli_args, error="执行超时(600s)")
    raw = (r.stdout or "") + (r.stderr or "")
    # 尝试解析 submit_id
    data: dict = {"returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    m = __import__("re").search(r"submit_id[=:\s]+([A-Za-z0-9_-]+)", raw)
    if m:
        data["submit_id"] = m.group(1)
    if r.returncode != 0:
        return _ok(sub, cli_args, error=f"CLI 返回非零: {raw[:500]}")
    return _ok(sub, cli_args, data=data)


def main():
    ap = argparse.ArgumentParser(description="即梦 Dreamina 薄封装")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(p, with_images=True):
        p.add_argument("--prompt", help="提示词(或 '$(cat file.txt)')")
        p.add_argument("--ratio", default="16:9", help="比例 16:9/9:16/1:1")
        p.add_argument("--model-version", help="模型版本")
        p.add_argument("--duration", type=int, help="视频时长(秒)")
        p.add_argument("--video-resolution", help="视频分辨率 720p/1080p")
        p.add_argument("--dry-run", action="store_true")
        if with_images:
            p.add_argument("--image", action="append", default=[])
            p.add_argument("--video", action="append", default=[])
            p.add_argument("--audio", action="append", default=[])

    p_t2i = sub.add_parser("text2image"); add_common(p_t2i, with_images=False)
    p_i2v = sub.add_parser("image2video"); add_common(p_i2v)
    p_mf = sub.add_parser("multiframe2video"); add_common(p_mf)
    p_mm = sub.add_parser("multimodal2video"); add_common(p_mm)
    p_t2v = sub.add_parser("text2video"); add_common(p_t2v, with_images=False)
    p_q = sub.add_parser("query")
    p_q.add_argument("--submit-id", required=True)
    p_q.add_argument("--dry-run", action="store_true")
    p_c = sub.add_parser("credit")
    p_c.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()
    if args.cmd == "query":
        return _build("query_result", args, args.dry_run)
    if args.cmd == "credit":
        cli = _which()
        if not cli:
            return _ok("user_credit", [], error="未检测到 dreamina CLI")
        if args.dry_run:
            return _ok("user_credit", [cli, "user_credit"], data={"dry_run": True})
        r = subprocess.run([cli, "user_credit"], capture_output=True, text=True)
        return _ok("user_credit", [cli, "user_credit"], data={"stdout": r.stdout, "stderr": r.stderr})
    # generation subcommands
    return _build(args.cmd, args, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
