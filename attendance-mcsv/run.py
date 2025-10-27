from app import create_app
from app.scheduler import run_scheduler
import threading

# Crea la instancia de la aplicación usando la fábrica
app = create_app()

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, args=(app,), daemon=True)
    scheduler_thread.start()
    print("Background Scheduler thread started.")
    # Ejecuta la aplicación en modo debug
    # En producción, usarías un servidor WSGI como Gunicorn o uWSGI
    app.run(debug=True)