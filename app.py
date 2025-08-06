from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/taskdb'
db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    hashed_pw = generate_password_hash(data['password'])
    user = User(username=data['username'], password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if request.method == 'GET':
            tasks = Task.query.filter_by(user_id=data['user_id']).all()
            return jsonify([{'id': t.id, 'title': t.title, 'completed': t.completed} for t in tasks])
        elif request.method == 'POST':
            req = request.json
            task = Task(title=req['title'], completed=False, user_id=data['user_id'])
            db.session.add(task)
            db.session.commit()
            return jsonify({'id': task.id, 'title': task.title, 'completed': task.completed}), 201
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def task_detail(task_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        task = Task.query.filter_by(id=task_id, user_id=data['user_id']).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        if request.method == 'PUT':
            req = request.json
            task.title = req.get('title', task.title)
            task.completed = req.get('completed', task.completed)
            db.session.commit()
            return jsonify({'id': task.id, 'title': task.title, 'completed': task.completed})
        elif request.method == 'DELETE':
            db.session.delete(task)
            db.session.commit()
            return jsonify({'result': 'Task deleted'})
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)