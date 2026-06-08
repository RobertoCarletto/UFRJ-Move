from app .extensions import ma 
from .models import BusLocation ,Route ,BusStop ,RouteStop 
from marshmallow import fields 

class BusStopSchema (ma .SQLAlchemySchema ):
    class Meta :
        model =BusStop 
        load_instance =True 
        ordered =True 

    id =ma .Integer (dump_only =True )
    name =ma .String (required =True )
    latitude =ma .Float (required =True )
    longitude =ma .Float (required =True )


class RouteStopSchema (ma .SQLAlchemySchema ):
    class Meta :
        model =RouteStop 
        load_instance =True 
        ordered =True 

    id =ma .Integer (dump_only =True )
    route_id =ma .Integer (dump_only =True )
    bus_stop_id =ma .Integer (required =True )
    sequence_order =ma .Integer (required =True )
    bus_stop =fields .Nested (BusStopSchema ,dump_only =True )


class RouteSchema (ma .SQLAlchemySchema ):
    class Meta :
        model =Route 
        load_instance =True 
        ordered =True 

    id =ma .Integer (dump_only =True )
    name =ma .String (required =True )
    description =ma .String ()
    active =ma .Boolean ()
    stops =fields .Nested (RouteStopSchema ,many =True ,dump_only =True )


class BusLocationSchema (ma .SQLAlchemySchema ):
    class Meta :
        model =BusLocation 
        load_instance =True 
        ordered =True 

    id =ma .Integer (dump_only =True )
    user_id =ma .Integer (required =True )
    user_name =fields .Method ("get_user_name",dump_only =True )
    route_id =ma .Integer (required =True )
    route_name =fields .Method ("get_route_name",dump_only =True )
    latitude =ma .Float (required =True )
    longitude =ma .Float (required =True )
    updated_at =ma .DateTime (dump_only =True )
    active =ma .Boolean ()

    def get_user_name (self ,obj ):
        return obj .user .name if obj .user else "Desconhecido"

    def get_route_name (self ,obj ):
        return obj .route .name if obj .route else "Desconhecida"
