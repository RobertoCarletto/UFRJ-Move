from flask .views import MethodView 
from flask import jsonify 
from flask_jwt_extended import jwt_required ,get_jwt_identity 
from app .extensions import db 
from .models import User 
from .schemas import UserSchema 

class ProfileAPI (MethodView ):
    decorators =[jwt_required ()]

    def get (self ):
        current_user_id =get_jwt_identity ()
        user =db .session .get (User ,current_user_id )

        if not user :
            return jsonify ({'error':'Usuário não encontrado'}),404 

        schema =UserSchema ()
        return jsonify (schema .dump (user )),200 
