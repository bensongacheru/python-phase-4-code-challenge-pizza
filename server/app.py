#!/usr/bin/env python3

from models import db, Restaurant, Pizza, RestaurantPizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class RestaurantResource(Resource):
    def get(self, id=None):
        if id is None:
            restaurants = Restaurant.query.all()
            return make_response([restaurant.to_dict() for restaurant in restaurants], 200)
        else:
            restaurant = db.session.get(Restaurant, id)  # Updated
            if restaurant:
                restaurant_data = restaurant.to_dict()
                # Fetch associated restaurant_pizzas
                restaurant_data['restaurant_pizzas'] = [
                    rp.to_dict() for rp in restaurant.restaurant_pizzas
                ]
                return make_response(restaurant_data, 200)
            return make_response({"error": "Restaurant not found"}, 404)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)  # Updated
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response({}, 204)
        return make_response({"error": "Restaurant not found"}, 404)

class PizzaResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response([pizza.to_dict() for pizza in pizzas], 200)

class RestaurantPizzaResource(Resource):
    def get(self):
        # Retrieve all restaurant_pizzas
        restaurant_pizzas = RestaurantPizza.query.all()
        return make_response([rp.to_dict() for rp in restaurant_pizzas], 200)

    def post(self):
        data = request.get_json()
        try:
            price = data['price']
            # Validate the price before creating the RestaurantPizza
            if price < 1 or price > 30:
                return make_response({"errors": ["validation errors"]}, 400)

            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return make_response(restaurant_pizza.to_dict(), 201)
        except ValueError as e:
            return make_response({"errors": [str(e)]}, 400)

# Register resources with their respective routes
api.add_resource(RestaurantResource, '/restaurants', '/restaurants/<int:id>')
api.add_resource(PizzaResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

@app.route('/')
def index():
    return make_response('<h1>Code challenge</h1>', 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)