from flask import Flask, abort
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from create import db, Person, Task
from combine import *
import time

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Tracker API',
    description='A Work Tracker API',
)
db.create_all()
ns = api.namespace('tracker', description='Tracker operations')



person = api.model('Person', {
    'name': fields.String(required=True, description='Name of worker'),
    'team': fields.String(required=True, description='The team worker belongs to')
})

task = api.model('Task', {
    'deadline': fields.Integer,
    'completed_time': fields.Integer,
    'task_id': fields.Integer,
    'task_name': fields.String(required=True, description='Name of Task'),
    'user_name': fields.String(required=True, description='Worker the task is assigned to'),
    'priority': fields.Integer(required=True, description='Priority of the task'),
})

task_id = api.model('TaskID', {
    'deadline': fields.Integer,
    'task_id': fields.Integer,
    'task_name': fields.String(required=True, description='Name of Task'),
    'user_name': fields.String(required=True, description='Worker the task is assigned to'),
    'priority': fields.Integer(required=True, description='Priority of the task'),
})

# parser for worker
parser_person = api.parser()
parser_person.add_argument('name', type=str, required=True, help='Name of worker', location='form')
parser_person.add_argument('team', type=str, required=True, help='Team of worker', location='form')

# parser to delete worker
parser_person_delete = api.parser()

parser_person_delete.add_argument('name', type=str, required=True, help='Name of worker to be removed', location='form')
# parser for task

parser_task = api.parser()
parser_task.add_argument('deadline', type=str, required=True, help='Deadline of task', location='form')
parser_task.add_argument('task_name', type=str, required=True, help="Name of the task", location='form')
parser_task.add_argument('user_name', type=str, required=True, help="Worker the task is assigned to", location='form')
parser_task.add_argument('priority', type=str, required=True, help="Priority of task")

parser_get_task = api.parser()
parser_get_task.add_argument('user_name', type=str, required=True, help="Worker the task is assigned to", location='form')

parser_completion = api.parser()
parser_completion.add_argument('completed_time', type=int, required=True, help='Task ID', location='form')

@ns.route('/worker')
class User(Resource):
    """Operation to Add and View workers"""
    @api.marshal_list_with(person)
    def get(self):
        """Get all the workers"""
        persons = Person.query.all()
        return [{'name':person.name, 'team':person.team} for person in persons]

    @api.doc(parser=parser_person)
    @api.marshal_with(person, code=201)
    def post(self):
        """Enter a new Worker"""
        args = parser_person.parse_args()
        response_body = {'name': args["name"],
                         'team': args["team"]}
        db.session.add(Person(name=args["name"], team=args["team"]))
        db.session.commit()
        return response_body, 201

    @api.doc(parser=parser_person_delete)
    def delete(self):
        """Delete Worker"""
        args = parser_person_delete.parse_args()
        worker = Person.query.filter_by(name=args["name"]).first()
        if not worker:
            abort(400, 'No worker named \'%s\' ' % args["name"])
        task = Task.query.filter_by(user_name=worker.name).first()
        if task:
            abort(400, 'Can not delete worker with task remaining')
        db.session.delete(worker)
        db.session.commit()



@ns.route('/task')
class Tasks(Resource):
    @api.marshal_list_with(task)
    def get(self):
        """Get all pending tasks"""
        tasks = Task.query.filter_by(completed_time=-1).all()
        return [{'task_id':task.id, 'task_name': task.task_name, 'user_name': task.user_name, 'deadline': task.deadline,
                 'priority': task.priority} for task in tasks]

    @api.doc(parser=parser_task)
    @api.marshal_with(task, code=201)
    def post(self):
        """Enter a new task"""
        args = parser_task.parse_args()
        response_body = {'task_name': args["task_name"],
                         'user_name': args["user_name"],
                         'deadline': args["deadline"],
                         'priority': args["priority"],
                         }
        worker = Person.query.filter_by(name=args["user_name"]).first()
        if not worker:
            abort(400, 'Worker %s does not exist. A Task can only be assigned to existing worker' % (args["user_name"]))

        db.session.add(Task(task_name=args["task_name"], user_name=args["user_name"], priority=args["priority"],
                            deadline=args["deadline"]))
        db.session.commit()
        return response_body, 201

@ns.route('/task/<string:user_name>')
class GetTaskByWorkerName(Resource):
    @api.marshal_list_with(task_id)
    def get(self, user_name):
        """Get Task of specific worker"""

        tasks = Task.query.filter_by(user_name=user_name).all()
        return [{'task_id':task.id, 'completed': task.completed_time, 'task_name': task.task_name, 'user_name': task.user_name, 'deadline': task.deadline,
                 'priority': task.priority} for task in tasks]

@ns.route('/task/<int:task_id>')
class TaskById(Resource):
    @api.marshal_list_with(task_id)
    def get(self, task_id):
        """Get Task By it's ID"""
        worker = Person.query.filter_by(user=user_name).first()
        if not worker:
            abort(400, 'No worker named \'%s\' ' % user_name)

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            abort(400, 'Task with ID %s does not exist.' % (task_id))
        return [{'task_id': task.id, 'task_name': task.task_name, 'user_name': task.user_name, 'deadline': task.deadline,
             'priority': task.priority}]

    @api.doc(parser=parser_completion)
    @api.marshal_with(task, code=201)
    def post(self, task_id):
        """Completion of Task"""
        args = parser_completion.parse_args()
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            abort(400, 'Task with ID %s does not exist.' % (task_id))
        task.completed_time = args["completed_time"]
        db.session.commit()
        return [{'task_id': task.id, 'task_name': task.task_name, 'user_name': task.user_name, 'deadline': task.deadline,
             'priority': task.priority}]

    def delete(self, task_id):
        """Delete Task"""

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            abort(400, 'Task with ID %s does not exist.' % (task_id))
        db.session.delete(task)
        db.session.commit()

@ns.route('/graph/<string:user_name>')
class GetReport(Resource):
    def get(self, user_name):
        """Get Report of a worker"""
        worker = Person.query.filter_by(name=user_name).first()
        if not worker:
            abort(400, 'No worker named \'%s\' ' % user_name)
        tasks = Task.query.filter_by(user_name=user_name).all()
        tasks_as_list = [{'task_id': task.id, 'task_name': task.task_name, 'completed': task.completed_time,
                          'user_name': task.user_name, 'deadline': task.deadline,
                          'priority': task.priority} for task in tasks]
        data_analysis(tasks_as_list, user_name)
        return tasks_as_list, 200

if __name__ == '__main__':
    app.run(debug=True)