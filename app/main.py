import os
from flask import Flask, jsonify, request
from flask_wtf.csrf import CSRFProtect
from app.models import db, Task

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

app.config.from_object('app.config.Config')
db.init_app(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{"id": t.id, "title": t.title, "done": t.done} for t in tasks])

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    task = Task(title=data['title'], done=data.get('done', False))
    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "title": task.title, "done": task.done}), 201

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=3000, debug=False)