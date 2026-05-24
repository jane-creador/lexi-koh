from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, SemanticList, Word, WordProgress

lists_bp = Blueprint('lists', __name__)


@lists_bp.route('/lists/new', methods=['GET', 'POST'])
def create_list():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('El nombre es obligatorio.', 'danger')
            return render_template('create_list.html')
        new_list = SemanticList(name=name, description=description, is_suggested=False)
        db.session.add(new_list)
        db.session.commit()
        flash('¡Lista creada con éxito!', 'success')
        return redirect(url_for('lists.detail', list_id=new_list.id))
    return render_template('create_list.html')


@lists_bp.route('/lists/<int:list_id>')
def detail(list_id):
    semantic_list = SemanticList.query.get_or_404(list_id)
    return render_template('list_detail.html', semantic_list=semantic_list)


@lists_bp.route('/lists/<int:list_id>/words/add', methods=['POST'])
def add_word(list_id):
    SemanticList.query.get_or_404(list_id)
    english = request.form.get('english', '').strip()
    spanish = request.form.get('spanish', '').strip()
    context_note = request.form.get('context_note', '').strip()
    if not english or not spanish:
        flash('Inglés y español son obligatorios.', 'danger')
        return redirect(url_for('lists.detail', list_id=list_id))
    word = Word(list_id=list_id, english=english, spanish=spanish, context_note=context_note)
    db.session.add(word)
    db.session.commit()
    flash('Palabra añadida.', 'success')
    return redirect(url_for('lists.detail', list_id=list_id))


@lists_bp.route('/lists/<int:list_id>/words/<int:word_id>/edit', methods=['POST'])
def edit_word(list_id, word_id):
    word = Word.query.filter_by(id=word_id, list_id=list_id).first_or_404()
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    word.english = data.get('english', word.english).strip()
    word.spanish = data.get('spanish', word.spanish).strip()
    word.context_note = data.get('context_note', word.context_note or '').strip()
    db.session.commit()
    return jsonify({
        'success': True,
        'word': {
            'id': word.id,
            'english': word.english,
            'spanish': word.spanish,
            'context_note': word.context_note,
            'reverso_url': word.reverso_url,
        }
    })


@lists_bp.route('/lists/<int:list_id>/words/<int:word_id>/delete', methods=['POST'])
def delete_word(list_id, word_id):
    word = Word.query.filter_by(id=word_id, list_id=list_id).first_or_404()
    db.session.delete(word)
    db.session.commit()
    if request.is_json:
        return jsonify({'success': True})
    flash('Palabra eliminada.', 'info')
    return redirect(url_for('lists.detail', list_id=list_id))


@lists_bp.route('/lists/<int:list_id>/delete', methods=['POST'])
def delete_list(list_id):
    semantic_list = SemanticList.query.get_or_404(list_id)
    if semantic_list.is_suggested:
        flash('No puedes eliminar una lista sugerida.', 'danger')
        return redirect(url_for('home.index'))
    db.session.delete(semantic_list)
    db.session.commit()
    flash('Lista eliminada.', 'info')
    return redirect(url_for('home.index'))


@lists_bp.route('/lists/suggested/<int:list_id>/copy', methods=['POST'])
def copy_suggested(list_id):
    suggested = SemanticList.query.filter_by(id=list_id, is_suggested=True).first_or_404()
    new_list = SemanticList(
        name=suggested.name,
        description=suggested.description,
        is_suggested=False
    )
    db.session.add(new_list)
    db.session.flush()
    for word in suggested.words:
        db.session.add(Word(
            list_id=new_list.id,
            english=word.english,
            spanish=word.spanish,
            context_note=word.context_note,
        ))
    db.session.commit()
    flash(f'Lista "{suggested.name}" copiada a tus listas.', 'success')
    return redirect(url_for('lists.detail', list_id=new_list.id))
