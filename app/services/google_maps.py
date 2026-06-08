import math 
import json 
import urllib .request 
import urllib .error 
from flask import current_app 

def haversine_distance (lat1 ,lon1 ,lat2 ,lon2 ):

    R =6371000 
    phi1 =math .radians (lat1 )
    phi2 =math .radians (lat2 )
    delta_phi =math .radians (lat2 -lat1 )
    delta_lambda =math .radians (lon2 -lon1 )

    a =math .sin (delta_phi /2 )**2 +math .cos (phi1 )*math .cos (phi2 )*math .sin (delta_lambda /2 )**2 
    c =2 *math .atan2 (math .sqrt (a ),math .sqrt (1 -a ))

    return R *c 

class GoogleMapsService :
    def __init__ (self ):

        self .api_key =current_app .config .get ('GOOGLE_MAPS_API_KEY')

    def snap_to_road (self ,lat ,lon ):

        if not self .api_key :
            return lat ,lon 

        url =f"https://roads.googleapis.com/v1/snapToRoads?path={lat },{lon }&interpolate=true&key={self .api_key }"
        try :
            req =urllib .request .Request (url ,headers ={'User-Agent':'UFRJ-Move-Backend'})
            with urllib .request .urlopen (req ,timeout =3 )as response :
                data =json .loads (response .read ().decode ())
                snapped_points =data .get ("snappedPoints",[])
                if snapped_points :
                    location =snapped_points [0 ].get ("location",{})
                    new_lat =location .get ("latitude",lat )
                    new_lng =location .get ("longitude",lon )
                    return new_lat ,new_lng 
        except Exception as e :

            current_app .logger .warning (f"Google Roads API Snap failed: {e }. Using original coords.")

        return lat ,lon 

    def get_distance_and_eta (self ,lat1 ,lon1 ,lat2 ,lon2 ):


        local_dist =haversine_distance (lat1 ,lon1 ,lat2 ,lon2 )

        local_duration =local_dist /5.56 

        if not self .api_key :
            return local_dist ,local_duration 

        url =f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={lat1 },{lon1 }&destinations={lat2 },{lon2 }&mode=driving&key={self .api_key }"
        try :
            req =urllib .request .Request (url ,headers ={'User-Agent':'UFRJ-Move-Backend'})
            with urllib .request .urlopen (req ,timeout =3 )as response :
                data =json .loads (response .read ().decode ())
                if data .get ("status")=="OK":
                    rows =data .get ("rows",[])
                    if rows and rows [0 ].get ("elements"):
                        element =rows [0 ]["elements"][0 ]
                        if element .get ("status")=="OK":
                            dist_meters =element ["distance"]["value"]
                            duration_seconds =element ["duration"]["value"]
                            return dist_meters ,duration_seconds 
        except Exception as e :
            current_app .logger .warning (f"Google Distance Matrix failed: {e }. Using local Haversine fallback.")

        return local_dist ,local_duration 
