from flask import Blueprint 
from .controllers import RegisterAPI ,LoginAPI 

auth_api =Blueprint ('auth_api',__name__ )

auth_api .add_url_rule ('/register',view_func =RegisterAPI .as_view ('register'),methods =['POST'])
auth_api .add_url_rule ('/login',view_func =LoginAPI .as_view ('login'),methods =['POST'])
