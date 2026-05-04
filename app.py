from flask import Flask, request, jsonify, render_template
from extensions import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret123'

db.init_app(app)

from models import User, Project, Task

with app.app_context():
    db.create_all()


# ------------------ AUTH ------------------

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not name or not email or not password or not role:
            return jsonify({"error": "All fields are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "User already exists"}), 400

        user = User(name=name, email=email, password=password, role=role)

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Signup successful"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        user = User.query.filter_by(email=email, password=password).first()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "role": user.role
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ PROJECT ------------------

@app.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        name = data.get('name')
        created_by = data.get('created_by')

        if not name or not created_by:
            return jsonify({"error": "Missing fields"}), 400

        project = Project(name=name, created_by=created_by)

        db.session.add(project)
        db.session.commit()

        return jsonify({"message": "Project created"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/projects', methods=['GET'])
def get_projects():
    try:
        projects = Project.query.all()

        result = []
        for p in projects:
            result.append({
                "id": p.id,
                "name": p.name,
                "created_by": p.created_by
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ TASK ------------------

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        title = data.get('title')
        assigned_to = data.get('assigned_to')
        project_id = data.get('project_id')

        if not title or not assigned_to or not project_id:
            return jsonify({"error": "Missing required fields"}), 400

        task = Task(
            title=title,
            description=data.get('description', ''),
            assigned_to=assigned_to,
            project_id=project_id,
            status="Pending"
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({"message": "Task created"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    try:
        task = Task.query.get(id)

        if not task:
            return jsonify({"error": "Task not found"}), 404

        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        task.status = data.get('status', task.status)

        db.session.commit()

        return jsonify({"message": "Task updated"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()

        result = []
        for t in tasks:
            result.append({
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "assigned_to": t.assigned_to,
                "project_id": t.project_id
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ DASHBOARD API ------------------

@app.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        total = Task.query.count()
        completed = Task.query.filter_by(status="Completed").count()
        pending = Task.query.filter_by(status="Pending").count()

        return jsonify({
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ FRONTEND ROUTES ------------------

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard-page')
def dashboard_page():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)