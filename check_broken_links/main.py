import os
import re
import time
import logging
import json
from functools import lru_cache
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from config import (
    ROOT_DIR, TIMEOUT, MAX_WORKERS, DELAY, USER_AGENT, BLACKLIST,
    LINK_PATTERNS, LOGGING_CONFIG, RETRY_CONFIG, OUTPUT_FILE
)

logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except ValueError:
        return False

def is_blacklisted(url: str, blacklist: list) -> bool:
    return any(domain in url for domain in blacklist)

def normalize_url(url: str) -> str:
    return url.split('#')[0].split('?')[0].strip('"\'<>').rstrip('/')

def youtube_id_to_url(youtube_id: str) -> str:
    return f"https://www.youtube.com/watch?v={youtube_id}"

@lru_cache(maxsize=1024)
def check_url(session: requests.Session, url: str, timeout: int) -> bool:
    if is_blacklisted(url, BLACKLIST):
        logger.debug(f"Ignoring blacklisted URL: {url}")
        return True
    try:
        response = session.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except requests.exceptions.RequestException as e:
        logger.warning(f"⚠️ {url} failed: {str(e)}")
        return False

def extract_links_from_file(file_path: str) -> set:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        links = set()
        for pattern in LINK_PATTERNS:
            for match in re.finditer(pattern, content):
                if pattern == LINK_PATTERNS[1]:  # video::youtube_id
                    youtube_id = match.group(1)
                    url = youtube_id_to_url(youtube_id)
                else:
                    url = match.group(0).replace('link:', '')
                url = normalize_url(url)
                if is_valid_url(url):
                    links.add(url)
                    logger.debug(f"Found URL: {url} (from {file_path})")
        return links
    except Exception as e:
        logger.error(f"Could not read {file_path}: {e}")
        return set()

def process_file(session: requests.Session, file_path: str, delay: float, timeout: int) -> list:
    broken_links = []
    links = extract_links_from_file(file_path)
    logger.info(f"📂 Processing {file_path} ({len(links)} URLs to check)...")
    for url in links:
        time.sleep(delay)
        if not check_url(session, url, timeout):
            logger.warning(f"❌ URL broken: {url}")
            broken_links.append((url, "URL not accessible"))
    return broken_links

def run_check(root_dir: str, max_workers: int, delay: float, timeout: int, output_file: str, blacklist: list) -> None:
    broken_links = {}
    adoc_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.adoc'):
                adoc_files.append(os.path.join(root, file))
    logger.info(f"🔍 Found {len(adoc_files)} .adoc files. Checking URLs...")
    session = requests.Session()
    retries = Retry(**RETRY_CONFIG)
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, session, file, delay, timeout): file for file in adoc_files}
        for future in as_completed(futures):
            file = futures[future]
            try:
                file_broken_links = future.result()
                if file_broken_links:
                    broken_links[file] = file_broken_links
            except Exception as e:
                logger.error(f"Error processing {file}: {e}")
    if not broken_links:
        logger.info("✅ No broken URLs found!")
    else:
        logger.info("❌ Broken URLs found:")
        for file, links in broken_links.items():
            logger.info(f"\n📄 {file}")
            for url, reason in links:
                logger.info(f"  🔗 {url} ({reason})")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(broken_links, f, indent=2, ensure_ascii=False)
    logger.info(f"📊 Results saved to {output_file}.")
