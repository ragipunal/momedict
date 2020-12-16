from sqlalchemy import orm
from sqlalchemy.sql import func, label
from sqlalchemy_utils.types.password import PasswordType

from momedict.database import db
from datetime import datetime, timedelta


class Vocab(db.Model):
    __tablename__ = 'vocab'
    __mapper_args__ = {'order_by': 'name'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    name = db.Column(db.String(120), nullable=False, info={'label': 'Name'})
    vocab_words = db.relationship('VocabWord', backref='vocabs')

    def __init__(self, user, name=None):
        self.user_id = user.id
        self.name = name

    def word_count(self):
        return VocabWord.query.filter_by(vocab_id=self.id).count()

    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'count': self.word_count()
        }

    @property
    def string(self):
        return self.name


class VocabWord(db.Model):
    __tablename__ = 'vocab_word'
    __mapper_args__ = {'order_by': 'word_id'}
    word_id = db.Column(db.String, db.ForeignKey('word.id'), primary_key=True, info={'label': 'Word'})
    vocab_id = db.Column(db.Integer, db.ForeignKey('vocab.id'), primary_key=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    view = db.Column(db.Integer, nullable=False, default=0)
    practice_point = db.Column(db.Float, nullable=False, default=0.0)

    word = db.relationship('Word', backref='vocab_word')
    vocab = db.relationship('Vocab', backref='vocab_word')

    def __init__(self, word_id=None, vocab_id=None):
        self.word_id = word_id
        self.vocab_id = vocab_id
        self.score = 0
        self.view = 0
        self.practice_point = 0.0

    def __repr__(self):
        return self.word_id

    def serialize(self):
        return {
            'word_id': self.word_id,
            'vocab_id': self.vocab_id,
            'score': self.score,
            'view': self.view,
            'practice_point': self.practice_point,
            'word': self.get_word.serialize()
        }

    @property
    def string(self):
        return self.vocab.name + '_' + self.word.id

    @property
    def get_word(self):
        return self.word


class Word(db.Model):
    __tablename__ = 'word'
    __mapper_args__ = {'order_by': 'id'}
    id = db.Column(db.String, primary_key=True, info={'label': 'Word'})
    pronunciation = db.Column(db.String, info={'label': 'Pronunciation'})
    definition_count = db.Column(db.Integer, info={'label': 'Definition Count'})
    search_count = db.Column(db.Integer, info={'label': 'Search Count'})
    # Definations
    definitions = db.relationship('Definition', backref='word', order_by='Definition.id')

    def __init__(self, id=None, pronunciation=None, definition_count=0):
        self.pronunciation = pronunciation['all'] if pronunciation and 'all' in pronunciation else None
        self.definition_count = definition_count
        self.id = id
        self.search_count = 0

    def __repr__(self):
        return self.id

    @property
    def definition_all(self):
        return self.definitions

    @property
    def index(self):
        return Word.find_index(self)

    @classmethod
    def find_index(cls, word):
        indexes = [q.id for q in cls.query.filter_by(exam_id=word.exam_id).all()]
        return indexes.index(word.id) + 1

    def serialize(self):
        response = {'id': self.id, 'pronunciation': self.pronunciation, 'definitions': [],
                    'search_count': self.search_count}
        for alt in self.definition_all:
            alt_dict = alt.serialize()
            del alt_dict['word_id']
            response['definitions'].append(alt_dict)
        return response


class Definition(db.Model):
    __tablename__ = 'definition'
    __mapper_args__ = {'order_by': 'id'}
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, info={'label': 'Defination Text'})
    part_of_speech = db.Column(db.String, info={'label': 'Part Of Speech'})
    similar_to = db.Column(db.String, info={'label': 'Similar To'})
    type_of = db.Column(db.String, info={'label': 'Type Of'})
    also = db.Column(db.String, info={'label': 'Also'})
    derivation = db.Column(db.String, info={'label': 'Derivation'})
    attribute = db.Column(db.String, info={'label': 'Attribute'})
    antonyms = db.Column(db.String, info={'label': 'Antonyms'})
    synonyms = db.Column(db.String, info={'label': 'Synonyms'})
    has_types = db.Column(db.String, info={'label': 'Has Types'})
    examples = db.Column(db.String, info={'label': 'Examples'})
    word_id = db.Column(db.String, db.ForeignKey('word.id'), index=True)

    def __init__(self, text, word_id, type_of=None, part_of_speech=None, similar_to=None, also=None, derivation=None,
                 attribute=None,
                 antonyms=None, synonyms=None, has_types=None, examples=None):
        self.text = text
        self.part_of_speech = part_of_speech
        self.similar_to = similar_to
        self.type_of = type_of
        self.also = also
        self.derivation = derivation
        self.attribute = attribute
        self.antonyms = antonyms
        self.synonyms = synonyms
        self.has_types = has_types
        self.examples = examples
        self.word_id = word_id

    def __repr__(self):
        return self.text

    @property
    def index(self):
        return Definition.find_index(self)

    @classmethod
    def find_index(cls, definition):
        indexes = [q.id for q in cls.query.filter_by(word_id=definition.word_id).all()]
        return indexes.index(definition.id) + 1

    def serialize(self):
        response = {
            'id': self.id,
            'text': self.text,
            'word_id': self.word_id,
            'part_of_speech': self.part_of_speech,
            'similar_to': self.similar_to.split(',') if self.similar_to else None,
            'type_of': self.type_of.split(',') if self.type_of else None,
            'also': self.also.split(',') if self.also else None,
            'derivation': self.derivation.split(',') if self.derivation else None,
            'attribute': self.attribute.split(',') if self.attribute else None,
            'antonyms': self.antonyms.split(',') if self.antonyms else None,
            'synonyms': self.synonyms.split(',') if self.synonyms else None,
            'has_types': self.has_types.split(',') if self.has_types else None,
            'examples': self.examples.split(',') if self.examples else None
        }
        return response


