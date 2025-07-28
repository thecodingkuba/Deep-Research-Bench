#!/usr/bin/env python
# -*- coding:utf-8 _*-
# @Time    : 2025-06-16
# @Author  : lc
# @File    : test_client_run.py
import argparse
import datetime
import json
import logging
import uuid
from json import JSONDecodeError
import httpx

def httpx_stream(url, method, timeout=300, **kwargs):
    timeout = httpx.Timeout(timeout or 300)
    try:
        with httpx.Client(timeout=timeout) as client:
            with client.stream(method, url, **kwargs) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    yield line
    except Exception as e:
        raise e


text_request_template = {
    "request_id": f"test_{uuid.uuid4().hex}",
    "assistant_id": "xm_deep_search",
    "content": "打开客厅风扇宝宝风",
    "metadata": {},
    "context": {}
}


def call_server_run_stream(base_url, thread_id, data, auth=None):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    api = base_url.rstrip("/") + f"/v1/threads/{thread_id}/runs_stream"
    print(f"call {api} with json {data} headers {headers}")
    for delta in httpx_stream(api, "post", json=data, headers=headers, timeout=6000):
        print(delta)


def test_client(base_url, assistant_id, request_text, mip, auth=None):
    data = text_request_template.copy()
    data["assistant_id"] = assistant_id
    data["content"] = request_text
    data["metadata"]["mip"] = mip
    thread_id = "69e67268526811f08f9d24eb1607fe62"

    call_server_run_stream(base_url, thread_id, data, auth=auth)


def test_online(base_url, request_json, auth=None):
    thread_id = datetime.date.today().isoformat()
    call_server_run_stream(base_url, thread_id, request_json, auth=auth)


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description="Run the Client")
    parser.add_argument(
        "--assistant_id",
        default="xm_deep_search",
    )
    parser.add_argument(
        "--mip",
        default="liuchen21",
    )
    parser.add_argument(
        "--request_text",
        help="request_text",
        default="",
    )
    parser.add_argument(
        "--request_json",
        help="request_json",
        default=None,
    )

    args = parser.parse_args()

    base_url = "https://aimpapi.midea.com/t-aigc/airc-deepresearch-sit/"
    auth = "msk-d60011d8a6905bd6b8d72cb77f847d978e387c253266a1dc5beb1c60f8fddf9b"
    # base_url = "https://apiuat.midea.com/t-aigc/aimp-airc-deepresearch/"
    # auth = "msk-230b26764bcba897b144ffffac905ad83cd0d6e2a430ab5a79513a4056d02fa7"

    # base_url = "https://apiuat.midea.com/t-aigc/sit/airc-magents/"
    # auth = "SIT-20250625134505-9d731cc2"

    if args.request_json:
        test_online(base_url, request_json=json.loads(args.request_json), auth=auth)
    else:
        test_client(base_url, assistant_id=args.assistant_id, request_text=args.request_text, mip=args.mip, auth=auth)
