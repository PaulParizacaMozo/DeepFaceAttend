from app import create_app

# Crea la instancia de la aplicación usando la fábrica
app = create_app()

if __name__ == "__main__":
    # Ejecuta la aplicación en modo debug
    # En producción, usarías un servidor WSGI como Gunicorn o uWSGI
    app.run(debug=True)
