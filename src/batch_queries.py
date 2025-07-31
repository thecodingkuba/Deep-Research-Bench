#!/usr/bin/env python
# -*- coding:utf-8 _*-
# Batch process all queries from query.jsonl using the working Midea API
import json
import time
import uuid
from pathlib import Path
import httpx
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# API Configuration
BASE_URL = "https://aimpapi.midea.com/t-aigc/airc-deepresearch-sit/"
AUTH_TOKEN = "msk-d60011d8a6905bd6b8d72cb77f847d978e387c253266a1dc5beb1c60f8fddf9b"
ASSISTANT_ID = "xm_deep_search"
MIP = "liuchen21"

# File paths
QUERY_FILE = "../data/prompt_data/query.jsonl"
OUTPUT_FILE = "../data/test_data/raw_data/midea.jsonl"

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
            
            # Return the best content found
            if final_content:
                return final_content
            elif content_pieces:
                return ''.join(content_pieces)
            else:
                return None
                
    except Exception as e:
        print(f"Error calling API: {e}")
        return None

def load_queries(file_path):
    """Load queries from JSONL file"""
    queries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line))
    return queries

def save_result(result, output_file):
    """Append result to output file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')

def process_queries():
    """Process all queries and save results"""
    # Load queries
    query_file_path = Path(__file__).parent / QUERY_FILE
    output_file_path = Path(__file__).parent / OUTPUT_FILE
    
    print(f"Loading queries from: {query_file_path}")
    queries = load_queries(query_file_path)
    print(f"Loaded {len(queries)} queries")
    
    # Process each query
    processed = 0
    failed = 0
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Processing query {i}/{len(queries)}")
        print(f"ID: {query['id']} | Topic: {query['topic']} | Language: {query['language']}")
        print(f"Query: {query['prompt'][:100]}...")
        
        # Call API
        start_time = time.time()
        response = call_midea_api(query['prompt'])
        end_time = time.time()
        
        # Prepare result in the specified format
        result = {
            "id": query['id'],
            "prompt": query['prompt'],
            "article": response if response else ""
        }
        
        if response:
            print(f"✅ SUCCESS - Got {len(response)} characters in {round(end_time - start_time, 2)}s")
            processed += 1
        else:
            print(f"❌ FAILED - No response received")
            failed += 1
        
        # Save result
        save_result(result, output_file_path)
        
        # Small delay to be respectful to the API
        if i < len(queries):
            print("Waiting 2 seconds before next query...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE!")
    print(f"Total queries: {len(queries)}")
    print(f"Successful: {processed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(processed/len(queries)*100):.1f}%")
    print(f"Results saved to: {output_file_path}")

if __name__ == "__main__":
    print("🚀 Starting batch processing of Deep Research Bench queries...")
    process_queries()
