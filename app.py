import os
from flask import Flask
from models import db

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def create_app():
    app = Flask(__name__)

    database_url = os.environ.get('DATABASE_URL', 'sqlite:///lexikoh.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SECRET_KEY', 'change-me-in-production'),
    )

    db.init_app(app)

    from routes.home import home_bp
    from routes.lists import lists_bp
    from routes.quiz import quiz_bp
    from routes.recursos import recursos_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(recursos_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
