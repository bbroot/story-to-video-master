#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runninghub_gen.py —— RunningHub(runninghub.cn) 标准 OpenAPI 封装
==============================================================
基于官方契约(https://github.com/HM-RunningHub/ComfyUI_RH_OpenAPI/blob/main/developer-kit/rh-api-contract.md)
与无依赖 Python 客户端(developer-kit/examples/python/client.py)的真实实现:

Base URL: https://www.runninghub.cn/openapi/v2  (境外 https://www.runninghub.ai/openapi/v2)
鉴权: Authorization: Bearer <RH_API_KEY>  +  Content-Type: application/json
三步: ① media/upload/binary 上传(如需) → ② POST {endpoint} 提交 → {taskId} → ③ POST /query 轮询
真实端点(模型注册表):
    rhart-image-v1/text-to-image           文生图
    rhart-image-v1/edit                    图生图
    rhart-video-s-official/image-to-video-realistic  图生视频(Sora2 官方支持真人)
    seedance2.0/... / seedance2.0-fast/... / seedance2.0-mini/...   Seedance 2.0 系列
返回(SUCCESS 终态): {"status":"SUCCESS","results":[{"url":"...","outputType":"video"}]}
参数规则: LIST 取声明枚举(如 duration 仅 4/8/12); 必填必须存在; 禁止臆造枚举/默认值
重试: 提交/上传最多 3 次指数退避; 仅重试网络错误/429/5xx; 不重试 400/401/403/余额不足/审核类
轮询间隔 5s, 最长 30 分钟; 超时返回 taskId 供 call-record 自查

子命令:
  upload       上传本地图片/视频 → 返回 download_url
  generate     提交任务 → 返回 taskId(可选 --wait 轮询)
  query        轮询任务状态

用法:
  python3 runninghub_gen.py upload --file 角色/林渡.png
  python3 runninghub_gen.py generate --endpoint seedance2.0/文生视频 --prompt "..." --ratio 16:9 --duration 8 --wait
  python3 runninghub_gen.py query --task-id <id> --wait
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE = "https://www.runninghub.cn/openapi/v2"
POLL_INTERVAL = 5
POLL_TIMEOUT = 1800  # 30 分钟


def _base() -> str:
    return os.environ.get("RH_API_BASE_URL") or DEFAULT_BASE


def _headers() -> dict:
    key = os.environ.get("RH_API_KEY")
    if not key:
        raise RuntimeError("未设置环境变量 RH_API_KEY（https://www.runninghub.cn/enterprise-api/sharedApi 获取）")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _url(path: str) -> str:
    return _base().rstrip("/") + path


def _post_json(path: str, payload: dict | None = None, raw_body: bytes | None = None, headers: dict | None = None) -> dict:
    data = raw_body if raw_body is not None else (json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else b"")
    h = headers or _headers()
    req = urllib.request.Request(_url(path), data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _retry(fn, max_attempts=3):
    last = None
    for i in range(max_attempts):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            # 不重试 400/401/403/402 余额/审核; 重试 429/5xx
            if e.code in (400, 401, 403, 402):
                raise
            last = e
            time.sleep((2 ** i) * 1.0)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last = e
            time.sleep((2 ** i) * 1.0)
    raise last if last else RuntimeError("重试失败")


def _ok(command: str, data: dict | None = None, error: str | None = None) -> int:
    out = {"ok": error is None, "command": command}
    if data is not None:
        out["data"] = data
    if error is not None:
        out["error"] = error
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if error is None else 1


def _multipart_upload(file_path: Path) -> dict:
    boundary = "----rhgen%d" % int(time.time() * 1000)
    with file_path.open("rb") as f:
        raw = f.read()
    ext = file_path.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp",
            ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}.get(ext, "application/octet-stream")
    body = b""
    body += ("--%s\r\n" % boundary).encode()
    body += ('Content-Disposition: form-data; name="file"; filename="%s"\r\n' % file_path.name).encode()
    body += ("Content-Type: %s\r\n\r\n" % mime).encode()
    body += raw
    body += b"\r\n"
    body += ("--%s--\r\n" % boundary).encode()
    h = _headers()
    h.pop("Content-Type", None)
    h["Content-Type"] = "multipart/form-data; boundary=%s" % boundary
    return _retry(lambda: _post_json("/media/upload/binary", raw_body=body, headers=h))


def cmd_upload(args) -> int:
    try:
        p = Path(args.file)
        if not p.exists():
            return _ok("upload", error="文件不存在: %s" % args.file)
        resp = _multipart_upload(p)
        return _ok("upload", data=resp)
    except Exception as e:  # noqa
        return _ok("upload", error=str(e))


def _build_payload(args) -> dict:
    payload = {}
    if args.prompt:
        payload["prompt"] = args.prompt
    if args.ratio:
        payload["aspectRatio"] = args.ratio
    if args.duration is not None:
        payload["duration"] = args.duration  # 仅 4/8/12
    if args.extra:
        # 允许 --extra '{"key":"val"}' 透传(供 asset_ids / real_person_mode 等)
        try:
            payload.update(json.loads(args.extra))
        except Exception as e:  # noqa
            raise RuntimeError("解析 --extra JSON 失败: %s" % e)
    if args.endpoint.startswith(("seedance2.0",)) and args.asset_ids:
        # Seedance 2.0 参考素材(图生/多模态): asset_ids 接受逗号/换行/JSON数组
        payload.setdefault("asset_ids", args.asset_ids)
    return payload


def cmd_generate(args) -> int:
    try:
        if not args.endpoint:
            return _ok("generate", error="缺少 --endpoint（如 seedance2.0/文生视频）")
        payload = _build_payload(args)
        # 提交(带重试)
        def _submit():
            return _post_json("/" + args.endpoint.lstrip("/"), payload)
        resp = _retry(_submit)
        task_id = resp.get("taskId") or resp.get("task_id")
        if not args.wait or not task_id:
            return _ok("generate", data={"taskId": task_id, "raw": resp})
        return cmd_query_poll(task_id, resp)
    except Exception as e:  # noqa
        return _ok("generate", error=str(e))


def _poll_once(task_id: str) -> dict:
    return _post_json("/query", {"taskId": task_id})


def _extract_results(resp: dict) -> list:
    results = []
    # 兼容多种返回形态
    for key in ("results", "result", "outputs", "data"):
        v = resp.get(key)
        if isinstance(v, list):
            results = v
            break
    urls = []
    for r in results:
        if isinstance(r, dict):
            u = r.get("url") or r.get("outputUrl") or r.get("downloadUrl")
            if u:
                urls.append(u)
    return urls


def cmd_query_poll(task_id: str, first_resp: dict | None = None) -> int:
    deadline = time.time() + POLL_TIMEOUT
    last = first_resp
    while time.time() < deadline:
        resp = _poll_once(task_id)
        last = resp
        status = (resp.get("status") or "").upper()
        if status in ("SUCCESS",):
            return _ok("query", data={"done": True, "status": status, "result_urls": _extract_results(resp), "raw": resp})
        if status in ("FAILED", "CANCEL", "CANCELED"):
            return _ok("query", data={"done": True, "status": status, "raw": resp}, error="任务终态: %s" % status)
        time.sleep(POLL_INTERVAL)
    return _ok("query", data={"done": False, "taskId": task_id,
                              "note": "轮询超时(30min)，请到 https://www.runninghub.cn/call-api/call-record 自查",
                              "raw": last})


def cmd_query(args) -> int:
    try:
        if not args.task_id:
            return _ok("query", error="缺少 --task-id")
        if not args.wait:
            resp = _poll_once(args.task_id)
            return _ok("query", data={"status": resp.get("status"), "result_urls": _extract_results(resp), "raw": resp})
        return cmd_query_poll(args.task_id)
    except Exception as e:  # noqa
        return _ok("query", error=str(e))


def main():
    ap = argparse.ArgumentParser(description="RunningHub 标准 OpenAPI 封装")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_up = sub.add_parser("upload"); p_up.add_argument("--file", required=True); p_up.set_defaults(func=cmd_upload)
    p_g = sub.add_parser("generate")
    p_g.add_argument("--endpoint", required=True, help="如 seedance2.0/文生视频")
    p_g.add_argument("--prompt"); p_g.add_argument("--ratio", default="16:9"); p_g.add_argument("--duration", type=int)
    p_g.add_argument("--asset-ids", help="Seedance 参考素材(逗号/换行/JSON数组)")
    p_g.add_argument("--extra", help='透传 JSON, 如 {"real_person_mode":false}')
    p_g.add_argument("--wait", action="store_true")
    p_g.set_defaults(func=cmd_generate)
    p_q = sub.add_parser("query")
    p_q.add_argument("--task-id", required=True); p_q.add_argument("--wait", action="store_true")
    p_q.set_defaults(func=cmd_query)

    args = ap.parse_args()
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return _ok(args.cmd, error="用户中断")


if __name__ == "__main__":
    raise SystemExit(main())
