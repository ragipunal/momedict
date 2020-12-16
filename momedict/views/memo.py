import random

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from momedict import forms, models
from momedict.user import get_user
from momedict.views import TemplateMethodView
from momedict.user import login_required
import requests
from momedict.importer import import_word_search
from momedict.config import RAPIDAPI_KEY, RAPIDAPI_HOST
from datetime import datetime
import json

memo = Blueprint('memo', __name__)


@memo.route('/')
@login_required
def main():
    context = {'courses': models.Vocab.query.all()}
    return render_template('memo/main.html', **context)


@memo.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_user()
    if user.registered:
        form = forms.ProfileForm(obj=user)
        if request.method == 'POST':
            form = forms.ProfileForm(request.form)
            if form.validate():
                user = models.User.query.filter_by(email=user.email).first()
                if user:
                    user.name = form.name.data
                    user.email = form.email.data
                    models.db.session.commit()

                    session['user'] = user.id
                    flash('Successfully updated.', 'success')
                else:
                    flash('Wrong email.', 'warning')
    else:
        flash('Please Login', 'warning')
        return redirect(url_for('auth.login'))
    context = dict(form=form)
    return render_template('memo/profile.html', **context)


@memo.route('/logout/')
def logout():
    if 'user' in session:
        del session['user']
    return redirect(url_for('memo.main'))


class CreateVocab(TemplateMethodView):
    template = 'memo/create_vocab.html'
    methods = ['GET', 'POST']

    def context(self, *args, **kwargs):
        context = super().context(*args, **kwargs)
        context['form'] = self.form
        return context

    def get(self):
        self.form = forms.CreateVocabForm()

    def post(self):
        response = self.get()
        if response:
            return response
        form = forms.CreateVocabForm(request.form)
        if form.validate():
            is_exists = models.Vocab.query.filter_by(user_id=get_user().id, name=form.name.data).first()
            if is_exists:
                flash('Error. This name is exists', 'warning')
            else:
                vocab = self.save_vocab(form)
                flash('Successfully created.', 'success')
                return redirect(url_for('memo.vocab', id=vocab.id))

        self.form = form

    def save_vocab(self, form):

        user = get_user()
        vocab = models.Vocab(user, form.name.data)
        models.db.session.add(vocab)
        models.db.session.commit()
        return vocab


memo.add_url_rule('/create_vocab/', view_func=CreateVocab.as_view('create_vocab'))


@memo.route('/start_practice')
@login_required
def start_practice():
    # Check if course exists
    vocabs = models.Vocab.query.filter_by(user_id=get_user().id).all()
    [vocab.serialize() for vocab in vocabs]
    context = dict(vocabs=[vocab.serialize() for vocab in vocabs])
    return render_template('memo/start_practice.html', **context)


@memo.route('/practice/<int:id>')
@login_required
def practice(id):
    # Check if vocab exists
    vocab = models.Vocab.query.filter_by(id=id, user_id=get_user().id).first()
    if vocab is None:
        flash('Not Exists Vocabulary selected.', 'warning')
        return redirect(url_for('memo.main'))

    vocab_word = models.VocabWord.query.filter_by(vocab=vocab) \
        .order_by(models.VocabWord.view.asc()) \
        .order_by(models.VocabWord.practice_point.asc()).first()

    vocab_word.view += 1
    models.db.session.commit()

    definition = models.Definition.query.filter_by(word_id=vocab_word.word_id).first()

    other_words = models.VocabWord.query.filter(models.VocabWord.vocab_id.is_(vocab.id)).filter(models.VocabWord.word_id.isnot(vocab_word.word_id)) \
        .order_by(models.VocabWord.view.asc()).limit(2)

    words = [vocab_word]
    for word in other_words:
        words.append(word)
    random.shuffle(words)

    context = dict(vocab=vocab, vocab_word=vocab_word, definition=definition, words=words)
    return render_template('memo/practice.html', **context)


@memo.route('/search/', methods=['POST'])
@login_required
def search():
    keyword = request.form.get('keyword').lower()
    word = models.Word.query.filter_by(id=keyword).first()
    if word is None:
        try:
            response = requests.get("https://wordsapiv1.p.rapidapi.com/words/" + keyword,
                                    headers={
                                        'x-rapidapi-key': RAPIDAPI_KEY,
                                        'x-rapidapi-host': RAPIDAPI_HOST,
                                        "Accept": "application/json"
                                    })
            import_word_search(response.json())
        except Exception as e:
            print(e)

    word = models.Word.query.filter_by(id=keyword).first()
    if word:
        models.UserStats.save_search(word, get_user(), datetime.now())
        user_count, count = models.UserStats.all_time_count(word, get_user())
        context = dict(word=json.loads(json.dumps(word.serialize())),
                       user_count=user_count, count=count, keyword=keyword)
    else:
        context = dict(word=None, keyword=keyword)
    return render_template('memo/search.html', **context)


@memo.route('/vocab/<int:id>/')
@login_required
def vocab(id):
    """Reset stats for a course"""
    # Check if course exists
    vocab = models.Vocab.query.filter_by(id=id, user_id=get_user().id).first_or_404()
    context = dict(vocab=vocab)
    return render_template('memo/vocab.html', **context)
