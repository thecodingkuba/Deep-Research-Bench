#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
Midea Deep Research API Client
Tests different endpoint approaches for the Midea AI research API
"""

import argparse
import datetime
import json
import logging
import uuid
from json import JSONDecodeError
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "https://aimpapi.midea.com/t-aigc/airc-deepresearch-sit/"
AUTH_TOKEN = "msk-d60011d8a6905bd6b8d72cb77f847d978e387c253266a1dc5beb1c60f8fddf9b"
ASSISTANT_ID = "xm_deep_search"
DEFAULT_MIP = "liuchen21"

# Request template
REQUEST_TEMPLATE = {
    "request_id": f"test_{uuid.uuid4().hex}",
    "assistant_id": ASSISTANT_ID,
    "content": "ask something!",
    "metadata": {},
    "context": {}
}


def httpx_stream(url, method, timeout=300, **kwargs):
    """Stream HTTP responses line by line"""
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


def parse_streaming_response(response_text):
    """Parse streaming format response and extract content"""
    content_pieces = []
    final_content = None
    
    for line in response_text.split('\n'):
        if line.strip() and line.startswith('data: '):
            try:
                # Extract JSON from data: prefix
                json_str = line[6:]  # Remove 'data: ' prefix
                chunk_data = json.loads(json_str)
                
                # Look for content pieces
                if 'content' in chunk_data:
                    content = chunk_data['content']
                    if isinstance(content, str) and content.strip():
                        content_pieces.append(content)
                    elif isinstance(content, list) and len(content) > 0:
                        # Final structured content
                        for item in content:
                            if item.get('type') == 'text':
                                final_content = item.get('text', '')
                                break
                                
            except json.JSONDecodeError:
                continue
    
    # Return the best content we found
    if final_content:
        return final_content
    elif content_pieces:
        return ''.join(content_pieces)
    else:
        return None


def call_server_run_stream(base_url, thread_id, data, auth=None):
    """Test streaming endpoint approach"""
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    
    api = base_url.rstrip("/") + f"/v1/threads/{thread_id}/runs_stream"
    print(f"Testing streaming endpoint: {api}")
    
    lines_count = 0
    content_lines = []
    
    try:
        for delta in httpx_stream(api, "post", json=data, headers=headers, timeout=6000):
            lines_count += 1
            if lines_count <= 5:  # Show first 5 lines
                print(f"Stream line {lines_count}: {delta}")
            content_lines.append(delta)
        
        print(f"Total streaming lines received: {lines_count}")
        if lines_count > 5:
            print("Last few lines:")
            for i, line in enumerate(content_lines[-3:]):
                print(f"  Line {lines_count-2+i}: {line}")
        
        # Try to extract actual content from streaming
        actual_content_found = False
        for line in content_lines:
            if line and 'data:' in line and 'message_chunk' not in line and len(line) > 20:
                print(f"Potential content line: {line}")
                actual_content_found = True
        
        if not actual_content_found:
            print("No obvious content found in streaming!")
            
    except Exception as e:
        print(f"Streaming error: {e}")
        return None

def call_server_run_callback(base_url, thread_id, data, auth=None):
    """Test callback endpoint and fallback to streaming with parsing"""
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    
    # Try the callback endpoint first
    api_callback = base_url.rstrip("/") + f"/v1/threads/{thread_id}/runs_callback"
    print(f"🔍 Testing callback endpoint: {api_callback}")
    
    try:
        timeout = httpx.Timeout(6000)
        with httpx.Client(timeout=timeout) as client:
            resp = client.request("post", api_callback, json=data, headers=headers)
            resp.raise_for_status()
            
            print("✅ Callback endpoint works!")
            content_type = resp.headers.get('content-type', '')
            print(f"Response content-type: {content_type}")
            print(f"Response length: {len(resp.text)} characters")
            
            # Try to parse as JSON first
            try:
                json_response = resp.json()
                if isinstance(json_response, dict):
                    # Look for common response fields
                    for field in ['content', 'message', 'response', 'text', 'result']:
                        if field in json_response:
                            print(f"Found '{field}' field in JSON response!")
                            return json_response[field]
                    
                    print("JSON response structure:")
                    print(json.dumps(json_response, indent=2)[:500] + "...")
                    return str(json_response)
                else:
                    print("Non-dict JSON response:")
                    return str(json_response)
                    
            except json.JSONDecodeError:
                print("Response is not JSON, returning as text")
                return resp.text
                
    except Exception as e:
        print(f"❌ Callback endpoint failed: {e}")
        print("Falling back to streaming endpoint...")
    
    # Fallback to streaming endpoint with parsing
    api_stream = base_url.rstrip("/") + f"/v1/threads/{thread_id}/runs_stream"
    print(f"🔄 Using streaming endpoint: {api_stream}")
    
    try:
        timeout = httpx.Timeout(6000)
        with httpx.Client(timeout=timeout) as client:
            resp = client.request("post", api_stream, json=data, headers=headers)
            resp.raise_for_status()
            
            content_type = resp.headers.get('content-type', '')
            print(f"Response content-type: {content_type}")
            print(f"Response length: {len(resp.text)} characters")
            
            # Parse streaming format
            result = parse_streaming_response(resp.text)
            
            if result:
                print("=== EXTRACTED CONTENT ===")
                print(f"Length: {len(result)} characters")
                print(result[:200] + "..." if len(result) > 200 else result)
                print("=" * 50)
                return result
            else:
                print("No content found in response")
                print("Raw response sample:")
                print(resp.text[:500] + "..." if len(resp.text) > 500 else resp.text)
                return None
                
    except Exception as e:
        print(f"Error with streaming endpoint: {e}")
        return None


def test_client(base_url, assistant_id, request_text, mip, auth=None):
    """Test the API client with different approaches"""
    data = REQUEST_TEMPLATE.copy()
    data["assistant_id"] = assistant_id
    data["content"] = request_text
    data["metadata"]["mip"] = mip
    data["request_id"] = f"test_{uuid.uuid4().hex}"
    
    thread_id = "69e67268526811f08f9d24eb1607fe62"
    
    print("=== Testing API Client ===")
    print(f"Request: {request_text}")
    print(f"Thread ID: {thread_id}")
    
    result = call_server_run_callback(base_url, thread_id, data, auth=auth)
    
    if result:
        print(f"\n✅ SUCCESS! Extracted {len(result)} characters of content")
        return result
    else:
        print("\n❌ Failed to extract content")
        return None


def test_online_stream(base_url, request_json, auth=None):
    """Test streaming approach"""
    thread_id = datetime.date.today().isoformat()
    call_server_run_stream(base_url, thread_id, request_json, auth=auth)


def test_online_callback(base_url, request_json, auth=None):
    """Test callback approach"""
    thread_id = datetime.date.today().isoformat()
    call_server_run_callback(base_url, thread_id, request_json, auth=auth)


def main():
    """Main function to run the API client"""
    parser = argparse.ArgumentParser(description="Test Midea Deep Research API")
    parser.add_argument("--assistant_id", default=ASSISTANT_ID, help="Assistant ID to use")
    parser.add_argument("--mip", default=DEFAULT_MIP, help="MIP value for metadata")
    parser.add_argument("--request_text", default="what is one plus one", 
                       help="Text to send to the API")
    parser.add_argument("--request_json", default=None, 
                       help="JSON request (overrides request_text)")

    args = parser.parse_args()

    # API configuration
    base_url = BASE_URL
    auth = AUTH_TOKEN
    
    print(f"🚀 Midea Deep Research API Client")
    print(f"Base URL: {base_url}")
    print(f"Assistant ID: {args.assistant_id}")
    print("-" * 60)

    if args.request_json:
        print("Using JSON request mode")
        test_online_callback(base_url, request_json=json.loads(args.request_json), auth=auth)
    else:
        print("Using text request mode")
        result = test_client(
            base_url=base_url,
            assistant_id=args.assistant_id,
            request_text=args.request_text,
            mip=args.mip,
            auth=auth
        )
        
        if result:
            print(f"\n📋 Final Result Preview:")
            preview = result[:300] + "..." if len(result) > 300 else result
            print(preview)


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
