import uuid
from flask import Blueprint, render_template, session
from models import SemanticList

home_bp = Blueprint('home', __name__)


def _ensure_sid():
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    return session['sid']


@home_bp.route('/')
def index():
    _ensure_sid()
    user_lists = (
        SemanticList.query
        .filter_by(is_suggested=False)
        .order_by(SemanticList.created_at.desc())
        .all()
    )
    suggested_lists = (
        SemanticList.query
        .filter_by(is_suggested=True)
        .order_by(SemanticList.id)
        .all()
    )
    return render_template('home.html', user_lists=user_lists, suggested_lists=suggested_lists)
