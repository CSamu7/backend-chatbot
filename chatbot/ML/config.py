import os
import django
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# ==================== CONFIG DJANGO ====================
try:
    from django.apps import apps
    if not apps.ready:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
        django.setup()
except RuntimeError:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

from chat.models import Chat, Message
from authentication.models import User

# Cargar modelo spaCy
import spacy

try:
    nlp = spacy.load("es_core_news_md")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "es_core_news_md"])
    nlp = spacy.load("es_core_news_md")

# Cargar modelo de ML
import pickle
import os

vectorizer = None
clf = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "chatbot_model.pkl")
    with open(model_path, "rb") as f:
        vectorizer, clf = pickle.load(f)
    ml_model_loaded = True
except FileNotFoundError:
    print(f"Advertencia: Archivo del modelo no encontrado en {model_path}")
    vectorizer = None
    clf = None
    ml_model_loaded = False
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    vectorizer = None
    clf = None
    ml_model_loaded = False

# ==================== SUPABASE ====================
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Las variables SUPABASE_URL y SUPABASE_KEY deben estar definidas en .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
