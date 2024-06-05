# Projeto: Sistema de Gerenciamento de Estoque para Cadeia de Supermercados

## [Cenário]
Estamos projetando um sistema de gerenciamento de estoque para uma cadeia de supermercados com várias filiais espalhadas por diferentes cidades.
Nossa arquitetura precisa ser capaz de lidar com um grande volume de dados, garantir a consulta e estoque e atualizações no inventário.

Iremos utilizar o Docker, para nos auxiliar na criação do cluster, e utilizaremos um banco de dados documental.
Seguindo a [documentação](https://gustavo-leitao.medium.com/criando-um-cluster-mongodb-com-replicaset-e-sharding-com-docker-9cb19d456b56) criada por Gustavo Leitão, daremos inicio ao nosso projeto.

## [Arquitetura e Justificativa]
1. **Estrutura Geral:**

   Nossa arquitetura MongoDB é composta por:
   - 1 roteador (mongos)
   - 3 shards, cada shard com duas instâncias (replica sets)
   - 3 servidores de configurações
  
      ![Flowcharts (1)](https://github.com/ErickBrenno/mongo-project/assets/83048005/348b5839-c2ab-40f6-a29e-80543d903111)

2. **Componentes e Distribuição:**
   - **Roteador (mongos):** O roteador é responsável por receber as solicitações de clientes e distribuir as operações aos shards apropriados. Ter um único roteador simplifica a configuração inicial e a manutenção do sistema. Ele também atua como um ponto de entrada centralizado, facilitando a gestão de conexões.

   - **Shards:**
   Optamos por 3 shards, cada um composto por dois membros em um replica set. Cada shard é um subconjunto do banco de dados, e a fragmentação dos dados entre eles permite:
      - **Distribuição de Carga:** Os dados são distribuídos entre os shards, evitando sobrecarga de um único servidor e melhorando a capacidade de processamento paralelo.
      - **Alta Disponibilidade:** Os replica sets garantem a replicação de dados. Se um membro de um shard falhar, outro membro pode assumir, assegurando que o serviço continue sem interrupção.
      - **Escalabilidade Horizontal:** A adição de shards adicionais é uma operação relativamente simples, permitindo a expansão conforme o volume de dados e o tráfego aumentam.
        
   - **Servidores de Configurações:** Os 3 servidores de configurações mantêm informações de metadados e a topologia do cluster. A configuração em replica set assegura a consistência e disponibilidade dessas informações essenciais, mesmo em caso de falhas de servidor.

3. **Fragmentação (Sharding):**
   A fragmentação foi configurada utilizando um índice hashed para ambas as coleções, “Produtos” e “Filiais”. Essa escolha é justificada pelos seguintes motivos:
   - ***Distribuição Uniforme:*** Um índice hashed gera uma distribuição quase uniforme dos documentos entre os shards, o que é crucial para evitar pontos de acesso e assegurar que nenhum shard se torne um gargalo de desempenho.
   - ***Escalabilidade:*** À medida que novas filiais e produtos são adicionados, a carga é distribuída de maneira equilibrada, permitindo que o sistema mantenha um desempenho consistente sem a necessidade de reconfigurações frequentes.
   - ***Simplicidade na Consulta:*** A fragmentação com base em índices hashed facilita a localização de documentos, pois as consultas podem ser distribuídas eficientemente pelo roteador.

## [Configuração do ambiente MongoDB]

### Criando Rede para a Comunicação entre os containers.
Essa rede será responsável pela comunicação dos containers de toda arquitetura.
```shell
docker network create mongo-shard
```


### Criando Containers ConfigServers.
Esses containers serão o responsaveis por armazenar os metadados do cluster sharded, como mapeamento de chunks para shards e configuração de balanceamento de carga.
```shell
docker run --name mongo-config01 --net mongo-shard -d mongo mongod --configsvr --replSet configserver --port 27017
docker run --name mongo-config02 --net mongo-shard -d mongo mongod --configsvr --replSet configserver --port 27017
docker run --name mongo-config03 --net mongo-shard -d mongo mongod --configsvr --replSet configserver --port 27017
```
![imagem](https://github.com/JonathanWillian5/MongoDB/assets/89879087/83adfee0-8629-429f-9378-103c2e3e3306)


### Configurando Replica Set ConfigServers
Nesta etapa, vamos configurar os servidores de configuração para o nosso cluster de sharding do MongoDB. 
Esses servidores são essenciais, pois armazenam metadados sobre a estrutura do cluster, incluindo a distribuição dos dados entre os shards e o estado atual do cluster.
```shell
docker exec -it mongo-config01 mongo
```
```shell
rs.initiate(
   {
      _id: "configserver",
      configsvr: true,
      version: 1,
      members: [
         { _id: 0, host : "mongo-config01:27017" },
         { _id: 1, host : "mongo-config02:27017" },
         { _id: 2, host : "mongo-config03:27017" }
      ]
   }
)
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/507f7f20-00b3-4966-b82d-152833ea8618)

### Criando Containers Shards.
Para esta etapa, vamos configurar três containers que atuaram como shards, cada shards composto por dois nós para formar um conjunto de réplicas. 
Os shards são responsáveis pelo armazenamento distribuído dos dados, ajudando a escalar horizontalmente o banco de dados.
- Shard01
```shell
docker run --name mongo-shard1a --net mongo-shard -d mongo mongod --port 27018 --shardsvr --replSet shard01
docker run --name mongo-shard1b --net mongo-shard -d mongo mongod --port 27018 --shardsvr --replSet shard01
```
- Shard02
```shell
docker run --name mongo-shard2a --net mongo-shard -d mongo mongod --port 27019 --shardsvr --replSet shard02
docker run --name mongo-shard2b --net mongo-shard -d mongo mongod --port 27019 --shardsvr --replSet shard02
```
- Shard03
```shell
docker run --name mongo-shard3a --net mongo-shard -d mongo mongod --port 27020 --shardsvr --replSet shard03
docker run --name mongo-shard3b --net mongo-shard -d mongo mongod --port 27020 --shardsvr --replSet shard03
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/d9903013-1bea-4633-8c35-0563b934f47e)


### Configurando Réplicas Sets Shards.
Essas configurações serão responsáveis por inicializar conjuntos de réplicas para cada shard no cluster de sharding.
- Shard01
```shell
docker exec -it mongo-shard1a mongo --port 27018
```
```shell
rs.initiate(
   {
      _id: "shard01",
      version: 1,
      members: [
         { _id: 0, host : "mongo-shard1a:27018" },
         { _id: 1, host : "mongo-shard1b:27018" },
      ]
   }
)
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/3a586f70-3f46-4f9b-83ac-fa2d8961fecc)
- Shard02
```shell
docker exec -it mongo-shard2a mongo --port 27019
```
```shell
rs.initiate(
   {
      _id: "shard02",
      version: 1,
      members: [
         { _id: 0, host : "mongo-shard2a:27019" },
         { _id: 1, host : "mongo-shard2b:27019" },
      ]
   }
)
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/f793d367-cdb0-4f9d-ba06-07b25bc97c29)
- Shard03
```shell
docker exec -it mongo-shard3a mongo --port 27020
```
```shell
rs.initiate(
   {
      _id: "shard03",
      version: 1,
      members: [
         { _id: 0, host : "mongo-shard3a:27020" },
         { _id: 1, host : "mongo-shard3b:27020" },
      ]
   }
)
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/36aa44f2-d527-421c-bc19-becce3ff14be)


### Configurando Roteador
Nessa etapa iremos criar um container que executa um roteador (mongos) que é o rotedor de sharding do MongoDB.
```shell
docker run -p 27017:27017 --name mongo-router --net mongo-shard -d mongo mongos --port 27017 --configdb 
configserver/mongo-config01:27017,mongo-config02:27017,mongo-config03:27017 --bind_ip_all
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/88088e04-4199-4512-a319-db68a6516eeb)


