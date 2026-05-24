import json
import random
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db, SemanticList, Word, WordProgress

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/quiz/<int:list_id>')
def quiz(list_id):
    semantic_list = SemanticList.query.get_or_404(list_id)
    words = list(semantic_list.words)

    if len(words) < 2:
        flash('Necesitas al menos 2 palabras para jugar.', 'warning')
        return redirect(url_for('lists.detail', list_id=list_id))

    all_spanish = [w.spanish for w in words]
    extra_spanish = [
        w.spanish for w in
        Word.query.filter(Word.list_id != list_id).limit(60).all()
    ]

    questions = []
    for word in words:
        distractors = [s for s in all_spanish if s != word.spanish]
        if len(distractors) < 3:
            pool = [s for s in extra_spanish if s not in distractors and s != word.spanish]
            random.shuffle(pool)
            distractors += pool[:3 - len(distractors)]

        random.shuffle(distractors)
        options = [word.spanish] + distractors[:3]
        random.shuffle(options)

        questions.append({
            'word_id': word.id,
            'english': word.english,
            'correct': word.spanish,
            'options': options,
        })

    random.shuffle(questions)

    return render_template(
        'quiz.html',
        semantic_list=semantic_list,
        questions_json=json.dumps(questions),
    )


@quiz_bp.route('/quiz/<int:list_id>/submit', methods=['POST'])
def submit_quiz(list_id):
    semantic_list = SemanticList.query.get_or_404(list_id)
    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    answers = data['answers']
    results = {
        'total': len(answers),
        'correct': 0,
        'wrong_words': [],
        'newly_mastered': [],
        'list_mastered': False,
        'percentage': 0,
    }

    for answer in answers:
        word = Word.query.get(answer.get('word_id'))
        if not word or word.list_id != list_id:
            continue

        is_correct = bool(answer.get('correct', False))
        progress = word.progress
        if not progress:
            progress = WordProgress(word_id=word.id)
            db.session.add(progress)
            db.session.flush()

        was_mastered = progress.is_mastered
        progress.record_answer(is_correct)

        if is_correct:
            results['correct'] += 1
        else:
            results['wrong_words'].append({'english': word.english, 'spanish': word.spanish})

        if not was_mastered and progress.is_mastered:
            results['newly_mastered'].append({'english': word.english, 'spanish': word.spanish})

    db.session.commit()

    db.session.refresh(semantic_list)
    results['list_mastered'] = semantic_list.is_fully_mastered
    if results['total']:
        results['percentage'] = int((results['correct'] / results['total']) * 100)

    return jsonify(results)
