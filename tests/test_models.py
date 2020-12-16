from momedict.database import db
from momedict import models

from tests import DatabaseTestCase


class ModelTestCase:
    model = None

    def create(self):
        return self.model()

    def edit(self, object):
        raise NotImplementedError

    def test_add(self):
        object = self.create()
        db.session.add(object)
        db.session.commit()

        assert object in db.session
        self.assertIsNotNone(self.model.query.get(object.id))

    def test_edit(self):
        object = self.create()
        db.session.add(object)
        db.session.commit()

        object_copy = self.copy_object(object)

        self.assertTrue(self.equal_keys(object, object_copy))

        self.edit(object)
        db.session.add(object)
        db.session.commit()
        self.assertFalse(self.equal_keys(object, object_copy))

    def copy_object(self, object):
        object_keys = object.__table__.columns.keys()
        object_keys.remove('id')
        return {key: getattr(object, key) for key in object_keys}

    def equal_keys(self, object, object2):
        for key in object2.keys():
            if getattr(object, key) != object2[key]:
                return False
        return True

    def test_delete(self):
        object = self.create()
        db.session.add(object)
        db.session.commit()

        self.assertIsNotNone(self.model.query.get(object.id))
        db.session.delete(object)
        db.session.commit()
        assert object not in db.session
        self.assertIsNone(self.model.query.get(object.id))


class TestUserModel(ModelTestCase, DatabaseTestCase):
    model = models.User

    def edit(self, user):
        user.name = "User"
        user.email = "user"


class TestWordModel(ModelTestCase, DatabaseTestCase):
    model = models.Word

    def create(self):
        return self.model(id="TEST WORD", pronunciation="Test Word Pro")

    def edit(self, course):
        course.code = "TEST WORD 2"
        course.name = "Test Word Pro 2"


class TestVocabModel(ModelTestCase, DatabaseTestCase):
    model = models.Vocab

    def edit(self, vocab):
        vocab.name = "Exam"


class TestDefinitionModel(ModelTestCase, DatabaseTestCase):
    model = models.Definition

    def edit(self, definition):
        definition.text = "Text"
