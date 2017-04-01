from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workerdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    team = db.Column(db.String)
    reliability = db.column(db.Integer)
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    deadline = db.Column(db.Integer, nullable=False)
    completed_time = db.Column(db.Integer, default=-1)
    task_name = db.Column(db.String(20), nullable=False)
    user_name = db.Column(db.String(20), db.ForeignKey('person.name'), nullable=False)
    priority = db.Column(db.Integer, nullable=False)