### Configurando Cluster Sharding
Nesta etapa, vamos configurar um cluster de sharding no MongoDB, composto por três shards. 
Cada shard é formado por um conjunto de réplicas para garantir redundância e alta disponibilidade.
```shell
docker exec -it mongo-router mongo
sh.addShard("shard01/mongo-shard1a:27018")
sh.addShard("shard01/mongo-shard1b:27018") 
sh.addShard("shard02/mongo-shard2a:27019")
sh.addShard("shard02/mongo-shard2b:27019")    
sh.addShard("shard03/mongo-shard3a:27020")
sh.addShard("shard03/mongo-shard3b:27020")
```
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/80d4fda7-2749-43b2-a16a-c14e726d36d5)

### Criação do banco e distribuição entre os shards
Nessa etapa estamos criando o banco de dados que se chama supermercado, criando um collection para os produtos e uma collection para filiais, o mesmo comando de criação das collections gera um indice para ambas.<br />
 - Para colletion produtos criamos um index do tipo hashed na chave ID.<br />
 - Para a collection filiais criamos um index do tipo hashed na chave document.<br />

```shell
use supermercados
db.produtos.createIndex({"id": "hashed"})
db.filiais.createIndex({"document": "hashed"})
```

![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/7a8ce613-00c5-4afc-8dea-86cc435aeece)

