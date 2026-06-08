from flask import Blueprint 
from .controllers import ProfileAPI 

user_api =Blueprint ('user_api',__name__ )

user_api .add_url_rule ('/profile',view_func =ProfileAPI .as_view ('profile'),methods =['GET'])