class User(db.Model):
    __tablename__ = 'user'
    __mapper_args__ = {'order_by': 'id'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, info={'label': 'Name'})
    email = db.Column(db.String, unique=True, info={'label': 'Email'}, index=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), info={'label': 'Password'})
    registered = db.Column(db.Boolean)

    def __init__(self):
        self.registered = False

    def __repr__(self):
        return self.email


class UserStats(db.Model):
    __tablename__ = 'user_stats'
    __mapper_args__ = {'order_by': 'user_id'}

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    word_id = db.Column(db.String, db.ForeignKey('word.id'), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer)
    day_of_week = db.Column(db.Integer)
    score = db.Column(db.Integer, default=0)
    search_count = db.Column(db.Integer, default=0)

    word = db.relationship('Word', backref='user_stats')
    user = db.relationship('User', backref='user_stats')

    def __init__(self, word: Word, user: User, date: datetime, score, search_count):
        self.word_id = word.id
        self.user_id = user.id
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.week = date.isocalendar()[1]
        self.day_of_week = date.isoweekday()
        self.score = score
        self.search_count = search_count

    @classmethod
    def all_time_core(cls, word, user):
        score = cls.query.with_entities(func.sum(cls.score).label("score"))\
            .filter_by(word=word, user=user).first().score
        return score

    @classmethod
    def thismonth(cls, user, word, now: datetime):
        score = cls.query.with_entities(func.sum(cls.score).label("score")) \
            .filter_by(word=word, user=user, year=now.year, month=now.month)
        return score

    @classmethod
    def last7days(cls, word, user, now: datetime):
        score = cls.query.with_entities(func.sum(cls.score).label("score")) \
            .filter_by(word=word, user=user, year=now.year, month=now.month).first().score
        return score

    @classmethod
    def all_time_count(cls, word, user):
        sq = cls.query.with_entities(func.sum(cls.search_count).label("mySum"))
        usc = sq.filter_by(word=word, user=user).first().mySum
        search_count = sq.filter_by(word=word).first().mySum
        return usc, search_count

    @classmethod
    def save_search(cls, word, user, now):
        search = cls.query.filter_by(word=word, user=user, year=now.year, month=now.month, day=now.day).first()
        if search:
            search.search_count += 1
            db.session.commit()
        else:
            search = cls(word,user, now, 0, 1)
            db.session.add(search)
            db.session.commit()


orm.configure_mappers()