> Criamos as fragmentações nas duas collection (produto, filiais)
  - Para colletion produtos criamos um shard do tipo hashed na chave ID.<br />
  - Para a collection filiais criamos um shard do tipo hashed na chave document.<br />

> **Note:** O tipo hashed na fragmentação fica responsável pela distribuição uniforme dos dados entre os shards.<br/>
> **Note:** É preciso criar um index na chave a ser fragmentada para conseguir fazer a criação do shard.

```shell
sh.shardCollection("supermercados.produtos", {"id": "hashed"})
sh.shardCollection("supermercados.filiais", {"document": "hashed"})
```
   
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/c2d03537-db2e-4de1-8faf-590e4ab6a0f7)


# Simulação
## Implementação da estratégia de particionamento
> Com isso é possível garantir uma distribuição balanceada e reduzir a sobrecarga do banco de dados e proporcionar um maior isolamento e segurança dos dados.
Para nossa estratégica adotamos o método de particionamento horizontal e por fragmentação.
 - Vantagens particionamento horizontal e fragmentado:
   
   1 - Escalabilidade: Permite que o banco de dados cresça horizontalmente, adicionando mais servidores para acomodar o aumento de dados e carga de trabalho.
   
   2 - Desempenho: Melhora o desempenho ao reduzir a quantidade de dados que cada consulta precisa processar. Isso é especialmente útil em grandes bancos de dados.
   
   3 - Gerenciamento de Dados: Facilita o gerenciamento e manutenção dos dados, como backup e recuperação, pois cada partição pode ser tratada separadamente.

![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/e22cc013-7f83-46f0-ada1-5452f430b96d)

Na imagem acima é possível ver a distribuição realizada entre os shards na colletions produtos utilizando a estratégia de fragmentação se baseando no hashed da chave ID.

# Teste de funcionamento e desempenho do ambiente

> **Desempenho:**<br/>
Para nosso teste de estresse utilizamos um código python, para realizar multiplas consultas, inserções e updates dentro do ambiente.

![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/19b8b421-c30c-4831-bcf5-352d8f6c592f)


>Na imagem abaixo, podemos visualizar como o ambiente se comportou durante as operações realizadas acima.

MONGO:<br/>
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/40f93e75-fc1c-4178-ab8a-ea24818ff387)<br/>
CONTAINERS:<br/>
![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/70a09ea9-4c52-4add-bf96-090d32097338)

**Consulta:**<br/>
Consulta buscando as informações sobre o estoque de algumas filiais.<br/>

![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/53075aac-1dec-40d9-ad09-e2f8719b5482)

**Atualizações:**<br/>
Atualização realizando a alteração da quantidade do inventário de ulgumas filiais.<br/>

![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/e7b00e11-2822-490f-b6ab-774f3554b362)

**Inserções:**<br/>
Nesse exemplo, estamos realizando a inserção de algumas Filiais na Collection "filiais".<br/>

![image](https://github.com/ErickBrenno/mongo-project/assets/83048005/28f5bae2-7b32-4213-b997-83d7bd2a3767)




