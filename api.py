from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Note, User
from flasgger import Swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from datetime import timedelta
from pydantic import ValidationError
from schemas import UserRegisterSchema, UserLoginSchema, NoteSchema

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'super-secret-jwt-key-12345'  # Сменить на свой!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

db.init_app(app)
jwt = JWTManager(app)
swagger = Swagger(app)

def check_user(username):
    return User.query.filter_by(username=username).first() is not None

@app.route('/')
def index():
    """
    Проверка работы API
    ---
    get:
      tags:
        - Общие
      responses:
        200:
          description: API работает
          schema:
            type: object
            properties:
              message:
                type: string
                example: API is running
    """
    return jsonify({'message': 'API is running'}), 200

@app.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя
    ---
    tags:
      - Пользователь
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: Данные для регистрации
        required: true
        schema:
          type: object
          required:
            - email
            - username
            - password
          properties:
            email:
              type: string
              example: user@example.com
            username:
              type: string
              example: user123
            password:
              type: string
              example: secret123
    responses:
      201:
        description: Пользователь успешно зарегистрирован
      400:
        description: Ошибка валидации данных
      409:
        description: Пользователь уже существует
    """
    try:
        data = UserRegisterSchema.parse_obj(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400

    if check_user(data.username):
        return jsonify({'error': 'User already exists'}), 409

    user = User(email=data.email, username=data.username)
    user.set_password(data.password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Вход выполнен',
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@app.route('/login', methods=['POST'])
def login():
    """
    Вход пользователя
    ---
    tags:
      - Пользователь
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: Данные для входа
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: user123
            password:
              type: string
              example: secret123
    responses:
      200:
        description: Успешный вход, возвращается токен доступа
        schema:
          type: object
          properties:
            access_token:
              type: string
      400:
        description: Ошибка валидации данных
      401:
        description: Неверный логин или пароль
    """
    try:
        data = UserLoginSchema.parse_obj(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400

    user = User.query.filter_by(username=data.username).first()
    if user and user.check_password(data.password):
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
              'message': 'Вход выполнен',
              'access_token': access_token,
              'refresh_token': refresh_token
          }), 200

    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    # При желании можно обновлять и refresh токен
    new_refresh_token = create_refresh_token(identity=current_user_id)

    return jsonify({
        'access_token': new_access_token,
        'refresh_token': new_refresh_token  # если будешь обновлять refresh токен
    }), 200



@app.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """
    Получить все заметки пользователя
    ---
    tags:
      - Заметки
    security:
      - Bearer: []
    responses:
      200:
        description: Список заметок
        schema:
          type: object
          properties:
            notes:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  content:
                    type: string
      401:
        description: Нет доступа
      404:
        description: Пользователь не найден
    """
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    notes = Note.query.filter_by(user_id=user.id).all()
    notes_list = [note.to_dict() for note in notes]
    return jsonify({'notes': notes_list}), 200

@app.route('/add_note', methods=['POST'])
@jwt_required()
def add_note():
    """
    Добавить новую заметку
    ---
    tags:
      - Заметки
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: Данные заметки
        required: true
        schema:
          type: object
          required:
            - title
            - content
          properties:
            title:
              type: string
              example: Пример заметки
            content:
              type: string
              example: Это содержимое заметки.
    responses:
      201:
        description: Заметка успешно добавлена
        schema:
          type: object
          properties:
            message:
              type: string
            note_id:
              type: integer
      400:
        description: Ошибка валидации данных
      401:
        description: Нет доступа
      404:
        description: Пользователь не найден
    """
    try:
        data = NoteSchema.parse_obj(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400

    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_note = Note(title=data.title, content=data.content, user_id=user.id)
    db.session.add(new_note)
    db.session.commit()

    return jsonify({'message': 'Note added', 'note_id': new_note.id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
