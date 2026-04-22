from pathlib import Path

APP_NAME = "Waikato Library CrossRef XML Generator"
APP_VERSION = "1.0.0"
CROSSREF_BATCH_ID_PREFIX = "waikato-library"
DEPOSITOR_NAME = "Waikato University Library"
DEPOSITOR_EMAIL = "library@waikato.ac.nz"
REGISTRANT = "Waikato University"

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATE_DIR = BASE_DIR / "templates"
