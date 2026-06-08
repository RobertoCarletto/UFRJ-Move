from app .extensions import db 
from datetime import datetime ,timezone 

class Route (db .Model ):
    __tablename__ ='routes'

    id =db .Column (db .Integer ,primary_key =True )
    name =db .Column (db .String (100 ),nullable =False ,unique =True )
    description =db .Column (db .String (255 ),nullable =True )
    active =db .Column (db .Boolean ,default =True )
    created_at =db .Column (db .DateTime ,default =lambda :datetime .now (timezone .utc ))


    stops =db .relationship ('RouteStop',back_populates ='route',order_by ='RouteStop.sequence_order',cascade ='all, delete-orphan')
    bus_locations =db .relationship ('BusLocation',back_populates ='route',lazy ='dynamic')


class BusStop (db .Model ):
    __tablename__ ='bus_stops'

    id =db .Column (db .Integer ,primary_key =True )
    name =db .Column (db .String (100 ),nullable =False ,unique =True )
    latitude =db .Column (db .Float ,nullable =False )
    longitude =db .Column (db .Float ,nullable =False )
    created_at =db .Column (db .DateTime ,default =lambda :datetime .now (timezone .utc ))

    routes =db .relationship ('RouteStop',back_populates ='bus_stop',cascade ='all, delete-orphan')


class RouteStop (db .Model ):
    __tablename__ ='route_stops'

    id =db .Column (db .Integer ,primary_key =True )
    route_id =db .Column (db .Integer ,db .ForeignKey ('routes.id'),nullable =False )
    bus_stop_id =db .Column (db .Integer ,db .ForeignKey ('bus_stops.id'),nullable =False )
    sequence_order =db .Column (db .Integer ,nullable =False )

    route =db .relationship ('Route',back_populates ='stops')
    bus_stop =db .relationship ('BusStop',back_populates ='routes')


class BusLocation (db .Model ):
    __tablename__ ='bus_locations'

    id =db .Column (db .Integer ,primary_key =True )
    user_id =db .Column (db .Integer ,db .ForeignKey ('users.id'),nullable =False )
    route_id =db .Column (db .Integer ,db .ForeignKey ('routes.id'),nullable =False )
    latitude =db .Column (db .Float ,nullable =False )
    longitude =db .Column (db .Float ,nullable =False )
    updated_at =db .Column (db .DateTime ,default =lambda :datetime .now (timezone .utc ),onupdate =lambda :datetime .now (timezone .utc ))
    active =db .Column (db .Boolean ,default =True )

    user =db .relationship ('User',backref =db .backref ('bus_locations',lazy =True ))
    route =db .relationship ('Route',back_populates ='bus_locations')
