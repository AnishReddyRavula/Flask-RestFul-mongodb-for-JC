#!/usr/bin/env 
# https://github.com/cdagli/flask-api-starter/blob/master/src/api/routes/routes_general.py
#necessary imports
import flask
from flask import Flask, jsonify, request
from flasgger import Swagger, SwaggerView, Schema, fields
from flasgger.utils import swag_from
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth
import json
import bson.binary
import hashlib
import bson.objectid
import bson.errors
from PIL import Image
from io import StringIO
from io import BytesIO
import datetime
import pymongo
from models.models import Ngouser, Adminuser, Name
from mongoengine import *
from flask import Response
import traceback
from passlib.apps import custom_app_context as pwd_context
#app to hold the flask application
app = Flask(__name__)
auth = HTTPBasicAuth()
Swagger(app)



#app to hold mongodb congifigration
app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
allow_formats = set(['jpeg', 'png', 'gif'])
#mongo variable to have pymongo's app
mongo = PyMongo(app)



from functools import wraps
from flask import request, Response


# def check_auth(username, password):
#     """This function is called to check if a username /
#     password combination is valid.
#     """
    # try:
    # 	usr = Adminuser.objects.filter(username = username)[0]
    # except Exception as e:
    # 	return False
    # if len(usr) == 0:
    # 	return False
    # if usr['password'] == password:
    # 	return True
    # else:
    # 	return False

# def authenticate():
#     """Sends a 401 response that enables basic auth"""
#     return Response(
#     'Could not verify your access level for that URL.\n'
#     'You have to login with proper credentials', 401,
#     {'WWW-Authenticate': 'Basic realm="Login Required"'})

# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth or not check_auth(auth.username, auth.password):
#             return authenticate()
#         return f(*args, **kwargs)
#     return decorated



@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    connect('start')
    print(username, password)
    try:	
    	usr = Adminuser.objects.filter(username = username)[0]
    except Exception as e:
    	print(e)
    	return False
    if len(usr) == 0:
    	return False
    if usr['password'] == password:
    	return True
    else:
    	return False

    


@app.route('/ngo_change/<string:username>', methods=['PUT'])
@auth.login_required
@swag_from('modify_ngouser.yml', methods=['PUT'])
def change_ngouser(username):

	# product = mongo.db.start
	print(request.json)
	connect('start')	#connecting to database
	ngouser_data = request.json 	#getting the posted data


	# parse through the posted data and save it in database
	password = ngouser_data['password']
	name = {}

	#check ofif the username already exists and validate username and password fields
	if username is None or password is None or len(password) < 6:
		return json.dumps({'success':False, 'Exception':'Missing data'}), 400, {'ContentType':'application/json'} # missing arguments
	if Ngouser.objects.filter(username = username).first() is None:
		return json.dumps({'success':False, 'Exception':'No user with that username'}), 400, {'ContentType':'application/json'} # existing user
	if len(username) > 200 and username.len() < 6 :
		return json.dumps({'success':False, 'Exception':'Check username size'}), 400, {'ContentType':'application/json'} # existing user


	if request.method != 'PUT':
		print("shit")

	# get the response appropriately after saving
	try:
		ngouser = Ngouser.objects.get(username=username)
		ngouser['password'] = password
		if 'first_name' not in ngouser_data['name'] and 'last_name'  not in ngouser_data['name']:
			return json.dumps({'success':False, 'Exception':'incorrect format in name'}), 400, {'ContentType':'application/json'} # incorrect format with name
		else:
			ngouser.name = Name(**ngouser_data['name'])

		if ngouser.save(validate=True):
			output = ngouser.to_json()
	except ValidationError as err:
			err = traceback.format_exception_only(type(e), e)
			return json.dumps({'success':False, 'Exception':err}), 400, {'ContentType':'application/json'}
	return json.dumps({'success':True, 'Changed':output}), 201, {'ContentType':'application/json'}


