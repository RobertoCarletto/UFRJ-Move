import os 
from datetime import timedelta 
from dotenv import load_dotenv 


project_root =os .path .abspath (os .path .join (os .path .dirname (__file__ ),'..'))
load_dotenv (os .path .join (project_root ,'.env'))

class Config :

    SECRET_KEY =os .environ .get ('SECRET_KEY')or 'ufrj-move-super-secret-key'


    basedir =os .path .abspath (os .path .dirname (__file__ ))
    SQLALCHEMY_DATABASE_URI =os .environ .get ('DATABASE_URL')or 'sqlite:///'+os .path .join (basedir ,'ufrj_move.db')
    SQLALCHEMY_TRACK_MODIFICATIONS =False 


    JWT_SECRET_KEY =os .environ .get ('JWT_SECRET_KEY')or 'ufrj-move-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES =timedelta (hours =24 )


    GOOGLE_MAPS_API_KEY =os .environ .get ('GOOGLE_MAPS_API_KEY')
