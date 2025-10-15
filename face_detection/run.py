from app import create_app, create_app_2

# app = create_app()
app = create_app_2()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)