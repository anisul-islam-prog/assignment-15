import pytest
from app.main import app, db
from app.models import Task

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_create_task(client):
    response = client.post('/tasks', json={"title": "Learn DevOps"})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == "Learn DevOps"
    assert data['done'] is False

def test_create_task_missing_title(client):
    response = client.post('/tasks', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_get_tasks(client):
    client.post('/tasks', json={"title": "Task 1"})
    client.post('/tasks', json={"title": "Task 2"})
    response = client.get('/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

def test_delete_task(client):
    create_resp = client.post('/tasks', json={"title": "Delete me"})
    task_id = create_resp.get_json()['id']
    
    delete_resp = client.delete(f'/tasks/{task_id}')
    assert delete_resp.status_code == 200
    
    get_resp = client.get('/tasks')
    assert len(get_resp.get_json()) == 0