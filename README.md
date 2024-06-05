# Projeto: Sistema de Gerenciamento de Estoque para Cadeia de Supermercados

## [Cenário]
Estamos projetando um sistema de gerenciamento de estoque para uma cadeia de supermercados com várias filiais espalhadas por diferentes cidades. O objetivo é garantir a eficiência na gestão de estoque, rastreamento de produtos, reposição automática e análise de dados para tomada de decisões estratégicas.

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

# Configuração do ambiente em MongoDB

## Criar Rede para a Comunicação entre os containers.
> Essa rede será responsável pela comunicação dos containers de toda arquitetura.
```shell
docker network create mongo-shard
```


## Criar Containers ConfigServers.
> Esses containers serão o responsaveis por armazenar os metadados do cluster sharded, como mapeamento de chunks para shards e configuração de balanceamento de carga.
```shell
docker run --name mongo-config01 --net mongo-shard -d mongo mongod --configsvr --replSet configserver --port 27017
docker run --name mongo-config02 --net mongo-shard -d mongo mongod --configsvr --replSet configserver --port 27017
docker run --name mongo-config03 --net mongo-shard -d mongo mongod --configsvr --replSet configserver --port 27017
```
![imagem](https://github.com/JonathanWillian5/MongoDB/assets/89879087/83adfee0-8629-429f-9378-103c2e3e3306)


## Configurar Replica Set ConfigServers
> Nesta etapa, vamos configurar os servidores de configuração para o nosso cluster de sharding do MongoDB. 
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
![d4119714-fc2d-4e93-bf0a-e13c66bbb85b](https://github.com/JonathanWillian5/MongoDB/assets/89879087/2b9f03f9-f8e3-4e7c-976c-bada8dc9ed97)


## Criar Containers Shards.
> Para esta etapa, vamos configurar três containers que atuaram como shards, cada shards composto por dois nós para formar um conjunto de réplicas. 
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
![85436b4a-d3ee-4f14-a1b9-39226309e9d0](https://github.com/JonathanWillian5/MongoDB/assets/89879087/71383870-5005-42b1-95bb-a39fdd96f488)


## Configurar Réplica Set Shards.
> Essas configurações serão responsáveis por inicializar conjuntos de réplicas para cada shard no cluster de sharding.
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
![959dd19e-0b03-45be-bbd3-3bb3fcd80691](https://github.com/JonathanWillian5/MongoDB/assets/89879087/9d6d6ff3-2e6e-4784-8228-859845df29fc)
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
![7854265f-f5b2-461c-b1a0-0d924fbcc2af](https://github.com/JonathanWillian5/MongoDB/assets/89879087/b9d7dc2b-e6e5-4e88-9ca9-d18d60e12637)
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
![bbb26b4f-067b-4ee6-b288-7edb15f4da06](https://github.com/JonathanWillian5/MongoDB/assets/89879087/72974b5b-7c1c-4e1b-bd85-4deb9885e3a9)


## Configuração Roteador.
> Nessa etapa iremos criar um container que executa um roteador (mongos) que é o rotedor de sharding do MongoDB.
```shell
docker run -p 27017:27017 --name mongo-router --net mongo-shard -d mongo mongos --port 27017 --configdb 
configserver/mongo-config01:27017,mongo-config02:27017,mongo-config03:27017 --bind_ip_all
```
![b6c77739-ffe1-4259-afbb-40b1818d34fe](https://github.com/JonathanWillian5/MongoDB/assets/89879087/7e8c09bd-2fe5-41db-bfd2-502a777981bd)


## Configuração Cluster Sharding
> Nesta etapa, vamos configurar um cluster de sharding no MongoDB, composto por três shards. 
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
![173bceea-9a42-4789-895d-f7ff96f32697](https://github.com/JonathanWillian5/MongoDB/assets/89879087/a1a3f32e-07c5-4072-9791-555ef346c5da)

## Criação do banco e distribuição entre os shards
> Nessa etapa estamos criando o banco de dados que se chama supermercado, criando um collection para os produtos e uma collection para filiais, o mesmo comando de criação das collections gera um indice para ambas.<br />
 - Para colletion produtos criamos um index do tipo hashed na chave ID.<br />
 - Para a collection filiais criamos um index do tipo hashed na chave document.<br />

```shell
use supermercados
db.produtos.createIndex({"id": "hashed"})
db.filiais.createIndex({"document": "hashed"})
```

![b7df2d6a-36e2-44ef-b874-ae8b9bebcce1](https://github.com/JonathanWillian5/MongoDB/assets/89879087/d186eae6-f955-42c8-b9d4-ca2bc2dcd875)

> Criamos as fragmentações nas duas collection (produto, filiais)
  - Para colletion produtos criamos um shard do tipo hashed na chave ID.<br />
  - Para a collection filiais criamos um shard do tipo hashed na chave document.<br />

> **Note:** O tipo hashed na fragmentação fica responsável pela distribuição uniforme dos dados entre os shards.<br/>
> **Note:** É preciso criar um index na chave a ser fragmentada para conseguir fazer a criação do shard.

```shell
sh.shardCollection("supermercados.produtos", {"id": "hashed})
sh.shardCollection("supermercados.filiais", {"document": "hashed})
```
   
![7d408e3a-842b-462d-a9fd-6c74cf8f9fb3](https://github.com/JonathanWillian5/MongoDB/assets/89879087/a3a4719a-d629-426d-be01-b8a4ebb36320)


# Simulação
## Implementação da estratégia de particionamento
> Com isso é possível garantir uma distribuição balanceada e reduzir a sobrecarga do banco de dados e proporcionar um maior isolamento e segurança dos dados.
Para nossa estratégica adotamos o método de particionamento horizontal e por fragmentação.
 - Vantagens particionamento horizontal e fragmentado:
   
   1 - Escalabilidade: Permite que o banco de dados cresça horizontalmente, adicionando mais servidores para acomodar o aumento de dados e carga de trabalho.
   
   2 - Desempenho: Melhora o desempenho ao reduzir a quantidade de dados que cada consulta precisa processar. Isso é especialmente útil em grandes bancos de dados.
   
   3 - Gerenciamento de Dados: Facilita o gerenciamento e manutenção dos dados, como backup e recuperação, pois cada partição pode ser tratada separadamente.

![79760ea9-4b40-4588-bac2-644a8ccd8d03](https://github.com/JonathanWillian5/MongoDB/assets/89879087/36b7c18a-0ffc-4199-aae2-d2bb986dc8fd)

Na imagem acima é possível ver a distribuição realizada entre os shards na colletions produtos utilizando a estratégia de fragmentação se baseando no hashed da chave ID.

# Teste de funcionamento e desempenho do ambiente

> **Desempenho:**<br/>
Para nosso teste de estresse utilizamos um código python, para realizar multiplas consultas, inserções e updates dentro do ambiente.

![f9e13947-e665-4b85-9beb-15b43e5fe7b6](https://github.com/JonathanWillian5/MongoDB/assets/89879087/3f2d36c5-875d-4b3e-9526-ad5ac7f5d6ac)


>Na imagem abaixo, podemos visualizar como o ambiente se comportou durante as operações realizadas acima.

MONGO:<br/>
![f88df407-7459-43b4-9ffe-a2c7f9cc6ca1](https://github.com/JonathanWillian5/MongoDB/assets/89879087/8c95e7dc-0979-466a-b0b2-5118eff3e895)<br/>
CONTAINERS:<br/>
![ff435965-754f-4a4d-aaf6-6d73c9306806](https://github.com/JonathanWillian5/MongoDB/assets/89879087/1a21eef5-85a9-49dc-b8bb-64316a97cbd4)

> **Consulta:**<br/>
Consulta buscando as informações sobre o estoque de algumas filiais.<br/>

![b3a8098a-5b62-486e-a940-be6b530e97c0](https://github.com/JonathanWillian5/MongoDB/assets/89879087/d76988bd-49f6-4800-a5e3-48eeb24882c4)

> **Atualizações:**<br/>
Atualização realizando a alteração da quantidade do inventário de ulgumas filiais.<br/>

![c6c0b856-8cac-4097-8108-a715a814713d](https://github.com/JonathanWillian5/MongoDB/assets/89879087/b4682db7-49b6-4dfc-9f13-25f793808632)

> **Adição:**<br/>
Realizando a inserçao de novas filiais.<br/>

![9d4a6820-a147-46f9-a6f3-c54c5086f7e3](https://github.com/JonathanWillian5/MongoDB/assets/89879087/98552c52-e008-478e-a83b-d6798e1d718d)



