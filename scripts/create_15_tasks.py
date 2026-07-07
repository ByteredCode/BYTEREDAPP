import requests
import json
import time

BASE = "https://byteredapp.onrender.com/api/v1"

def login():
    for attempt in range(5):
        try:
            r = requests.post(f"{BASE}/auth/login", json={"correo": "antonio@bytered.es", "contrasena": "admin1234A"}, timeout=30)
            if r.status_code == 200:
                return r.json()["access_token"]
            print(f"  Login attempt {attempt+1}: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            print(f"  Login attempt {attempt+1} error: {e}")
        time.sleep(5)
    return None

def crear_tarea(token, titulo, descripcion, prioridad, columna, orden):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "columna": columna,
    }
    try:
        r = requests.post(f"{BASE}/scrum/tareas", json=data, headers=headers, timeout=30)
        if r.status_code == 201:
            return r.json()
        print(f"  Error creating '{titulo}': {r.status_code} - {r.text[:100]}")
        return None
    except Exception as e:
        print(f"  Error creating '{titulo}': {e}")
        return None

TAREAS = [
    # Todo (4)
    ("Disenar mockups landing page", "Prototipos en Figma", "Alta", "Todo"),
    ("Configurar CI/CD GitHub Actions", "Pipeline deploy", "Media", "Todo"),
    ("Escribir tests unitarios backend", "Cubrir auth y scrum", "Media", "Todo"),
    ("Corregir CSS responsive", "Ajustar media queries", "Baja", "Todo"),
    # Haciendose (4)
    ("Implementar drag & drop Kanban", "Usar @dnd-kit", "Alta", "Haciendose"),
    ("Sistema de tickets v2", "Notificaciones Resend", "Critica", "Haciendose"),
    ("Integrar modulo fichajes", "Login register timestamp", "Media", "Haciendose"),
    ("Optimizar queries lentas", "Indices y eager loading", "Alta", "Haciendose"),
    # En revision (4)
    ("Documentar API con Swagger", "Descripciones endpoints", "Baja", "En revision"),
    ("Configurar CSP headers", "Seguridad OWASP", "Media", "En revision"),
    ("Revisar permisos multi-tenant", "Aislamiento company_id", "Alta", "En revision"),
    ("Testing eliminacion tareas", "Verificar endpoint DELETE", "Media", "En revision"),
    # Done (3)
    ("Login con JWT", "FastAPI + PyJWT", "Critica", "Done"),
    ("Desplegar frontend Hostinger", "Build via FTP", "Alta", "Done"),
    ("Crear BD MySQL Hostinger", "Schema inicial", "Alta", "Done"),
]

if __name__ == "__main__":
    print("Obteniendo token...")
    token = login()
    if not token:
        print("No se pudo autenticar")
        exit(1)
    print(f"Token OK")

    for i, (titulo, desc, prio, col) in enumerate(TAREAS):
        print(f"  [{i+1}/15] {titulo} ({col})")
        crear_tarea(token, titulo, desc, prio, col, i)
        time.sleep(0.5)

    print("15 tareas creadas!")
