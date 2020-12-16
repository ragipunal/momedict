from flask_wtf import FlaskForm
from wtforms import fields, validators
from wtforms_alchemy import model_form_factory

from momedict import models
from momedict.user import get_user

import email_validator

db = models.db
BaseModelForm = model_form_factory(FlaskForm)


class MomedictForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VocabForm(MomedictForm, BaseModelForm):
    class Meta:
        model = models.Vocab


class VocabWord(MomedictForm, BaseModelForm):
    class Meta:
        model = models.VocabWord

    # Foreign key
    word_id = fields.HiddenField()
    vocab_id = fields.HiddenField()


class WordForm(MomedictForm, BaseModelForm):
    class Meta:
        model = models.Word

    # Foreign key
    exam_id = fields.HiddenField()


class VocabWordForm(MomedictForm, BaseModelForm):
    class Meta:
        model = models.VocabWord

    # Foreign key
    word_id = fields.HiddenField()
    vocab_id = fields.HiddenField()


class DefinitionForm(MomedictForm, BaseModelForm):
    class Meta:
        model = models.Definition

    # Foreign key
    word_id = fields.HiddenField()


class RegisterForm(FlaskForm):
    name = fields.StringField('Fullname', [validators.required()])
    email = fields.StringField('Email', [validators.required(), validators.email()])
    password = fields.PasswordField('Password', [
        validators.required(),
        validators.EqualTo('confirm', message='Password does not match')
    ])
    confirm = fields.PasswordField('Password confirm', [validators.required()])


class LoginForm(FlaskForm):
    email = fields.StringField('Email', [validators.required(), validators.email()])
    password = fields.PasswordField('Password', [validators.required()])


class ProfileForm(FlaskForm):
    name = fields.StringField('Fullname', [validators.required()])
    email = fields.StringField('Email', [validators.required(), validators.email()])


class CreateVocabForm(FlaskForm):
    name = fields.StringField('Name', [validators.required()])
