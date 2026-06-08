from flask import Blueprint 
from .controllers import BusLocationAPI ,ActiveLocationsAPI ,ListRoutesAPI 

bus_api =Blueprint ('bus_api',__name__ )

bus_api .add_url_rule ('/location',view_func =BusLocationAPI .as_view ('bus_location'),methods =['POST','DELETE'])
bus_api .add_url_rule ('/locations',view_func =ActiveLocationsAPI .as_view ('active_locations'),methods =['GET'])
bus_api .add_url_rule ('/routes',view_func =ListRoutesAPI .as_view ('list_routes'),methods =['GET'])
