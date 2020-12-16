import argparse
import json

from flask_script import Command, Option

from momedict import models
from momedict.database import db


class ValidationError(Exception):
    pass


def import_definition(definition, word):
    text = definition.get('definition')
    part_of_speech = definition.get('partOfSpeech')
    synonyms = definition.get('synonyms')
    if synonyms:
        synonyms = ','.join(synonyms)
    similar_to = definition.get('similarTo')
    if similar_to:
        similar_to = ','.join(similar_to)
    type_of = definition.get('typeOf')
    if type_of:
        type_of = ','.join(type_of)
    has_types = definition.get('hasTypes')
    if has_types:
        has_types = ','.join(has_types)
    examples = definition.get('examples')
    if examples:
        examples = ','.join(examples)
    attribute = definition.get('attribute')
    if attribute:
        attribute = ','.join(attribute)
    antonyms = definition.get('antonyms')
    if antonyms:
        antonyms = ','.join(antonyms)
    also = definition.get('also')
    if also:
        also = ','.join(also)
    derivation = definition.get('derivation')
    if derivation:
        derivation = ','.join(derivation)
    return models.Definition(text=text, word_id=word.id, part_of_speech=part_of_speech,
                                          synonyms=synonyms, similar_to=similar_to, type_of=type_of,
                                          has_types=has_types, examples=examples, attribute=attribute,
                                          antonyms=antonyms, also=also, derivation=derivation)


def import_word(word_json):
    # Will raise exception if error found
    for key, value in word_json.items():
        validate_word(value)
        # Get or create word
        word = models.Word.query.filter_by(id=key).first()
        if not word and 'definitions' in value and len(value['definitions']) > 0:
            pronunciation = value.get('pronunciation') if 'pronunciation' in value else None
            word = models.Word(key, pronunciation, len(value['definitions']))
            db.session.add(word)
            db.session.commit()
            # Get or create exam
            definitions = value['definitions']
            for def_obj in [import_definition(definition_json, word) for definition_json in definitions]:
                db.session.add(def_obj)
            db.session.commit()
    return True


def import_word_search(word_json):
    validate_word(word_json)
    # Get or create word
    word = models.Word.query.filter_by(id=word_json['word']).first()
    if not word and 'results' in word_json and len(word_json['results']) > 0:
        pronunciation = word_json['pronunciation'].get('all') if 'pronunciation' in word_json else None
        word = models.Word(word_json['word'], pronunciation, len(word_json['results']))
        db.session.add(word)
        db.session.commit()
        # Get or create definition
        definitions = word_json['results']
        for def_obj in [import_definition(definition_json, word) for definition_json in definitions]:
            db.session.add(def_obj)
        db.session.commit()
    return True


def validate_word(word_json):
    # Pass all validation (for test)
    pass
    # Definition and word has to present
    # if 'pronunciation' in word_json:
    #     if 'all' not in word_json['pronunciation']:
    #         raise ValidationError('Not exists pronunciation all')
    # validate_definitions(word_json)


def validate_definitions(word_json):
    # Pass all validation (for test)
    pass
    # if 'definitions' not in word_json:
    #     raise ValidationError('Not exists definitions')
    # if type(word_json['definitions']) is not list:
    #     raise ValidationError('Definition is not list')
    # if len(word_json['definitions']) == 0:
    #     raise ValidationError('Definition count is zero')


class ImportCommand(Command):
    'Import questions in JSON format'

    option_list = (
        Option('filenames', nargs='+', type=argparse.FileType('r'), help='JSON question files'),
    )

    def run(self, filenames):
        print("Importing words...")
        for filename in filenames:
            print('Importing words from', filename.name)
            with open(filename.name, encoding="utf-8") as fh:
                word_json = json.load(fh)
                import_word(word_json)
        print("Importing completed")
