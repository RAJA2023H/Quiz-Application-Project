import unittest
from sqlalchemy import inspect
from flask import Flask
from website import create_app, db
from flask_login import LoginManager
from flask_login import current_user
from website.models import Note, User
import json
from werkzeug.security import generate_password_hash

class TestApp(unittest.TestCase):
    """testing the app features"""

    def setUp(self):
        """set up testing envirement"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.test_user = User(email='test@example.com', first_name='Test', password=generate_password_hash('password', method='pbkdf2:sha256'))
        db.session.add(self.test_user)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        """clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_init(self):
        """Test if the app is created"""
        self.assertIsInstance(self.app, Flask)

        """Test if the database is created"""
        """from website.models import User, Note"""
        inspector = inspect(db.engine)
        self.assertTrue(inspector.get_table_names())

        """Test if login manager is initialized"""
        self.assertIsInstance(self.app.login_manager, LoginManager)

    def test_home(self):
        """Test that the home route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'login', response.data)

    def test_note(self):
        """Test note method"""
        with self.client:

            response = self.client.post('/login', data=dict(email=self.test_user.email, password='password'))
            self.assertEqual(response.status_code, 302)

            response = self.client.post('/', data=dict(note="This is a test note"), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            note = Note.query.filter_by(user_id=self.test_user.id).first()
            print("Note after insertion:", note)
            self.assertIsNotNone(note)
            self.assertEqual(note.data, "This is a test note")

            response = self.client.post('/delete-note', data=json.dumps({'noteId': note.id}), content_type='application/json')
            self.assertEqual(response.status_code, 200)

            deleted_note = Note.query.filter_by(id=note.id).first()
            self.assertIsNone(deleted_note)

    if __name__ == "__main__":
        unittest.main()
