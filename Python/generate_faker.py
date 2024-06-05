import uuid, random, time
from faker import Faker
from datetime import datetime
from supermercados import supermercados


fake = Faker('pt_BR')
documents = [fake.cnpj() for i in range(0, len(supermercados))]

def generate_dict(template: str, quantidade = None):
    output = []
    index = 0

    match template:
        case "filiais":
            for i in supermercados:                                   
                x = {
                    "nome": i,
                    "dt_create": fake.date(),
                    "localizacao": {
                        "endereco": fake.street_address(),
                        "cidade": fake.city(),
                        "estado": fake.country_code(),
                        "cep": fake.postcode()
                    },
                    "document": documents[index]
                }
                output.append(x)
                index += 1                
            return output
        
        case "produtos":
            for i in range(0, quantidade):
                x = {
                "id": str(uuid.uuid4()),
                "filial_document": random.choice(documents),
                "dt_create": fake.date(),
                "nome": fake.word().capitalize(),
                "preco": round(random.uniform(1, 100), 2),
                "quantidade": random.randint(1, 500)
                }
                output.append(x)
            return output