from mongodb import MongoDB

mongo = MongoDB("localhost:27017", "supermercados")
while True:
    target = {"id": "d28a7a10-75f9-46e5-aac7-e951535f7a8f"}
    value = {"$set": {"nome": "Robertinho vendedor"}}
    
    mongo.update(collection="produtos", target=target, value=value)