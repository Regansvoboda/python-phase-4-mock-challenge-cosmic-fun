from flask import Flask, request, make_response, jsonify
# from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError

from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# CORS(app)
migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)

class Scientists(Resource):
    def get(self):
        s_list = []
        for s in Scientist.query.all():
            s_dict = {
                'id': s.id,
                'name': s.name,
                'field_of_study': s.field_of_study,
                'avatar': s.avatar
            }
            s_list.append(s_dict)
        return make_response(s_list, 200)
    def post(self):
        data = request.get_json()
        sc = Scientist(name = data['name'],
                       field_of_study = data['field_of_study'],
                       avatar = data['avatar'])
        try:
            db.session.add(sc)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response( {'error': 'validation errors'}, 422 )
        return make_response(sc.to_dict(), 201)
    
api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        s_instance = Scientist.query.filter_by(id = id).first()
        if s_instance == None:
            return make_response({'error': 'Scientist not found'}, 404)
        return make_response(s_instance.to_dict(), 200)
    
    def patch(self, id):
        s_instance = Scientist.query.filter_by(id = id).first()
        if s_instance == None:
            return make_response({"errors": ["validation errors"]}, 404)
        data = request.get_json()
        for key in data.keys():
            setattr(s_instance, key, data[key])
        db.session.add(s_instance)
        db.session.commit()
        return make_response(s_instance.to_dict(), 200)
    
    def delete(self, id):
        sc = Scientist.query.filter_by(id = id).first()
        if sc == None:
            return make_response({"error": "Scientist not found"}, 404)
        db.session.delete(sc)
        db.session.commit()
        return make_response({'msg': 'Delete successful'}, 200)
        
api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        p_list = []
        for p in Planet.query.all():
            p_dict = {
                'id': p.id,
                'name': p.name,
                'distance_from_earth': p.distance_from_earth,
                'nearest_star': p.nearest_star,
                'image': p.image
            }
            p_list.append(p_dict)
        return make_response(p_list, 200)
    
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        data = request.get_json()
        new_mission = Mission(name = data['name'],
                              scientist_id = data['scientist_id'],
                              planet_id = data['planet_id'])
        try:
            db.session.add(new_mission)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response( {'error': 'validation errors'}, 422 )
        return make_response(new_mission.to_dict(), 201)
    
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555)
