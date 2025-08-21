import logging

# Configuration centrale du script
ROOT_DIR = "../main/modules"          # Répertoire racine à scanner
TIMEOUT = 15                          # Timeout pour les requêtes HTTP (secondes)
MAX_WORKERS = 5                       # Nombre maximal de threads pour le traitement parallèle
DELAY = 0.5                           # Délai entre chaque requête (secondes)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
BLACKLIST = []                        # Liste des domaines à ignorer (ex: ["spam.com", "ads.example"])

# Patterns pour l'extraction des liens
LINK_PATTERNS = [
    r'link:(?:http[s]?:\/\/.)?(?:www\.)?[-a-zA-Z0-9@%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)',  # URLs classiques
    r'video::([A-Za-z0-9_\-]{11})',    # Identifiants YouTube
]

# Configuration du logging
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": '%(asctime)s - %(levelname)s - %(message)s',
    "handlers": [logging.StreamHandler()]
}

# Configuration des retries pour les requêtes HTTP
RETRY_CONFIG = {
    "total": 3,
    "backoff_factor": 1,
    "status_forcelist": [500, 502, 503, 504]
}

# Fichier de sortie
OUTPUT_FILE = "broken_links.json"
