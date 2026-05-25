"""
Seed the database with pre-built suggested lists.
Called automatically on every app startup (idempotent via count check).
Can also be run standalone: python seed.py
"""
import os
import sys

SUGGESTED_LISTS = [
    {
        'name': 'Kitchen verbs',
        'description': 'Verbos esenciales de cocina',
        'words': [
            ('cook',   'cocinar'),
            ('bake',   'hornear'),
            ('stir',   'remover'),
            ('chop',   'picar'),
            ('boil',   'hervir'),
            ('fry',    'freír'),
            ('mix',    'mezclar'),
            ('taste',  'probar'),
        ],
    },
    {
        'name': 'Kitchen nouns',
        'description': 'Objetos y utensilios de cocina',
        'words': [
            ('oven',   'horno'),
            ('knife',  'cuchillo'),
            ('spoon',  'cuchara'),
            ('pan',    'sartén'),
            ('bowl',   'cuenco'),
            ('fridge', 'nevera'),
            ('stove',  'estufa'),
            ('plate',  'plato'),
        ],
    },
    {
        'name': 'Emotions',
        'description': 'Emociones y sentimientos',
        'words': [
            ('happy',   'feliz'),
            ('sad',     'triste'),
            ('angry',   'enfadado'),
            ('scared',  'asustado'),
            ('excited', 'emocionado'),
            ('nervous', 'nervioso'),
            ('proud',   'orgulloso'),
            ('calm',    'tranquilo'),
        ],
    },
    {
        'name': 'Nature',
        'description': 'Elementos de la naturaleza',
        'words': [
            ('forest',   'bosque'),
            ('river',    'río'),
            ('mountain', 'montaña'),
            ('cloud',    'nube'),
            ('ocean',    'océano'),
            ('flower',   'flor'),
            ('tree',     'árbol'),
            ('rain',     'lluvia'),
        ],
    },
    {
        'name': 'Travel',
        'description': 'Vocabulario de viajes',
        'words': [
            ('passport', 'pasaporte'),
            ('luggage',  'equipaje'),
            ('flight',   'vuelo'),
            ('hotel',    'hotel'),
            ('map',      'mapa'),
            ('ticket',   'billete'),
            ('border',   'frontera'),
            ('customs',  'aduana'),
        ],
    },
    {
        'name': 'Body',
        'description': 'Partes del cuerpo',
        'words': [
            ('heart',    'corazón'),
            ('brain',    'cerebro'),
            ('lung',     'pulmón'),
            ('knee',     'rodilla'),
            ('shoulder', 'hombro'),
            ('wrist',    'muñeca'),
            ('ankle',    'tobillo'),
            ('spine',    'columna vertebral'),
        ],
    },
]


def seed_suggested_lists(db, SemanticList, Word):
    """Insert suggested lists only if none exist yet (idempotent)."""
    if SemanticList.query.filter_by(is_suggested=True).count() == 0:
        for list_data in SUGGESTED_LISTS:
            sem_list = SemanticList(
                name=list_data['name'],
                description=list_data['description'],
                is_suggested=True,
                session_id=None,
            )
            db.session.add(sem_list)
            db.session.flush()

            for english, spanish in list_data['words']:
                db.session.add(Word(
                    list_id=sem_list.id,
                    english=english,
                    spanish=spanish,
                ))

        db.session.commit()
        print(f"Seeded {len(SUGGESTED_LISTS)} suggested lists.")
    else:
        print("Suggested lists already present — skipping seed.")


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    from app import app
    from models import db, SemanticList, Word
    with app.app_context():
        seed_suggested_lists(db, SemanticList, Word)
