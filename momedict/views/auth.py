import random

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from momedict import forms, models
from momedict.user import get_user
from momedict.views import TemplateMethodView
from momedict.user import login_required

auth = Blueprint('auth', __name__)


class Register(TemplateMethodView):
    template = 'auth/register.html'
    methods = ['GET', 'POST']

    def context(self, *args, **kwargs):
        context = super().context(*args, **kwargs)
        context['form'] = self.form
        return context

    def get(self):
        user = get_user()
        if user.registered:
            flash('Du er allerede logget inn', 'error')
            return redirect(url_for('memo.main'))
        self.form = forms.RegisterForm()

    def post(self):
        response = self.get()
        if response:
            return response
        form = forms.RegisterForm(request.form)
        if form.validate():
            self.save_user(form)
            flash('Successfully registered.', 'success')
            return redirect(url_for('memo.main'))
        self.form = form

    def save_user(self, form):
        user = get_user()
        user.name = form.name.data
        user.email = form.email.data
        user.password = form.password.data
        user.registered = True
        models.db.session.add(user)
        models.db.session.commit()


auth.add_url_rule('/register/', view_func=Register.as_view('register'))


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    user = get_user()
    if user.registered:
        flash('Already login', 'warning')
        return redirect(url_for('memo.main'))
    if request.method == 'POST':
        form = forms.LoginForm(request.form)
        if form.validate():
            # Login
            user = models.User.query.filter_by(email=form.email.data).first()
            if user and user.password == form.password.data:
                flash('Successfuly login.', 'success')
                session['user'] = user.id
                return redirect(url_for('memo.main'))
            else:
                flash('Wrong email or password.', 'warning')
        else:
            flash('Login failed.', 'warning')
    else:
        form = forms.LoginForm()
    context = dict(form=form)
    return render_template('auth/login.html', **context)


@auth.route('/logout/')
def logout():
    if 'user' in session:
        del session['user']
    return redirect(url_for('memo.main'))
