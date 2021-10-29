from flask import Flask, request, jsonify
import json
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./sql_app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #zmniejsza zużycie pamięci - wyłącza info o zmianach

db = SQLAlchemy(app)


class Routes(db.Model):
	__tablename__ = "routes"
	id = db.Column(db.Integer, primary_key = True, index = True)
	name = db.Column(db.String, unique = True, index = True)
	route = db.Column(db.PickleType, default = [])
	max_min_route = db.Column(db.PickleType, default = [])

@app.route('/route/', methods = ['POST'])
def save_route():
	route_json = (request.get_json(force = True))# force jeśli dane idą bez nagłówka json
	temp = ([{"lat_max": max([dic['latitude'] for dic in route_json['route']]),
					"lat_min": min([dic['latitude'] for dic in route_json['route']]),
					"long_max" : max([dic['latitude'] for dic in route_json['route']]),
					"long_min" : min([dic['latitude'] for dic in route_json['route']])}])

	db.session.add(Routes(name = route_json['name'], route = (route_json['route']), max_min_route = temp))
	try:
		db.session.commit()
		return jsonify(Saved = 'Successfully')
	except:
		return jsonify(Saved = 'Failure')	

# curl -H "Content-Type: application/json" --request GET http://127.0.0.1:5000/route/get_names



@app.route('/route/get_names', methods = ['GET'])
def load_route():
	routes = Routes.query.all()
	return jsonify([routes[i].name for i in range(len(routes))])

# curl -H "Content-Type: application/json" --request GET http://127.0.0.1:5000/route/get_all_latlong


@app.route('/route/get_all_latlong', methods = ['GET'])
def load_latlongs():
	routes = Routes.query.all()
	return jsonify([routes[i].max_min_route for i in range(len(routes))])
	
# curl -H "Content-Type: application/json" --request GET http://127.0.0.1:5000/route/nazwa_trasy

@app.route('/route/<route_name>', methods = ['GET'])
def find_route_by_name(route_name):
	routes = Routes.query.filter_by(name = route_name).first_or_404(
									description='There is no data with {}'.format(route_name))
	return jsonify(name = routes.name, route = routes.route)



# curl -H "Content-Type: application/json" --request POST -d '{"lat_min": 53, "lat_max":60, "long_min": 10, "long_max": 90}' http://127.0.0.1:5000/route/latlong

@app.route('/route/latlong', methods = ['POST'])
def find_route_by_latlont():
	route_json = (request.get_json(force = True))
	routes = Routes.query.all()
	id_list = []
	for r in routes:
		if r.max_min_route[0]['lat_min'] >= route_json['lat_min'] and r.max_min_route[0]['lat_max'] <= route_json['lat_max'] and r.max_min_route[0]['long_min'] >= route_json['long_min'] and r.max_min_route[0]['long_max'] <= route_json['long_max']:
			id_list.append(r.id)	
	return jsonify(id_list)
			