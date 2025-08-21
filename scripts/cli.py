import click
import logging
from main import run_check
from config import ROOT_DIR, TIMEOUT, MAX_WORKERS, DELAY, BLACKLIST, OUTPUT_FILE, LOGGING_CONFIG

@click.command()
@click.option(
    "--root-dir",
    type=click.Path(exists=True, file_okay=False),
    default=ROOT_DIR,
    help=f"Répertoire racine à scanner. [Default: {ROOT_DIR}]",
)
@click.option(
    "--timeout",
    type=int,
    default=TIMEOUT,
    help=f"Timeout pour les requêtes HTTP. [Default: {TIMEOUT}]",
)
@click.option(
    "--max-workers",
    type=int,
    default=MAX_WORKERS,
    help=f"Nombre maximal de threads. [Default: {MAX_WORKERS}]",
)
@click.option(
    "--delay",
    type=float,
    default=DELAY,
    help=f"Délai entre chaque requête. [Default: {DELAY}]",
)
@click.option(
    "--output",
    type=click.Path(),
    default=OUTPUT_FILE,
    help=f"Fichier de sortie JSON. [Default: {OUTPUT_FILE}]",
)
@click.option(
    "--blacklist",
    type=str,
    multiple=True,
    default=[],
    help="Domaine à ignorer (peut être répété).",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Active le mode verbeux (DEBUG).",
)
@click.version_option(version="1.0.0")
def cli(root_dir, timeout, max_workers, delay, output, blacklist, verbose):
    """Vérifie les liens brisés dans les fichiers .adoc."""
    if verbose:
        LOGGING_CONFIG["level"] = logging.DEBUG
    logging.basicConfig(**LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 Démarrage de la vérification dans {root_dir}")
    run_check(
        root_dir=root_dir,
        max_workers=max_workers,
        delay=delay,
        timeout=timeout,
        output_file=output,
        blacklist=BLACKLIST + list(blacklist),
    )

if __name__ == "__main__":
    cli()