@app.route('/add_ngo_user', methods=['POST'])
@auth.login_required
@swag_from('add_ngouser.yml', methods=['POST'])
def add_ngo_user():

	# product = mongo.db.start
	print(request.json)
	connect('start')	#connecting to database
	ngo_data = request.json 	#getting the posted data
	ngouser = Ngouser()		#model object for ngo user

	# parse through the posted data and save it in database
	username = ngo_data['username']
	password = ngo_data['password']
	name = {}

	# check for correct name format in name request
	if 'first_name' not in ngo_data['name'] and 'last_name'  not in ngo_data['name']:
		return json.dumps({'success':False, 'Exception':'incorrect format in name'}), 400, {'ContentType':'application/json'} # incorrect format with name
	else:
		ngouser.name = Name(**ngo_data['name'])

	#check ofif the username already exists and validate username and password fields
	if username is None or password is None:
		return json.dumps({'success':False, 'Exception':'Missing data'}), 400, {'ContentType':'application/json'} # missing arguments
	if Ngouser.objects.filter(username = username).first() is not None:
		return json.dumps({'success':False, 'Exception':'user already exists'}), 400, {'ContentType':'application/json'} # existing user
	if len(username) > 200 and username.len() < 6 :
		return json.dumps({'success':False, 'Exception':'Check username size'}), 400, {'ContentType':'application/json'} # existing user
	if len(password) > 100 and password.len() < 6 :
		return json.dumps({'success':False, 'Exception':'Check password size'}), 400, {'ContentType':'application/json'} # existing user

	ngouser['username'] = username
	ngouser['password'] = password

	# get the response appropriately after saving
	try:
		if ngouser.save(validate=True):
			output = ngouser.to_json()
	except ValidationError as e:
			err = traceback.format_exception_only(type(e), e)
			return json.dumps({'success':False, 'Exception':err}), 400, {'ContentType':'application/json'}
	return json.dumps({'success':True, 'created':output}), 201, {'ContentType':'application/json'}




@app.route('/users_ngo', methods=['GET'])
@auth.login_required
def list_ngousers():
	"""
	This is the NGO users listing API
    	This API will return all the NGO users registered
	    ---
	    tags:
	       - NGO user operations
	    responses:
	      404:
	        description: Error in the server!
	      200:
	        description: list of al the NGO users
	        schema:
	          id: NGO
	          properties:
	            NGOs:
	              type: array
	              description: The Registered NGO users list
	              items:
	                type: string
	              default: [{"name":"Swarna Homes", "username": "swarna_homes"}]
	"""
	connect('start')	#connecting to database
	ngousers_list = Ngouser.objects.only('username', 'name')
	output = []
	for obj in ngousers_list:
		output.append(json.loads(obj.to_json()))
	print(output)
	return jsonify({'Total NGO\'s' : output})


@app.route('/ngo', methods=['GET'])
@auth.login_required
@swag_from('index.yml')
def ngo_list():
	start = mongo.db.start
	output=[]
	for s in start.find():
		print(s)
		output.append({'name' : s['name'], 'distance' : s['distance']})
	return jsonify({'Total NGO\'s' : output})





@app.route('/ngo/<name>', methods=['GET'])
def get_one_star(name):
	"""
	This is the NGOs listing API
    	This API will return all the NGOs registered
	    ---
	    tags:
	       - NGO user operations
	    
	    responses:
	      404:
	        description: Error in the server!
	      200:
	        description: list of al the NGOs
	        schema:
	          id: NGO
	          properties:
	            
	            NGOs:
	              type: array
	              description: The Registered NGO list
	              items:
	                type: string
	              default: [{"name":"Swarna Homes", "value": 500}]
	"""
	start = mongo.db.start
	s = start.find_one({'name' : name})
	if s:
		output = {'name' : s['name'], 'distance' : s['distance']}
	else:
		output = "No such name"
	return jsonify({'Total NGO\'s' : output})



