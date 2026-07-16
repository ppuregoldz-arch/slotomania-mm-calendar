#!/usr/bin/env python3
"""
Extract JSON examples from Aviator HLD wiki content
"""
import json
import re
import sys

def extract_json_examples(content):
    """Extract all JSON examples from HTML content"""
    # Look for JSON objects in the content
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    
    # Also look for specific patterns around event examples
    event_patterns = [
        r'FrozenEvent.*?\{.*?\}',
        r'ReadyToPlayEvent.*?\{.*?\}', 
        r'RoundStartedEvent.*?\{.*?\}',
        r'RoundEndedEvent.*?\{.*?\}',
        r'UserRewardedEvent.*?\{.*?\}',
        r'OfferDeclinedEvent.*?\{.*?\}'
    ]
    
    found_jsons = []
    
    # Search for JSON objects
    matches = re.findall(json_pattern, content, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and 'userId' in str(match):
                found_jsons.append(match)
        except:
            continue
    
    # Search for event-specific patterns
    for pattern in event_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        found_jsons.extend(matches)
    
    return found_jsons

if __name__ == "__main__":
    # Read the content from the agent tools file
    import os
    
    file_path = r"C:\Users\mayed\.cursor\projects\c-Users-mayed-OneDrive-Playtika-Ltd-Desktop-My-Cursor-Projects-General-31-03\agent-tools\43635196-6ba1-4d13-a87a-0f5f8ce58c19.txt"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Searching for JSON examples in HLD content...")
    
    # Extract JSON examples
    jsons = extract_json_examples(content)
    
    if jsons:
        print(f"Found {len(jsons)} JSON examples:")
        for i, json_example in enumerate(jsons, 1):
            print(f"\n--- Example {i} ---")
            print(json_example[:500] + "..." if len(json_example) > 500 else json_example)
    else:
        print("No JSON examples found. Let's search for other patterns...")
        
        # Search for other patterns that might contain examples
        patterns_to_try = [
            r'"eventType"\s*:\s*"[^"]*"',
            r'"userId"\s*:\s*\d+',
            r'FROZEN.*?eventType',
            r'gameId.*?userId',
            r'example.*?\{',
            r'\{.*?eventType.*?\}'
        ]
        
        for pattern in patterns_to_try:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                print(f"\nFound matches for pattern '{pattern}':")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"  {match[:200]}...")