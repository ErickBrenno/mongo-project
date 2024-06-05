from mongodb import MongoDB

mongo = MongoDB("localhost:27017", "supermercados")

while True:
    d = mongo.find(collection="produtos", query= {"filial_document": "92.674.851/0001-38"})
    print(d)