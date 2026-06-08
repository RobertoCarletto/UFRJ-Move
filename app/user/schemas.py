from app .extensions import ma 
from .models import User 
from marshmallow import validate 

class UserSchema (ma .SQLAlchemySchema ):
    class Meta :
        model =User 
        load_instance =True 
        ordered =True 

    id =ma .Integer (dump_only =True )
    name =ma .String (required =True ,validate =validate .Length (min =2 ,max =100 ))
    email =ma .Email (required =True )
    cpf =ma .String (required =True ,validate =validate .Regexp (r'^\d{11}$|^\d{3}\.\d{3}\.\d{3}-\d{2}$',error ='CPF inválido. Deve conter 11 números ou formato 000.000.000-00.'))
    created_at =ma .DateTime (dump_only =True )
