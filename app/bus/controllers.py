from flask .views import MethodView 
from flask import request ,jsonify 
from flask_jwt_extended import jwt_required ,get_jwt_identity 
from app .extensions import db 
from .models import BusLocation ,Route ,BusStop ,RouteStop 
from .schemas import BusLocationSchema ,RouteSchema 
from app .services .google_maps import GoogleMapsService ,haversine_distance 
from datetime import datetime ,timezone ,timedelta 

class BusLocationAPI (MethodView ):

    @jwt_required ()
    def post (self ):

        data =request .get_json ()
        current_user_id =get_jwt_identity ()

        if not data or 'latitude'not in data or 'longitude'not in data or not data .get ('route_id'):
            return jsonify ({'error':'Latitude, longitude e route_id são obrigatórios'}),400 

        route_id =data ['route_id']
        route =db .session .get (Route ,route_id )
        if not route :
            return jsonify ({'error':'Rota informada não encontrada'}),404 


        gmaps =GoogleMapsService ()
        lat ,lon =gmaps .snap_to_road (data ['latitude'],data ['longitude'])

        location =BusLocation .query .filter_by (user_id =current_user_id ,active =True ).first ()

        if location :
            location .latitude =lat 
            location .longitude =lon 
            location .route_id =route_id 
            location .updated_at =datetime .now (timezone .utc )
        else :
            location =BusLocation (
            user_id =current_user_id ,
            route_id =route_id ,
            latitude =lat ,
            longitude =lon ,
            active =True 
            )
            db .session .add (location )

        try :
            db .session .commit ()
            schema =BusLocationSchema ()
            return jsonify ({'message':'Localização atualizada','data':schema .dump (location )}),200 
        except Exception as e :
            db .session .rollback ()
            return jsonify ({'error':'Erro ao salvar localização'}),500 

    @jwt_required ()
    def delete (self ):

        current_user_id =get_jwt_identity ()
        location =BusLocation .query .filter_by (user_id =current_user_id ,active =True ).first ()

        if location :
            location .active =False 
            try :
                db .session .commit ()
                return jsonify ({'message':'Transmissão interrompida com sucesso'}),200 
            except Exception as e :
                db .session .rollback ()
                return jsonify ({'error':'Erro ao parar transmissão'}),500 

        return jsonify ({'message':'Nenhuma transmissão ativa encontrada'}),200 


class ActiveLocationsAPI (MethodView ):

    def get (self ):


        time_limit =datetime .now (timezone .utc )-timedelta (seconds =30 )

        active_transmissions =BusLocation .query .filter (
        BusLocation .active ==True ,
        BusLocation .updated_at >=time_limit 
        ).all ()


        transmissions_by_route ={}
        for loc in active_transmissions :
            if loc .route_id not in transmissions_by_route :
                transmissions_by_route [loc .route_id ]=[]
            transmissions_by_route [loc .route_id ].append (loc )

        buses =[]
        gmaps =GoogleMapsService ()

        for route_id ,locs in transmissions_by_route .items ():
            route =db .session .get (Route ,route_id )
            if not route :
                continue 



            clusters =[]
            for loc in locs :
                placed =False 
                for cluster in clusters :

                    center_lat =sum (c .latitude for c in cluster )/len (cluster )
                    center_lng =sum (c .longitude for c in cluster )/len (cluster )

                    if haversine_distance (loc .latitude ,loc .longitude ,center_lat ,center_lng )<=50 :
                        cluster .append (loc )
                        placed =True 
                        break 
                if not placed :
                    clusters .append ([loc ])


            for cluster in clusters :
                avg_lat =sum (c .latitude for c in cluster )/len (cluster )
                avg_lng =sum (c .longitude for c in cluster )/len (cluster )
                validation_count =len (cluster )
                latest_update =max (c .updated_at for c in cluster )


                stops_eta =[]
                for rs in route .stops :
                    stop =rs .bus_stop 
                    dist_meters ,duration_seconds =gmaps .get_distance_and_eta (avg_lat ,avg_lng ,stop .latitude ,stop .longitude )
                    stops_eta .append ({
                    "stop_id":stop .id ,
                    "name":stop .name ,
                    "sequence_order":rs .sequence_order ,
                    "distance_meters":round (dist_meters ),
                    "eta_minutes":round (duration_seconds /60 ,1 )
                    })


                stops_eta .sort (key =lambda x :x ["sequence_order"])



                next_stop =None 
                closest_stop_in_range =min (stops_eta ,key =lambda x :x ["distance_meters"])if stops_eta else None 

                if closest_stop_in_range :
                    if closest_stop_in_range ["distance_meters"]<=30 :
                        closest_stop_in_range ["eta_minutes"]=0.0 
                        next_stop =closest_stop_in_range 
                    else :

                        next_stop =closest_stop_in_range 

                buses .append ({
                "route_id":route .id ,
                "route_name":route .name ,
                "latitude":avg_lat ,
                "longitude":avg_lng ,
                "validation_count":validation_count ,
                "status":"validated"if validation_count >=2 else "pending",
                "updated_at":latest_update .isoformat (),
                "next_stop":next_stop ,
                "stops_eta":stops_eta 
                })


        schema =BusLocationSchema (many =True )
        return jsonify ({
        'count':len (buses ),
        'buses':buses ,
        'raw_locations':schema .dump (active_transmissions )
        }),200 


class ListRoutesAPI (MethodView ):

    def get (self ):

        routes =Route .query .filter_by (active =True ).all ()
        schema =RouteSchema (many =True )
        return jsonify (schema .dump (routes )),200 
