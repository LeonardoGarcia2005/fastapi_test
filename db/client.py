from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Conexión al localhost (MongoDB corriendo en tu máquina) base de datos local
#db_client = MongoClient().local

uri = "mongodb+srv://leonardojgarciaparada2005:Leonardog2005@cluster0.chmci.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Crear un nuevo cliente para la conexion de base de datos
db_client = MongoClient(uri, server_api=ServerApi('1')).PDFCONNECT

# Enviar un ping de respuesta para confimar si se conencto correstamente la base de datos
try:
    db_client.admin.command('ping')
    print("¡Se ha realizado un ping a tu implementación! ¡Te has conectado exitosamente a MongoDB!")
except Exception as e:
    print(e)