from mongodb import MongoDB
from generate_faker import generate_dict


mongo = MongoDB("localhost:27017", "supermercados")
produtos = generate_dict("produtos", 1000000)
mongo.post(data=produtos, collection="produtos")