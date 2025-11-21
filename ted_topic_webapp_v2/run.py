from app import app as flask_app
from dashboard import app as dash_app

dash_app.init_app(flask_app)

if __name__ == '__main__':
    flask_app.run(debug=True)