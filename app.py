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
        try:
            db.session.execute(db.text(
                "ALTER TABLE semantic_list ADD COLUMN session_id VARCHAR(100);"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        from seed import seed_suggested_lists
        from models import SemanticList, Word

        # Remove duplicate suggested lists, keeping the lowest-id copy of each name.
        seen = {}
        for lst in SemanticList.query.filter_by(is_suggested=True).order_by(SemanticList.id).all():
            if lst.name in seen:
                db.session.delete(lst)
            else:
                seen[lst.name] = lst.id
        db.session.commit()

        seed_suggested_lists(db, SemanticList, Word)

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
