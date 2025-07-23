#!/usr/bin/env python
# -*- coding:utf-8 _*-
# Run a single query using the Midea API and display the result
import json
import time
import uuid
from pathlib import Path
import httpx
from datetime import datetime

# Add current directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# API Configuration
BASE_URL = "https://aimpapi.midea.com/t-aigc/airc-deepresearch-sit/"
AUTH_TOKEN = "msk-d60011d8a6905bd6b8d72cb77f847d978e387c253266a1dc5beb1c60f8fddf9b"
ASSISTANT_ID = "xm_deep_search"
MIP = "liuchen21"

text_request_template = {
    "request_id": f"test_{uuid.uuid4().hex}",
    "assistant_id": "xm_deep_search",
    "content": "ask something!",
    "metadata": {},
    "context": {}
}

def call_midea_api(query_text, thread_id=None):
    """Call Midea API with the working configuration"""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Use working endpoint
    api = BASE_URL.rstrip("/") + f"/v1/threads/{thread_id or uuid.uuid4().hex}/runs_stream"
    
    # Prepare request data
    data = text_request_template.copy()
    data["assistant_id"] = ASSISTANT_ID
    data["content"] = query_text
    data["metadata"]["mip"] = MIP
    data["request_id"] = f"batch_{uuid.uuid4().hex}"
    
    try:
        timeout = httpx.Timeout(6000)  # 100 minutes timeout for complex queries
        with httpx.Client(timeout=timeout) as client:
            resp = client.request("post", api, json=data, headers=headers)
            resp.raise_for_status()
            
            response_text = resp.text
            
            # Parse streaming format to extract content
            content_pieces = []
            final_content = None
            
            for line in response_text.split('\n'):
                if line.strip() and line.startswith('data: '):
                    try:
                        json_str = line[6:]  # Remove 'data: ' prefix
                        chunk_data = json.loads(json_str)
                        
                        if 'content' in chunk_data:
                            content = chunk_data['content']
                            if isinstance(content, str) and content.strip():
                                content_pieces.append(content)
                            elif isinstance(content, list) and len(content) > 0:
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
                
    except Exception as e:
        print(f"Error calling API: {e}")
        return None

def run_single_query(query_text):
    """Run a single query and display the result in the terminal"""
    print(f"\n🚀 Running query: {query_text}")
    print(f"{'='*60}")
    
    # Call API
    start_time = time.time()
    response = call_midea_api(query_text)
    end_time = time.time()
    
    # Display results
    if response:
        print(f"\n✅ SUCCESS - Got response in {round(end_time - start_time, 2)}s")
        print(f"Response length: {len(response)} characters")
        print(f"\n{'='*60}")
        print("RESPONSE:")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}")
    else:
        print(f"\n❌ FAILED - No response received")
    
    return response

if __name__ == "__main__":
    # Get input from the user
    query_text = input("Enter your query: ").strip()
    
    if query_text:
        run_single_query(query_text)
    else:
        print("No query provided. Exiting.")