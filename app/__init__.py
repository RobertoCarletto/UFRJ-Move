from flask import Flask ,jsonify 
from .config import Config 
from .extensions import db ,jwt ,ma ,cors 

from .auth .routes import auth_api 
from .user .routes import user_api 
from .bus .routes import bus_api 

def create_app ():
    app =Flask (__name__ )
    app .config .from_object (Config )


    db .init_app (app )
    jwt .init_app (app )
    ma .init_app (app )
    cors .init_app (app )


    @jwt .expired_token_loader 
    def expired_token_callback (jwt_header ,jwt_payload ):
        return jsonify ({'error':'Token expirado','message':'Faça login novamente'}),401 

    @jwt .invalid_token_loader 
    def invalid_token_callback (error ):
        return jsonify ({'error':'Token inválido','message':'O token fornecido é inválido'}),401 

    @jwt .unauthorized_loader 
    def missing_token_callback (error ):
        return jsonify ({'error':'Acesso negado','message':'Token JWT não fornecido no cabeçalho Authorization'}),401 


    app .register_blueprint (auth_api ,url_prefix ='/api/auth')
    app .register_blueprint (user_api ,url_prefix ='/api/user')
    app .register_blueprint (bus_api ,url_prefix ='/api/bus')


    @app .route ('/',methods =['GET'])
    def index ():
        return jsonify ({'message':'Bem-vindo à API do UFRJ Move!','status':'Online'}),200 


    with app .app_context ():
        db .create_all ()
        from .seed import seed_database 
        seed_database ()

    return app 
