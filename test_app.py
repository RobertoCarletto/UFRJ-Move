import unittest 
import json 
from datetime import datetime ,timezone 
from app import create_app 
from app .extensions import db 
from app .user .models import User 
from app .bus .models import Route ,BusStop ,RouteStop ,BusLocation 

class UFRJMoveTestCase (unittest .TestCase ):
    def setUp (self ):

        self .app =create_app ()
        self .app .config ['TESTING']=True 

        self .app .config ['SQLALCHEMY_DATABASE_URI']='sqlite:///:memory:'

        self .client =self .app .test_client ()
        self .app_context =self .app .app_context ()
        self .app_context .push ()


        db .create_all ()


        from app .seed import seed_database 
        seed_database ()

    def tearDown (self ):
        db .session .remove ()
        db .drop_all ()
        self .app_context .pop ()

    def test_database_seeding (self ):

        routes =Route .query .all ()
        self .assertEqual (len (routes ),4 )

        route_names =[r .name for r in routes ]
        self .assertIn ("Circular Interno 1",route_names )
        self .assertIn ("Circular Interno 2",route_names )

        stops =BusStop .query .all ()
        self .assertGreater (len (stops ),0 )

        ct_stop =BusStop .query .filter_by (name ="Centro de Tecnologia (CT)").first ()
        self .assertIsNotNone (ct_stop )
        self .assertEqual (ct_stop .latitude ,-22.8239 )

    def test_user_registration_and_validation (self ):


        response =self .client .post ('/api/auth/register',json ={
        'name':'João Silva',
        'email':'joao@ufrj.br',
        'cpf':'123.456.789-09',
        'password':'senha_segura'
        })
        self .assertEqual (response .status_code ,201 )
        data =json .loads (response .data )
        self .assertIn ('user',data )

        self .assertEqual (data ['user']['cpf'],'12345678909')


        response =self .client .post ('/api/auth/register',json ={
        'name':'Outro Nome',
        'email':'joao@ufrj.br',
        'cpf':'987.654.321-00',
        'password':'senha_segura'
        })
        self .assertEqual (response .status_code ,409 )


        response =self .client .post ('/api/auth/register',json ={
        'name':'Mais Um',
        'email':'outro@ufrj.br',
        'cpf':'12345678909',
        'password':'senha_segura'
        })
        self .assertEqual (response .status_code ,409 )


        response =self .client .post ('/api/auth/register',json ={
        'name':'Cpf Errado',
        'email':'errado@ufrj.br',
        'cpf':'123-456',
        'password':'senha_segura'
        })
        self .assertEqual (response .status_code ,400 )

    def test_user_login (self ):


        user =User (name ='Maria Souza',email ='maria@ufrj.br',cpf ='11122233344')
        user .set_password ('minha_senha')
        db .session .add (user )
        db .session .commit ()


        response =self .client .post ('/api/auth/login',json ={
        'email':'maria@ufrj.br',
        'password':'minha_senha'
        })
        self .assertEqual (response .status_code ,200 )
        data =json .loads (response .data )
        self .assertIn ('token',data )


        response =self .client .post ('/api/auth/login',json ={
        'email':'maria@ufrj.br',
        'password':'senha_errada'
        })
        self .assertEqual (response .status_code ,401 )

    def test_bus_location_transmission_and_clustering (self ):


        self .client .post ('/api/auth/register',json ={
        'name':'User One',
        'email':'user1@ufrj.br',
        'cpf':'11111111111',
        'password':'password123'
        })
        login_res1 =self .client .post ('/api/auth/login',json ={
        'email':'user1@ufrj.br',
        'password':'password123'
        })
        token1 =json .loads (login_res1 .data )['token']


        self .client .post ('/api/auth/register',json ={
        'name':'User Two',
        'email':'user2@ufrj.br',
        'cpf':'22222222222',
        'password':'password123'
        })
        login_res2 =self .client .post ('/api/auth/login',json ={
        'email':'user2@ufrj.br',
        'password':'password123'
        })
        token2 =json .loads (login_res2 .data )['token']


        headers1 ={'Authorization':f'Bearer {token1 }'}
        route1 =Route .query .filter_by (name ="Circular Interno 1").first ()

        tx_res1 =self .client .post ('/api/bus/location',json ={
        'route_id':route1 .id ,
        'latitude':-22.8240 ,
        'longitude':-43.2300 
        },headers =headers1 )
        self .assertEqual (tx_res1 .status_code ,200 )


        locs_res =self .client .get ('/api/bus/locations')
        self .assertEqual (locs_res .status_code ,200 )
        data =json .loads (locs_res .data )
        self .assertEqual (data ['count'],1 )
        self .assertEqual (data ['buses'][0 ]['validation_count'],1 )
        self .assertEqual (data ['buses'][0 ]['status'],'pending')


        headers2 ={'Authorization':f'Bearer {token2 }'}
        tx_res2 =self .client .post ('/api/bus/location',json ={
        'route_id':route1 .id ,
        'latitude':-22.8241 ,
        'longitude':-43.2301 
        },headers =headers2 )
        self .assertEqual (tx_res2 .status_code ,200 )


        locs_res2 =self .client .get ('/api/bus/locations')
        data2 =json .loads (locs_res2 .data )
        self .assertEqual (data2 ['count'],1 )
        self .assertEqual (data2 ['buses'][0 ]['validation_count'],2 )
        self .assertEqual (data2 ['buses'][0 ]['status'],'validated')


        self .assertGreater (len (data2 ['buses'][0 ]['stops_eta']),0 )
        self .assertIsNotNone (data2 ['buses'][0 ]['next_stop'])


        stop_res1 =self .client .delete ('/api/bus/location',headers =headers1 )
        self .assertEqual (stop_res1 .status_code ,200 )


        locs_res3 =self .client .get ('/api/bus/locations')
        data3 =json .loads (locs_res3 .data )
        self .assertEqual (data3 ['count'],1 )
        self .assertEqual (data3 ['buses'][0 ]['validation_count'],1 )
        self .assertEqual (data3 ['buses'][0 ]['status'],'pending')

if __name__ =='__main__':
    unittest .main ()
