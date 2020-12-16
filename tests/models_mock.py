from momedict.models import Vocab, VocabWord, Definition, Word
from momedict.database import db


def add_word(id='apple', pronunciation='apple', definition_count=0, **kwargs):
    word = Word(id, pronunciation, definition_count, **kwargs)
    db.session.add(word)
    db.session.commit()
    return word


def add_definition(word, **kwargs):
    definition = Definition(text='word of the ring', word_id=word.id, **kwargs)
    db.session.add(definition)
    db.session.commit()
    return definition


def add_vocab(user, name="T16", **kwargs):
    vocab = Vocab(user.id, name, **kwargs)
    db.session.add(vocab)
    db.session.commit()
    return vocab


def add_vocab_word(vocab, word, **kwargs):
    vocab_word = VocabWord(vocab.id, word.id, **kwargs)
    db.session.add(vocab_word)
    db.session.commit()
    return vocab_word


