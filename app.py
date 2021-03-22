from flask import Flask, jsonify, request
from flask_restplus import Api, Resource,reqparse
from Aicol2020definition import legal_defs
import json

flask_app = Flask(__name__)
app = Api(app = flask_app, version='1.0', title='Extract law definitions', description='This version was tested with "Estatuo de los trabajadores"', default ='Test', default_label='Yo can try it!')


todos={}

class Todo(Resource):
	def post(self, documento):
		salida=legal_defs.main(documento)
		return jsonify(salida)
	
		

app.add_resource(Todo, '/<string:documento>')