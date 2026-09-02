#!/usr/bin/env python3
"""
Vital4Living - Autonomous Run & Publish Wrapper
Runs the multi-agent CrewAI writing loop and immediately pushes the resulting
article directly into your Ghost CMS admin panel as a draft in a single step!
Includes robust programmatic HTML monetization injection for affiliate links and PPC units.
"""

import os
import sys
import json
import re
import subprocess

try:
    import requests
except ImportError:
    print("Installing missing dependency: requests...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

try:
    import jwt
except ImportError:
    print("Installing missing dependency: PyJWT...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyJWT"], check=True)
    import jwt

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing missing dependency: beautifulsoup4...")
    subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4"], check=True)
    from bs4 import BeautifulSoup

from datetime import datetime as dt

def load_env():
    env_paths = [
        os.path.expanduser('~/vital4living/.env'),
        os.path.expanduser('~/.env'),
        '.env'
    ]
    env_vars = {}
    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.split('=', 1)
                        env_vars[key.strip()] = val.strip().strip('"').strip("'")
            break
    return env_vars

def get_ghost_jwt(admin_key):
    try:
        key_id, secret = admin_key.split(':')
    except ValueError:
        raise ValueError("Invalid GHOST_ADMIN_API_KEY format. Expected 'ID:SECRET'")
    secret_bytes = bytes.fromhex(secret)
    iat = int(dt.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
    payload = {'iat': iat, 'exp': iat + 5 * 60, 'aud': '/admin/'}
    return jwt.encode(payload, secret_bytes, algorithm='HS256', headers=header)

def extract_json(text):
    """Robustly extracts a JSON block from stdout, ignoring any preambles or warnings."""
    match = re.search(r'(\\{.*\\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try finding any JSON block inside backticks
    code_blocks = re.findall(r'```(?:json)?\\s*(\\{.*?\\})\\s*```', text, re.DOTALL)
    for block in code_blocks:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass
            
    # Try parsing the whole text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    return None

def monetize_html(html_content, inventory):
    """Programmatically injects affiliate links and PPC containers into the HTML."""
    if not BeautifulSoup:
        return html_content
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Calculate word count
    text_content = soup.get_text()
    word_count = len(text_content.split())
    
    # 1. Inject affiliate links into text nodes safely
    for item in inventory:
        if item.get("monetization_type") == "affiliate":
            dest_url = item.get("destination_url")
            keywords = item.get("targeting_keywords", [])
            
            for kw in keywords:
                text_nodes = soup.find_all(string=True)
                matched = False
                for node in text_nodes:
                    if node.parent.name in ['a', 'script', 'style', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        continue
                    if kw.lower() in node.lower():
                        raw_text = str(node)
                        idx = raw_text.lower().find(kw.lower())
                        if idx != -1:
                            before = raw_text[:idx]
                            actual_kw = raw_text[idx:idx+len(kw)]
                            after = raw_text[idx+len(kw):]
                            
                            new_before = soup.new_string(before) if before else None
                            new_link = soup.new_tag('a', href=dest_url)
                            new_link.string = actual_kw
                            new_after = soup.new_string(after) if after else None
                            
                            parent = node.parent
                            index = parent.index(node)
                            node.extract()
                            
                            if new_after:
                                parent.insert(index, new_after)
                            parent.insert(index, new_link)
                            if new_before:
                                parent.insert(index, new_before)
                                
                            matched = True
                            break
                if matched:
                    break
                             
    # 2. Inject PPC blocks programmatically after 2nd paragraph, and at the end if >800 words
    paragraphs = soup.find_all('p')
    ppc_item = next((x for x in inventory if x.get("monetization_type") == "ppc_ad_unit"), None)
    
    if ppc_item and "ad_code_html" in ppc_item:
        ad_code = ppc_item["ad_code_html"]
        
        # Primary block after 2nd paragraph
        if len(paragraphs) >= 2:
            p2 = paragraphs[1]
            ad_soup = BeautifulSoup(ad_code, 'html.parser')
            p2.insert_after(ad_soup)
            
        # Optional secondary block if text exceeds 800 words
        if word_count > 800:
            headers = soup.find_all(['h2', 'h3', 'h4'])
            conclusion_header = None
            for h in headers:
                if 'conclusion' in h.get_text().lower() or 'final thoughts' in h.get_text().lower():
                    conclusion_header = h
                    break
            
            if not conclusion_header and headers:
                conclusion_header = headers[-1]
                
            if conclusion_header:
                ad_soup2 = BeautifulSoup(ad_code, 'html.parser')
                conclusion_header.insert_before(ad_soup2)
            elif len(paragraphs) >= 4:
                ad_soup2 = BeautifulSoup(ad_code, 'html.parser')
                paragraphs[-1].insert_before(ad_soup2)
            
    return str(soup)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_and_publish.py '<JSON_PAYLOAD_STRING>'")
        sys.exit(1)

    payload_str = sys.argv[1]
    
    env = load_env()
    ghost_url = env.get("GHOST_URL")
    admin_key = env.get("GHOST_ADMIN_API_KEY")

    if not ghost_url or not admin_key:
        print("🚨 ERROR: GHOST_URL or GHOST_ADMIN_API_KEY not found in your .env file!")
        sys.exit(1)

    ghost_url = ghost_url.rstrip('/')

    print("=====================================================")
    print("🚀 LAUNCHING AUTONOMOUS WRITING & PUBLISHING PIPELINE")
    print("=====================================================")
    print("1. Running CrewAI Agents (Sierra, Cash, Editor)...")
    
    crew_script = os.path.expanduser('~/vital4living/platform/scripts/webzine-crew-v2.py')
    python_bin = os.path.expanduser('~/vital4living/venv/bin/python3')
    if not os.path.exists(python_bin):
        python_bin = 'venv/bin/python3'
        if not os.path.exists(python_bin):
            python_bin = 'python3'

    try:
        process = subprocess.Popen(
            [python_bin, crew_script, payload_str],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print("🚨 ERROR: CrewAI execution failed!")
            print(stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"🚨 ERROR: Failed to run crew script: {e}")
        sys.exit(1)

    print("2. Extracting & Monetizing Article HTML...")
    draft_data = extract_json(stdout)
    if not draft_data:
        print("🚨 ERROR: Could not extract valid JSON output from the agents!")
        print("Raw output received from agents:")
        print(stdout)
        sys.exit(1)

    meta_title = draft_data.get("meta_title", "New Ski Technical Guide")
    meta_description = draft_data.get("meta_description", "Technical sizing guidelines.")
    html_body = draft_data.get("html_body")
    if not html_body:
        print("🚨 ERROR: Missing html_body in agent JSON!")
        sys.exit(1)

    try:
        inventory = [
            {
                "partner_name": "AvantLink - Salomon Outdoor",
                "monetization_type": "affiliate",
                "targeting_keywords": ["Mondo sizing", "DIN setting", "Salomon", "ski boots"],
                "destination_url": "https://partner.avantlink.com/click?merchantId=123"
            },
            {
                "partner_name": "REI Co-op - Ultralight Gear",
                "monetization_type": "affiliate",
                "targeting_keywords": ["seam failure", "Dyneema", "ripstop", "backpack"],
                "destination_url": "https://rei.sjv.io/c/78910"
            },
            {
                "partner_name": "Premium Google AdSense - Mid Article PPC",
                "monetization_type": "ppc_ad_unit",
                "targeting_keywords": ["fabric denier", "torque specs", "hull geometry"],
                "ad_code_html": '<div class="v4l-ad-container"><!-- AdsByGoogle --><ins class="adsbygoogle" style="display:block; text-align:center;" data-ad-layout="in-article" data-ad-format="fluid" data-ad-client="ca-pub-999999999" data-ad-slot="1111111"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>'
            }
        ]
        try:
            p_load = json.loads(payload_str)
            if "monetization_inventory" in p_load:
                inventory = p_load["monetization_inventory"]
        except Exception:
            pass
        html_body = monetize_html(html_body, inventory)
        print("✔ Programmatic monetization complete!")
    except Exception as e:
        print(f"⚠ Warning: Programmatic monetization failed: {e}")

    title = meta_title.split('|')[0].strip() if '|' in meta_title else meta_title
    slug = title.lower().replace(' ', '-').replace('/', '-').replace(':', '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')

    print(f"📌 Title: {title}")
    print("3. Pushing to Ghost CMS...")
    post_payload = {
        "posts": [
            {
                "title": title,
                "slug": slug,
                "status": "draft",
                "html": html_body,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "visibility": "public"
            }
        ]
    }

    try:
        token = get_ghost_jwt(admin_key)
    except Exception as e:
        print(f"🚨 ERROR: Failed to generate Ghost JWT token: {e}")
        sys.exit(1)

    headers = {
        "Authorization": f"Ghost {token}",
        "Content-Type": "application/json"
    }
    api_url = f"{ghost_url}/ghost/api/admin/posts/?source=html"
    try:
        response = requests.post(api_url, json=post_payload, headers=headers)
        if response.status_code == 201:
            res_json = response.json()
            post = res_json['posts'][0]
            print("\n=====================================================")
            print("🎉 SUCCESS! YOUR ARTICLE IS LIVE ON GHOST!")
            print("=====================================================")
            print(f"🌐 Admin Editor URL: {ghost_url}/ghost/#/editor/post/{post['id']}")
            print("=====================================================")
        else:
            print(f"\n❌ FAILED to push to Ghost: Status Code {response.status_code}")
            print(f"Details: {response.text}")
    except Exception as e:
        print(f"\n🚨 Connection Error: {e}")

if __name__ == "__main__":
    main()
