from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote

db = SQLAlchemy()


class SemanticList(db.Model):
    __tablename__ = 'semantic_list'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default='')
    is_suggested = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    words = db.relationship(
        'Word', backref='semantic_list', lazy=True,
        cascade='all, delete-orphan',
        order_by='Word.created_at'
    )

    @property
    def word_count(self):
        return len(self.words)

    @property
    def mastered_count(self):
        return sum(1 for w in self.words if w.progress and w.progress.is_mastered)

    @property
    def progress_percentage(self):
        if not self.words:
            return 0
        return int((self.mastered_count / len(self.words)) * 100)

    @property
    def is_fully_mastered(self):
        if not self.words:
            return False
        return all(w.progress and w.progress.is_mastered for w in self.words)


class Word(db.Model):
    __tablename__ = 'word'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('semantic_list.id'), nullable=False)
    english = db.Column(db.String(200), nullable=False)
    spanish = db.Column(db.String(200), nullable=False)
    context_note = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    progress = db.relationship(
        'WordProgress', backref='word', uselist=False,
        cascade='all, delete-orphan'
    )

    @property
    def reverso_url(self):
        return f"https://www.reverso.net/traducci%C3%B3n-texto#sl=eng&tl=spa&text={quote(self.english, safe='')}"


class Collection(db.Model):
    __tablename__ = 'collection'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    links = db.relationship(
        'CollectionLink', backref='collection', lazy=True,
        cascade='all, delete-orphan',
        order_by='CollectionLink.created_at',
    )

    @property
    def link_count(self):
        return len(self.links)


class CollectionLink(db.Model):
    __tablename__ = 'collection_link'

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WordProgress(db.Model):
    __tablename__ = 'word_progress'

    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False, unique=True)
    correct_streak = db.Column(db.Integer, default=0, nullable=False)
    total_correct = db.Column(db.Integer, default=0, nullable=False)
    total_attempts = db.Column(db.Integer, default=0, nullable=False)
    is_mastered = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def record_answer(self, correct: bool):
        self.total_attempts += 1
        if correct:
            self.total_correct += 1
            self.correct_streak += 1
            if self.correct_streak >= 3:
                self.is_mastered = True
        else:
            self.correct_streak = 0
        self.updated_at = datetime.utcnow()
