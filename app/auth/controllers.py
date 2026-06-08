from flask .views import MethodView 
from flask import request ,jsonify 
from flask_jwt_extended import create_access_token 
from app .extensions import db 
from app .user .models import User 
from app .user .schemas import UserSchema 
from marshmallow import ValidationError 

class RegisterAPI (MethodView ):
    def post (self ):

        data =request .get_json ()

        if not data :
            return jsonify ({'error':'Nenhum dado fornecido'}),400 

        password =data .get ('password')
        if not password or len (password )<6 :
            return jsonify ({'error':'A senha é obrigatória e deve ter pelo menos 6 caracteres'}),400 

        validation_data =data .copy ()
        validation_data .pop ('password',None )

        schema =UserSchema ()
        try :

            user_data =schema .load (validation_data )
        except ValidationError as err :

            return jsonify ({'errors':err .messages }),400 

        if User .query .filter_by (email =user_data .email ).first ():
            return jsonify ({'error':'Este e-mail já está em uso'}),409 


        clean_cpf ="".join (filter (str .isdigit ,user_data .cpf ))
        if User .query .filter_by (cpf =clean_cpf ).first ():
            return jsonify ({'error':'Este CPF já está em uso'}),409 

        new_user =User (name =user_data .name ,email =user_data .email ,cpf =clean_cpf )
        new_user .set_password (password )

        try :
            db .session .add (new_user )
            db .session .commit ()
            return jsonify ({
            'message':'Usuário cadastrado com sucesso',
            'user':schema .dump (new_user )
            }),201 
        except Exception as e :
            db .session .rollback ()
            return jsonify ({'error':'Erro ao cadastrar usuário no banco de dados'}),500 


class LoginAPI (MethodView ):
    def post (self ):

        data =request .get_json ()

        if not data or not data .get ('email')or not data .get ('password'):
            return jsonify ({'error':'E-mail e senha são obrigatórios'}),400 

        user =User .query .filter_by (email =data ['email']).first ()

        if not user or not user .check_password (data ['password']):
            return jsonify ({'error':'E-mail ou senha inválidos'}),401 

        access_token =create_access_token (identity =str (user .id ))

        schema =UserSchema ()
        return jsonify ({
        'message':'Login realizado com sucesso',
        'token':access_token ,
        'user':schema .dump (user )
        }),200 
