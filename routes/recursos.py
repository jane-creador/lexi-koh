from flask import Blueprint, render_template, request, redirect, url_for, session
from models import Collection, CollectionLink, db

recursos_bp = Blueprint('recursos', __name__)


def _sid():
    return session.get('sid', '')


@recursos_bp.route('/recursos')
def index():
    sid = _sid()
    collections = (
        Collection.query
        .filter_by(session_id=sid)
        .order_by(Collection.created_at.desc())
        .all()
    )
    return render_template('recursos.html', collections=collections)


@recursos_bp.route('/recursos/collections', methods=['POST'])
def create_collection():
    sid = _sid()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if title and sid:
        db.session.add(Collection(session_id=sid, title=title, description=description))
        db.session.commit()
    return redirect(url_for('recursos.index'), 303)


@recursos_bp.route('/recursos/collections/<int:col_id>/edit', methods=['POST'])
def edit_collection(col_id):
    col = Collection.query.filter_by(id=col_id, session_id=_sid()).first_or_404()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if title:
        col.title = title
        col.description = description
        db.session.commit()
    return redirect(url_for('recursos.index') + f'#col-{col_id}', 303)


@recursos_bp.route('/recursos/collections/<int:col_id>/delete', methods=['POST'])
def delete_collection(col_id):
    col = Collection.query.filter_by(id=col_id, session_id=_sid()).first_or_404()
    db.session.delete(col)
    db.session.commit()
    return redirect(url_for('recursos.index'), 303)


@recursos_bp.route('/recursos/collections/<int:col_id>/links', methods=['POST'])
def add_link(col_id):
    col = Collection.query.filter_by(id=col_id, session_id=_sid()).first_or_404()
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    if title and url:
        db.session.add(CollectionLink(collection_id=col.id, title=title, url=url))
        db.session.commit()
    return redirect(url_for('recursos.index') + f'#col-{col_id}', 303)


@recursos_bp.route('/recursos/links/<int:link_id>/edit', methods=['POST'])
def edit_link(link_id):
    link = (
        CollectionLink.query
        .join(Collection)
        .filter(CollectionLink.id == link_id, Collection.session_id == _sid())
        .first_or_404()
    )
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    if title and url:
        link.title = title
        link.url = url
        db.session.commit()
    return redirect(url_for('recursos.index') + f'#col-{link.collection_id}', 303)


@recursos_bp.route('/recursos/links/<int:link_id>/delete', methods=['POST'])
def delete_link(link_id):
    link = (
        CollectionLink.query
        .join(Collection)
        .filter(CollectionLink.id == link_id, Collection.session_id == _sid())
        .first_or_404()
    )
    col_id = link.collection_id
    db.session.delete(link)
    db.session.commit()
    return redirect(url_for('recursos.index') + f'#col-{col_id}', 303)
