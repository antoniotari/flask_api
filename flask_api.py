#!flask/bin/python
from flask import Flask,jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask.ext.httpauth import HTTPBasicAuth

#----resource
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

#----instal virtualenv in the project folder
# apt-get install virtualenvwrapper
#----install flask in the project folder
# $ virtualenv flask
# $ flask/bin/pip install flask
# $ flask/bin/pip install flask-httpauth

#----test the rest api
#- test get request
# $ curl -i http://localhost:5000/todo/api/v1.0/tasks/3
#-------
#- test post request:
# $ curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000
#-------
#- test put request
# $ curl -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/v1.0/tasks/2
#----------------
#- authenticated request
# $ curl -u username:password -i http://localhost:5000/todo/api/v1.0/tasks

auth = HTTPBasicAuth()
app = Flask(__name__)

#----------------
#----------------
tasks = [
	{
		'id': 1,
        	'title': u'Buy groceries',
        	'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        	'done': False
    	},
    	{
        	'id': 2,
        	'title': u'Learn Python',
        	'description': u'Need to find a good Python tutorial on the web', 
        	'done': False
    	}
]

#-------------------------------------------------------
#----------------Let's say we want our web service to only be 
#accessible to username antonio  and password python. We can 
#setup a Basic HTTP authentication as follows:
#-----With the authentication system setup, all that is left is to 
#indicate which functions need to be protected, by adding the 
#@auth.login_required decorator, check get_tasks_auth()
@auth.get_password
def get_password(username):
    	if username == 'antonio':
        	return 'python'
    	return None

#-------------------------------------------------------
#----------------
@auth.error_handler
def unauthorized():
    	return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

#-------------------------------------------------------
#----------------Instead of returning task ids we can return the full URI 
#that controls the task. For this we can write a small helper function 
#that generates a "public" version of a task to send to the client
#All we are doing here is taking a task from our database and creating a 
#new task that has all the fields except id, which gets replaced with 
#another field called uri, generated with Flask's url_for.
#ie: return jsonify( { 'tasks': map(make_public_task, tasks) } )
def make_public_task(task):
	new_task = {}
    	for field in task:
        	if field == 'id':
            		new_task['uri'] = url_for('get_task', task_id = task['id'], _external = True)
        	else:
            		new_task[field] = task[field]
    	return new_task

#-------------------------------------------------------
#----------------
@app.route('/')
def index():
	return "Hello, World!"

#-------------------------------------------------------
#----------------Error response in json format instead of text/html
@app.errorhandler(404)
def not_found(error):
    	return make_response(jsonify( { 'error': 'Not found' } ), 404)

#-------------------------------------------------------
#----------------
@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
def get_tasks():
	return jsonify( { 'tasks': map(make_public_task, tasks) } )
#	return jsonify( { 'tasks': tasks } )

#-------------------------------------------------------
#----------------get task with authentication
@app.route('/todo/api/v1.0/tasksauth', methods = ['GET'])
@auth.login_required
def get_tasks_auth():
	return get_tasks()

#-------------------------------------------------------
#----------------
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['GET'])
def get_task(task_id):
	task = filter(lambda t: t['id'] == task_id, tasks)
    	if len(task) == 0:
        	abort(404)
    	return jsonify( { 'task': task[0] } )

#-------------------------------------------------------
#----------------The request.json will have the request data, but only if 
#it came marked as JSON. If the data isn't there, or if it is there, but 
#we are missing a title item then we return an error code 400, which is 
#the code for the bad request.
#--respond to the client with the added task and send back a status code 
#201, which HTTP defines as the code for "Created"
@app.route('/todo/api/v1.0/tasks', methods = ['POST'])
def create_task():
    	if not request.json or not 'title' in request.json:
        	abort(400)
    	task = {
        	'id': tasks[-1]['id'] + 1,
        	'title': request.json['title'],
        	'description': request.json.get('description', ""),
        	'done': False
    	}
    	tasks.append(task)
    	return jsonify( { 'task': task } ), 201

#-------------------------------------------------------
#----------------
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['PUT'])
def update_task(task_id):
    	task = filter(lambda t: t['id'] == task_id, tasks)
    	if len(task) == 0:
        	abort(404)
    	if not request.json:
        	abort(400)
    	if 'title' in request.json and type(request.json['title']) != unicode:
        	abort(400)
    	if 'description' in request.json and type(request.json['description']) is not unicode:
        	abort(400)
    	if 'done' in request.json and type(request.json['done']) is not bool:
        	abort(400)
    	task[0]['title'] = request.json.get('title', task[0]['title'])
    	task[0]['description'] = request.json.get('description', task[0]['description'])
    	task[0]['done'] = request.json.get('done', task[0]['done'])
    	return jsonify( { 'task': task[0] } )

#-------------------------------------------------------
#----------------
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['DELETE'])
def delete_task(task_id):
    	task = filter(lambda t: t['id'] == task_id, tasks)
    	if len(task) == 0:
        	abort(404)
    	tasks.remove(task[0])
    	return jsonify( { 'result': True } )

#-------------------------------------------------------
#----------------
if __name__ == '__main__':
	app.run(debug = True)