@app.route('/add_admin', methods=['POST'])
@auth.login_required
def add_admin():
	"""
	Create Admin end point
    	Create Admin end point
	    ---
	    tags:
	       - Create Admin end point
	    parameters:
	      - in: body
	        name: body
	        schema:
	          id: User
	          required:
	            - password
	            - name
	          properties:
	            password:
	              type: string
	              description: password for user
	              default: minimum 6 charachters
	            name:
	              type: object
	              properties:
	                first_name:
	                    type: string
	                    description: First name of user
	                    default: John
	                last_name:
	                  type: string
	                  description: Last name of the user
	                  default: Doe
	            username:
	              type: string
	              description: Username for the login
	              default: john_doe
	    responses:
	      404:
	        description: Key error or bad request
	      201:
	        description: Data posted successfully
	        
	"""

	# product = mongo.db.start
	print(request.json)
	connect('start')	#connecting to database
	admin_data = request.json 	#getting the posted data
	adminuser_obj = Adminuser()		#model object for ngo user

	# parse through the posted data and save it in database
	username = admin_data['username']
	password = admin_data['password']
	name = {}
	if 'first_name' not in admin_data['name'] and 'last_name'  not in admin_data['name']:
		return json.dumps({'success':False, 'Exception':'incorrect format in name'}), 400, {'ContentType':'application/json'} # incorrect format with name
	else:
		adminuser_obj.name = Name(**admin_data['name'])

	if username is None or password is None:
		return json.dumps({'success':False, 'Exception':'Missing data'}), 400, {'ContentType':'application/json'} # missing arguments
	if Adminuser.objects.filter(username = username).first() is not None:
		return json.dumps({'success':False, 'Exception':'user already exists'}), 400, {'ContentType':'application/json'} # existing user
	if len(username) > 200 and len(username) < 6 :
		return json.dumps({'success':False, 'Exception':'Check username size'}), 400, {'ContentType':'application/json'} # existing user
	if len(password) > 100 and len(password) < 6 :
		return json.dumps({'success':False, 'Exception':'Check password size'}), 400, {'ContentType':'application/json'} # existing user

	adminuser_obj['username'] = username
	adminuser_obj['password'] = password

	# get the response appropriately after saving
	try:
		if adminuser_obj.save(validate=True):
			output = adminuser_obj.to_json()
	except ValidationError as e:
			err = traceback.format_exception_only(type(e), e)
			return json.dumps({'success':False, 'Exception':err}), 400, {'ContentType':'application/json'}
	return json.dumps({'success':True, 'created':output}), 201, {'ContentType':'application/json'}







#this mehtod is to save the file in the database
def save_file(f):
	#get the mongo collections instance
	start = mongo.db.start

	#get the content into bytes format
	content = BytesIO(f.read())
	
	try:
		#get the format of the document
		mime = Image.open(content).format.lower()

		#check is the format is not in the specified format
		if mime not in allow_formats:
	  		raise IOError()
	except IOError:
		flask.abort(400)

	#get the checksum of the image
	sha1 = hashlib.sha1(content.getvalue()).hexdigest()

	#make a dictionary that needs to be saved in the database, with content, format, time, and checksum
	c = dict(
		content=bson.binary.Binary(content.getvalue()),
		mime=mime,
		time=datetime.datetime.utcnow(),
		sha1=sha1,
		)
	#try saving the data
	try:
		start.files.save(c)
	except pymongo.errors.DuplicateKeyError:
		return jsonify({'result' : "already uploaded"})
	return jsonify({'sha':sha1})

@app.route('/f/<sha1>')
def serve_file(sha1):
	start = mongo.db.start
	try:
		f = start.files.find_one({'sha1': sha1})
		if f is None:
			raise bson.errors.InvalidId()
		if request.headers.get('If-Modified-Since') == f['time'].ctime():
			return Response(status=304)
		resp = Response(f['content'], mimetype='image/' + f['mime'])
		resp.headers['Last-Modified'] = f['time'].ctime()
		return resp
	except bson.errors.InvalidId:
		flask.abort(404)

