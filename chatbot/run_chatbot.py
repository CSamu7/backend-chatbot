import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from ML.chatbot import chatbot

def get_safe_input(prompt: str = "") -> str:
    try:

        sys.stdout.write(prompt)
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            return "salir"
        return line.strip()
    except EOFError:
        return "salir"
    except Exception:
        return input(prompt).strip()

if __name__ == "__main__":

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== Chatbot de Libros Iniciado ===")
    print("Escribe 'salir' para terminar.\n")
    
    chatbot(get_input=get_safe_input)