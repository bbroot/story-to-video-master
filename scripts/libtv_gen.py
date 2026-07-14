#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
libtv_gen.py —— LibTV(liblib.tv) 传话层封装
===========================================
基于官方 OpenClaw Skill 包真实 API（github.com/libtv-labs/libtv-skills）:
- 会话式 agent-im OpenAPI，Agent 只做"传话"，分镜/模型选择由 LibTV 后端完成
- 鉴权: Authorization: Bearer <LIBTV_ACCESS_KEY>
- 端点(默认 https://im.liblib.tv，可经 OPENAPI_IM_BASE / IM_BASE_URL 覆盖):
    POST /openapi/session            创建会话/发消息  {sessionId?, message?}
    GET  /openapi/session/:id        查询会话消息列表
    POST /openapi/session/change-project  切换项目
    POST /openapi/file/upload        上传图片/视频(multipart file, ≤200MB)
- 结果: 轮询(GET session)每 8s；assistant 消息含 URL 即完成；超时去 projectUrl 画布看

设计原则(遵循官方 SKILL.md): 用户侧不做创作，只做传话。
  ① 读 LIBTV_ACCESS_KEY  ② 上传本地素材拿 OSS URL  ③ 把原始描述+URL 原样交给 session
  ④ 8s 轮询 query  ⑤ 完成下载 + 返回结果URL + projectUrl

子命令:
  upload    上传本地图片/视频 → 返回 OSS URL
  session   创建会话并(可选)发送消息 → 返回 sessionId + projectUrl
  query     轮询会话消息 → 返回最新消息(含结果 URL)
  download  批量下载会话中的结果 URL → 本地文件

用法:
  python3 libtv_gen.py upload --file 角色/林渡.png
  python3 libtv_gen.py session --message "把这段小说改成分镜并生成视频: …" --image-url "https://libtv-res…/林渡.png"
  python3 libtv_gen.py query --session-id <id> --wait
  python3 libtv_gen.py download --session-id <id> --output-dir out/
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE = "https://im.liblib.tv"
POLL_INTERVAL = 8
POLL_TIMEOUT = 180  # 3 分钟无结果则提示去画布


def _base() -> str:
    return os.environ.get("OPENAPI_IM_BASE") or os.environ.get("IM_BASE_URL") or DEFAULT_BASE


def _headers() -> dict:
    key = os.environ.get("LIBTV_ACCESS_KEY")
    if not key:
        raise RuntimeError("未设置环境变量 LIBTV_ACCESS_KEY（LibTV 网页「LibTV Skills → 复制 access key」获取）")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _url(path: str) -> str:
    return _base().rstrip("/") + path


def _post_json(path: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(_url(path), data=data, headers=_headers(), method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(path: str) -> dict:
    req = urllib.request.Request(_url(path), headers=_headers(), method="GET")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ok(command: str, data: dict | None = None, error: str | None = None) -> int:
    out = {"ok": error is None, "command": command}
    if data is not None:
        out["data"] = data
    if error is not None:
        out["error"] = error
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if error is None else 1


# ---- multipart upload (pure stdlib) ----
def _multipart_upload(path: str, file_path: Path) -> dict:
    boundary = "----libtvgen%d" % int(time.time() * 1000)
    # 探测 mime
    ext = file_path.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp",
            ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}.get(ext, "application/octet-stream")
    with file_path.open("rb") as f:
        raw = f.read()
    if len(raw) > 200 * 1024 * 1024:
        raise RuntimeError("文件超过 200MB 上限: %s" % file_path)
    body = b""
    body += ("--%s\r\n" % boundary).encode()
    body += ('Content-Disposition: form-data; name="file"; filename="%s"\r\n' % file_path.name).encode()
    body += ("Content-Type: %s\r\n\r\n" % mime).encode()
    body += raw
    body += b"\r\n"
    body += ("--%s--\r\n" % boundary).encode()
    headers = _headers()
    headers.pop("Content-Type", None)
    headers["Content-Type"] = "multipart/form-data; boundary=%s" % boundary
    req = urllib.request.Request(_url(path), data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_upload(args) -> int:
    try:
        p = Path(args.file)
        if not p.exists():
            return _ok("upload", error="文件不存在: %s" % args.file)
        resp = _multipart_upload("/openapi/file/upload", p)
        return _ok("upload", data=resp)
    except Exception as e:  # noqa
        return _ok("upload", error=str(e))


def cmd_session(args) -> int:
    try:
        message = args.message or ""
        if args.image_url:
            # 把 OSS URL 原样附在消息里（传话层：不润色、不扩写）
            message = (message + "\n\n参考素材: " + " ".join(args.image_url)).strip()
        payload = {}
        if args.session_id:
            payload["sessionId"] = args.session_id
        if message:
            payload["message"] = message
        resp = _post_json("/openapi/session", payload)
        return _ok("session", data=resp)
    except Exception as e:  # noqa
        return _ok("session", error=str(e))


def _extract_urls(messages: list) -> list:
    urls = []
    for m in messages:
        if isinstance(m, dict) and m.get("role") == "assistant":
            content = m.get("content") or ""
            for u in re.findall(r"https?://[^\s)\"']+", content):
                urls.append(u)
    return urls


def cmd_query(args) -> int:
    try:
        if not args.session_id:
            return _ok("query", error="缺少 --session-id")
        if not args.wait:
            resp = _get_json("/openapi/session/%s" % args.session_id)
            urls = _extract_urls(resp.get("data", {}).get("messages", []) if isinstance(resp.get("data"), dict) else [])
            return _ok("query", data={"raw": resp, "result_urls": urls})
        # 轮询
        deadline = time.time() + (args.timeout or POLL_TIMEOUT)
        last_seq = 0
        while time.time() < deadline:
            resp = _get_json("/openapi/session/%s" % args.session_id)
            data = resp.get("data", {})
            messages = data.get("messages", []) if isinstance(data, dict) else []
            urls = _extract_urls(messages)
            if urls:
                return _ok("query", data={"done": True, "result_urls": urls, "projectUrl": data.get("projectUrl"), "raw": resp})
            time.sleep(POLL_INTERVAL)
        return _ok("query", data={"done": False, "note": "3 分钟无结果，请前往画布查看", "projectUrl": _project_url(args.session_id)})
    except Exception as e:  # noqa
        return _ok("query", error=str(e))


def _project_url(session_id: str) -> str:
    return "%s/openapi/session/%s" % (_base(), session_id)


def cmd_download(args) -> int:
    try:
        if not args.session_id:
            return _ok("download", error="缺少 --session-id")
        resp = _get_json("/openapi/session/%s" % args.session_id)
        data = resp.get("data", {})
        messages = data.get("messages", []) if isinstance(data, dict) else []
        urls = _extract_urls(messages)
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for i, u in enumerate(urls):
            ext = ".bin"
            m = re.search(r"\.([a-z0-9]{2,5})(?:[?#]|$)", u, re.I)
            if m:
                ext = "." + m.group(1).lower()
            fn = "%s_%d%s" % (args.prefix or "libtv", i, ext)
            dst = out_dir / fn
            req = urllib.request.Request(u, headers={})
            with urllib.request.urlopen(req, timeout=300) as r, dst.open("wb") as f:
                f.write(r.read())
            saved.append(str(dst))
        return _ok("download", data={"saved": saved, "count": len(saved)})
    except Exception as e:  # noqa
        return _ok("download", error=str(e))


def main():
    ap = argparse.ArgumentParser(description="LibTV 传话层封装")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_up = sub.add_parser("upload"); p_up.add_argument("--file", required=True); p_up.set_defaults(func=cmd_upload)
    p_se = sub.add_parser("session")
    p_se.add_argument("--message"); p_se.add_argument("--session-id"); p_se.add_argument("--image-url", action="append", default=[])
    p_se.set_defaults(func=cmd_session)
    p_q = sub.add_parser("query")
    p_q.add_argument("--session-id"); p_q.add_argument("--wait", action="store_true"); p_q.add_argument("--timeout", type=int)
    p_q.set_defaults(func=cmd_query)
    p_d = sub.add_parser("download")
    p_d.add_argument("--session-id", required=True); p_d.add_argument("--output-dir", default="output/libtv")
    p_d.add_argument("--prefix"); p_d.set_defaults(func=cmd_download)

    args = ap.parse_args()
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return _ok(args.cmd, error="用户中断")


if __name__ == "__main__":
    raise SystemExit(main())
