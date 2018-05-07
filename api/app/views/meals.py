from flask import json, request
from flask_restful import reqparse, Resource
from app.models import db, Meal, User
from flask_jwt_extended import (
                                JWTManager, jwt_required, 
                                create_access_token,
                                get_jwt_identity)
from app.views.auth.validate import *


class MealOptions(Resource):
    """
    Enables Registered Cater/Admin to  add,Update,Delete and get Database
    """
    
    @jwt_required
    @require_admin    
    def get(self, id):
        """
        Method gets a single meal by its  id.
        """
        active_user = User.query.filter_by(email=get_jwt_identity()).first()
        meal = Meal.query.filter_by(id=id).first()
        if meal is None:
            return {"status": "Failed",
                    "message": "Meal with that id does not exist"}, 404
        if meal.user_id == active_user.id:
            response = meal.json_dump()
            return response
        return {'message': 'Meal does not exist'}, 404

    @jwt_required
    @require_admin
    def put(self, id):
        """
        Method updates single selected meal using its id.
        """
        json_data = request.get_json(force=True)

        if 'meal_name' not in json_data or 'price' not in json_data:
            return {"status": "Failure", 
                    "message": "Please provide a meal a name or price."}, 406
        
        meal_name = json_data['meal_name']
        meal_price = json_data['price']
        active_user = User.query.filter_by(email=get_jwt_identity()).first()
        meal = Meal.query.filter_by(id=id).first()

        if meal is None:
            return {"status": "Failure",
                    "message": "Enter a valid meal id"}, 404
        
        if meal.user_id == active_user.id:
            if meal_name == '' or not mealname_and__menuitem_validator(json_data['meal_name']) or meal_price == '':
                return {"status": "Failure",
                        "message": "Enter Valid meal Detalisl"}, 406
            else:
                meal.meal_name = meal_name
                meal.meal_price = meal_price
                db.session.commit()
                response = meal.json_dump()
                return{"status": "success", "message": response}, 200

        return {'message': 'meal Does not exit'}, 404

    @jwt_required
    @require_admin
    def delete(self, id):
        """
         Method deletes a meal by id.
        """
        json_data = request.get_json(force=True)
        current_user = User.query.filter_by(email=get_jwt_identity()).first()
        meal = Meal.query.filter_by(id=id).first()

        if meal is None:
            return {"status": "Failed!!",
                    "message": "Enter a valid meal id"}, 404

        if meal.user_id == current_user.id:
            Meal.query.filter_by(id = id).delete()
            db.session.commit()
            response = json.loads(json.dumps(json_data))
            return {"status": "deleted!", "message": response}, 200

        return {'Message': 'Meal Does not exit'}, 404


class MealLists(Resource):
    """
    MealList is for Geting all the meals in the Database
    """
    @jwt_required
    @require_admin    
    def get(self):
        
        """
        Getting Meals Lists
        """
        current_user = User.query.filter_by(email=get_jwt_identity()).first()
        meals = Meal.query.filter_by(user_id=current_user.id)

        if meals is None:
            return{"message": "No Meal List At The Moment"}
        response = [meal.json_dump() for meal in meals]
        return {"status": "success", "message": response}, 200

    @jwt_required
    @require_admin
    def post(self):
        """
         Posting Meals
        """
        json_data = request.get_json(force=True)

        if 'meal_name' not in json_data or 'price' not in json_data:
            return {"status": "Failed!", 
                    "message": "Enter correct meal_name and price."}, 406

        meal_name = space_stripper(json_data['meal_name'])
        meal_price = json_data['price']

        if meal_name == '' or not name_validator(meal_name) or meal_price == '':
            return {"status": "Failed",
                    "message": "Enter a valid meal Details"}, 406

        current_user = User.query.filter_by(email=get_jwt_identity()).first()
        user_id = current_user.id
        meal = Meal(meal_name=meal_name, 
                    user_id=user_id,
                    meal_price=meal_price)
        meal.save()
        response = json.loads(json.dumps(meal.json_dump()))
        return {"status": "success", "message": response}, 201

    
