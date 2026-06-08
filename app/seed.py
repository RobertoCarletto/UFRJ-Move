from app .extensions import db 
from app .bus .models import Route ,BusStop ,RouteStop 

def seed_database ():


    if Route .query .first ()is not None :
        return 

    print ("Seeding database with UFRJ circular routes and stops...")


    stops_data =[
    {"name":"Centro de Tecnologia (CT)","latitude":-22.8239 ,"longitude":-43.2302 },
    {"name":"Centro de Ciências da Saúde (CCS)","latitude":-22.8262 ,"longitude":-43.2354 },
    {"name":"Educação Física (EEFD)","latitude":-22.8193 ,"longitude":-43.2348 },
    {"name":"Alojamento Estudantil","latitude":-22.8168 ,"longitude":-43.2384 },
    {"name":"Faculdade de Letras","latitude":-22.8227 ,"longitude":-43.2319 },
    {"name":"Reitoria","latitude":-22.8207 ,"longitude":-43.2272 },
    {"name":"Parque Tecnológico","latitude":-22.8139 ,"longitude":-43.2307 },
    {"name":"Prédio da Coppe (Bloco I/J)","latitude":-22.8251 ,"longitude":-43.2325 },
    ]

    stops_map ={}
    for stop_info in stops_data :
        stop =BusStop (
        name =stop_info ["name"],
        latitude =stop_info ["latitude"],
        longitude =stop_info ["longitude"]
        )
        db .session .add (stop )
        stops_map [stop_info ["name"]]=stop 


    db .session .flush ()


    routes_data =[
    {
    "name":"Circular Interno 1",
    "description":"Via Alojamento Estudantil. CT -> CCS -> EEFD -> Alojamento -> CT",
    "stops":[
    "Centro de Tecnologia (CT)",
    "Prédio da Coppe (Bloco I/J)",
    "Centro de Ciências da Saúde (CCS)",
    "Educação Física (EEFD)",
    "Alojamento Estudantil",
    "Centro de Tecnologia (CT)"
    ]
    },
    {
    "name":"Circular Interno 2",
    "description":"Via Reitoria. CT -> CCS -> EEFD -> Reitoria -> CT",
    "stops":[
    "Centro de Tecnologia (CT)",
    "Prédio da Coppe (Bloco I/J)",
    "Centro de Ciências da Saúde (CCS)",
    "Educação Física (EEFD)",
    "Reitoria",
    "Centro de Tecnologia (CT)"
    ]
    },
    {
    "name":"Circular Interno 3",
    "description":"Via Faculdade de Letras. CT -> Letras -> Reitoria -> CCS -> CT",
    "stops":[
    "Centro de Tecnologia (CT)",
    "Faculdade de Letras",
    "Reitoria",
    "Centro de Ciências da Saúde (CCS)",
    "Centro de Tecnologia (CT)"
    ]
    },
    {
    "name":"Circular Interno 4",
    "description":"Via Parque Tecnológico. CT -> CCS -> Parque Tecnológico -> CT",
    "stops":[
    "Centro de Tecnologia (CT)",
    "Centro de Ciências da Saúde (CCS)",
    "Parque Tecnológico",
    "Centro de Tecnologia (CT)"
    ]
    }
    ]

    for route_info in routes_data :
        route =Route (
        name =route_info ["name"],
        description =route_info ["description"],
        active =True 
        )
        db .session .add (route )
        db .session .flush ()


        for index ,stop_name in enumerate (route_info ["stops"]):
            bus_stop =stops_map [stop_name ]
            route_stop =RouteStop (
            route_id =route .id ,
            bus_stop_id =bus_stop .id ,
            sequence_order =index +1 
            )
            db .session .add (route_stop )

    try :
        db .session .commit ()
        print ("Database seeded successfully with routes and stops.")
    except Exception as e :
        db .session .rollback ()
        print (f"Error seeding database: {e }")
