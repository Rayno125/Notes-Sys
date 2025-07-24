from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from models import Note, User
from db_config import db






app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# db = SQLAlchemy(app)



@app.route('/')

def index():
    return render_template('index.html')



@app.route('/add/<username>')
def add_note(username):
    user = User.query.filter_by(username=username).first()

    
    
    new_note = Note(title="Пример", content="Это содержимое", user_id=user.id)
    db.session.add(new_note)
    db.session.commit()
    return f"Заметка добавлена на аккаунт {username}"
        

@app.route('/notes/<username>')
def get_notes(username):
    user = User.query.filter_by(username=username).first()

    notes = Note.query.filter_by(user_id=user.id).all()

    
    
    return {note.id: note.title + '/'+ note.content for note in notes}
  
@app.route('/create_user/<username>')
def create_user(username):
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return f'Пользователь {username} успешно создан!'



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

