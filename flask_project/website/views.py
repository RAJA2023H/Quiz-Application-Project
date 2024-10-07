from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
from .models import Note

views = Blueprint('views', __name__)

"""-------this part could be replaced later with data from a database------"""
quiz_data = {
    "title": "Python Basics Quiz",
    "questions": [
        {
            "id": 1,
            "text": "What is the correct file extension for Python files?",
            "options": [".pt", ".py", ".python", ".pyt"],
            "answer": ".py"
        },
        {
            "id": 2,
            "text": "Which keyword is used to define a function in Python?",
            "options": ["func", "def", "define", "function"],
            "answer": "def"
        }
    ]
}
"""------------"""

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')
    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        user_answers = {}
        for question in quiz_data["questions"]:
            selected_option = request.form.get(f"question_{question['id']}")
            user_answers[question['id']] = selected_option
        correct_answers = 0
        for question in quiz_data["questions"]:
            if user_answers[question['id']] == question["answer"]:
                correct_answers += 1

        score = correct_answers
        flash(f'You scored {score} out of {len(quiz_data["questions"])}', category='success')

        return render_template('quiz_results.html', result={"score": score, "quiz": quiz_data})
    return render_template('quiz.html', quiz=quiz_data, questions=quiz_data["questions"])