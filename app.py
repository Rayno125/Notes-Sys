from flask import Flask, render_template, url_for, request,redirect,flash, session
from flask_sqlalchemy import SQLAlchemy
from models import Note, User
from db_config import db
from flasgger import Swagger
from time import sleep


#Main parts of app----------------------------------------
app = Flask(__name__)

app.secret_key = 'my_super_secret_key_12345'

swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# db = SQLAlchemy(app)





def check_user(username):
    return User.query.filter_by(username=username).first() is not None


@app.route('/')

def index():
    if 'username' not in session:
        return render_template('index.html',session_html=False)
    else:
        return render_template('index.html',username=session['username'], session_html = True)


    

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
  
# @app.route('/create_user/<username>/<password>')
# def create_user(username, password):
#     user = User(username=username, password=password)
#     db.session.add(user)
#     db.session.commit()
#     return f'Пользователь {username} успешно создан!'


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username):
            flash('Пользователь существует')
            return redirect(url_for('register'))

        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            
            
            return render_template('login.html', form_type = 'register', registered = True, username = username)
    
    return render_template('login.html', form_type = 'register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
    return render_template('login.html', form_type = 'login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