@app.route('/upload', methods=['POST'])
def upload():
	print(request.files['uploaded_file'])
	f = request.files['uploaded_file']
	sha1 = save_file(f)
	# return flask.redirect('/f/'+str(fid))
	return jsonify({'result' : 'cool'})

@app.route('/start', methods=['POST'])
def add_start():
	star = mongo.db.start
	print((request.get_json()))
	name = request.json['name']
	distance = request.json['distance']
	output = []
	old_star = star.find_one()
	print(old_star)
	star_id = star.insert({'name': name, 'distance': distance, 'old' : old_star})
	new_star = star.find_one({'_id': star_id })
	output = {'name' : new_star['name'], 'distance' : new_star['distance']}
	return jsonify({'result' : output})

@app.route('/add_pro', methods=['POST'])
def add_product():
	"""
	This is the NGOs listing API
	    This API will return all the NGOs registered
	    ---
	    tags:
	      - Internships operations
	    
	    responses:
	      404:
	        description: Error in the server!
	      200:
	        description: list of al the NGOs
	        schema:
	          id: NGO
	          properties:
	            
	            NGOs:
	              type: array
	              description: The Registered NGO list
	              items:
	                type: string
	              default: [{"name":"Swarna Homes", "value": 500}]
	"""
	product = mongo.db.start
	print(request.get_json())
	print((request.get_json()))
	name = request.json['name']
	price = request.json['price']
	product_id = product.product.insert({'name': name, 'price': price})
	print(product_id)
	new_product = product.product.find_one({'_id': product_id })
	output = {'name' : new_product['name'], 'price' : new_product['price']}
	return jsonify({'result' : output})


@app.route('/pro_lis', methods=['GET'])
@auth.login_required
def products():
	"""
	This is the NGOs listing API
	    This API will return all the NGOs registered
	    ---
	    tags:
	      - users

	"""
	product = mongo.db.start
	output=[]
	maximum_price = int(request.args.get('max')) if request.args.get('max') else 0
	print(product.product.find({"price": {"$gt": maximum_price}}).count())
	for s in product.product.find({"price": {"$gt": maximum_price}}):
		print(s)
		output.append({'name' : s['name'], 'price' : s['price']})
	return jsonify({'result' : output})

@auth.login_required
@app.route('/pro_list/<maximum_price>/<search>',defaults={'search': None}, methods=['GET'])
@app.route('/pro_list/<search>', methods=['GET'])
def products_maximum(maximum_price=None, search=None):
	"""
	This is the NGOs listing API
	    This API will return all the NGOs registered
	    ---
	    tags:
	      - users
	    parameters:
	      - name: maximum_price
	        in: path
	        type: integer
	        description: size of awesomeness
	        required: false
	      - name: search
	        in: path
	        type: string
	        description: size of awesomeness
	        required: false
	"""
	product = mongo.db.start
	output=[]
	print(search)
	if search:
		for s in product.product.find({"name": search}):
			print(s)
			output.append({'name' : s['name'], 'price' : s['price']})

	elif maximum_price:
		for s in product.product.find({"price": {"$gt": maximum_price}}):
			print(s)
			output.append({'name' : s['name'], 'price' : s['price']})
	else:
		for s in product.product.find():
			print(s, "elif")
			output.append({'name' : s['name'], 'price' : s['price']})

	return jsonify({'result' : output})

@app.route('/pro_lis/<name>', methods=['GET'])
def get_product(name):
	product = mongo.db.start
	maximum_price = int(request.args.get('max'))
	s = product.product.find_one({'name' : name, "price": {"$gt": maximum_price}})
	if s:
		output = {'name' : s['name'], 'price' : s['price']}
	else:
		output = "No such product"
	return jsonify({'result' : output})

@app.route('/')
def hello_world():
	return ('Hello World')

if __name__ == '__main__':
	app.run(debug=True)