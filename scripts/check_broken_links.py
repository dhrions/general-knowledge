import os
import re
import time
import warnings
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
ROOT_DIR = "../docs/modules"
IGNORE_LOCAL = False
TIMEOUT = 15
MAX_WORKERS = 5  # Réduit pour éviter les blocages
DELAY = 0.5  # Délai entre les requêtes (secondes)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
BLACKLIST = []  # Ex: ["wikipedia.org"] pour ignorer certains domaines

# Désactiver les warnings SSL (mais garder la vérification)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Patterns pour extraire les liens
LINK_PATTERNS = [
    r'link:([^\s]+?)\[',
    r'https?://[^\s]+',
    r'xref:([^\s]+?)\[',
    r'image::([^\s]+?)\[',
    r'video::([^\s]+?)\[',
]

def is_local_link(link):
    return not link.startswith(('http://', 'https://'))

def is_blacklisted(url):
    return any(domain in url for domain in BLACKLIST)

def check_local_path(file_path, link):
    link = link.split('#')[0]
    abs_path = os.path.normpath(os.path.join(os.path.dirname(file_path), link))
    return os.path.exists(abs_path)

def check_url(session, url):
    if is_blacklisted(url):
        return True  # Ignorer les domaines blacklistés

    try:
        # Utiliser GET au lieu de HEAD pour plus de compatibilité
        response = session.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            stream=True,  # Ne pas télécharger le corps de la réponse
        )
        return response.status_code < 400
    except requests.exceptions.RequestException as e:
        print(f"⚠️  {url} failed: {str(e)}")
        return False

def extract_links_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        links = []
        for pattern in LINK_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                link = match.strip('"\'<>')
                links.append(link)
        return links
    except Exception as e:
        print(f"⚠️  Could not read {file_path}: {e}")
        return []

def process_file(session, file_path):
    broken_links = []
    links = extract_links_from_file(file_path)
    for link in links:
        if is_local_link(link):
            if not IGNORE_LOCAL and not check_local_path(file_path, link):
                broken_links.append((link, "Local path not found"))
        else:
            time.sleep(DELAY)  # Délai pour éviter les blocages
            if not check_url(session, link):
                broken_links.append((link, "URL not accessible"))
    return broken_links

def main():
    broken_links = {}
    adoc_files = []
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith('.adoc'):
                adoc_files.append(os.path.join(root, file))

    print(f"🔍 Found {len(adoc_files)} .adoc files. Checking links...\n")

    # Configuration de la session avec retry pour les échecs temporaires
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, session, file): file for file in adoc_files}
        for future in as_completed(futures):
            file = futures[future]
            try:
                file_broken_links = future.result()
                if file_broken_links:
                    broken_links[file] = file_broken_links
            except Exception as e:
                print(f"⚠️  Error processing {file}: {e}")

    # Affichage des résultats
    if not broken_links:
        print("✅ No broken links found!")
    else:
        print("❌ Broken links found:")
        for file, links in broken_links.items():
            print(f"\n📄 {file}")
            for link, reason in links:
                print(f"  🔗 {link} ({reason})")

    total_broken = sum(len(links) for links in broken_links.values())
    print(f"\n📊 Summary: {total_broken} broken links in {len(broken_links)} files.")

if __name__ == "__main__":
    main()
