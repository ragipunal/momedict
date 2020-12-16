import json
import math
from flask import Blueprint, Response, request
from flask.views import MethodView

from momedict import models
import requests
from momedict.config import RAPIDAPI_HOST, RAPIDAPI_KEY
from momedict.importer import import_word_search

api = Blueprint('api', __name__)


def error(message):
    return {'message': message}


class JsonView(MethodView):
    def dispatch_request(self, *args, **kwargs):
        """Returns a json document with mimetype set"""
        return Response(
            json.dumps(super(JsonView, self).dispatch_request(*args, **kwargs)),
            mimetype='application/json'
        )


# REST API

class SearchWord(JsonView):
    def get(self, word):
        words_m = models.Word.query.filter(models.Word.id.like(word)).first()
        if words_m is None:
            try:
                response = requests.get("https://wordsapiv1.p.rapidapi.com/words/" + word,
                                        headers={
                                            'x-rapidapi-key': RAPIDAPI_KEY,
                                            'x-rapidapi-host': RAPIDAPI_HOST,
                                            "Accept": "application/json"
                                        })
                import_word_search(response.json())
            except Exception as e:
                print(e)

        words_m = models.Word.query.filter(models.Word.id.like('%' + word + '%')).all()

        serialized_objects = [word.serialize() for word in words_m]
        result = [obj for obj in serialized_objects if obj is not None]
        return {'data': result, 'totalCount': len(result), 'summary': '', 'groupCount': 0}


api.add_url_rule('/words/search/<string:word>', view_func=SearchWord.as_view('search_word'))


class VocabWords(JsonView):
    def get(self, id):
        vocab_m = models.Vocab.query.filter_by(id=id).first_or_404()
        vocab_words = models.VocabWord.query.filter_by(vocab=vocab_m).offset(request.args.get('skip')).limit(
            request.args.get('take'))
        serialized_objects = [word_m.serialize() for word_m in vocab_words]
        result = [obj for obj in serialized_objects if obj is not None]
        return {'data': result, 'totalCount': len(result), 'summary': '', 'groupCount': 0}

    def delete(self, id):
        vocab_word_m = models.VocabWord.query.filter_by(word_id=request.form.get('word_id'), vocab_id=id).first()
        if vocab_word_m:
            models.db.session.delete(vocab_word_m)
            models.db.session.commit()
        return True


api.add_url_rule('/vocab/<int:id>/words/', view_func=VocabWords.as_view('vocab_words'), methods=['GET'])


class VocabWordDelete(JsonView):
    def delete(self, id):
        vocab_word_m = models.VocabWord.query.filter_by(word_id=request.form.get('word_id'), vocab_id=id).first()
        if vocab_word_m:
            models.db.session.delete(vocab_word_m)
            models.db.session.commit()
        return True


api.add_url_rule('/vocab/<int:id>/word/delete', view_func=VocabWordDelete.as_view('vocab_word_delete'),
                 methods=['DELETE'])


class VocabAddWord(JsonView):
    def post(self):
        vocab_m = models.VocabWord.query.filter_by(word_id=request.form.get('word'),
                                                   vocab_id=request.form.get('id')).first()
        if vocab_m:
            return False
        else:
            vocab_word = models.VocabWord(word_id=request.form.get('word'), vocab_id=request.form.get('id'))
            models.db.session.add(vocab_word)
            models.db.session.commit()
        return True


api.add_url_rule('/vocab/addword/', view_func=VocabAddWord.as_view('vocab_add_word'), methods=['POST'])


class Practice(JsonView):
    def post(self):
        word_id = request.form.get('word_id')
        vocab_id = request.form.get('vocab_id')
        vw_id = request.form.get('vw_id')
        definition_id = request.form.get('definition_id')
        if word_id and vw_id and definition_id and vocab_id:
            vocab_word = models.VocabWord.query.filter_by(word_id=vw_id, vocab_id=vocab_id).first()
            definition = models.Definition.query.filter_by(id=definition_id).first()
            if definition.word_id == word_id:

                vocab_word.score += 1
                vocab_word.practice_point = math.exp(vocab_word.score / vocab_word.view)
                models.db.session.commit()
                return True
            else:
                vocab_word.score -= 1
                vocab_word.practice_point = math.exp(vocab_word.score / vocab_word.view)
                models.db.session.commit()
        return False


api.add_url_rule('/practice/', view_func=Practice.as_view('practice'), methods=['POST'])
