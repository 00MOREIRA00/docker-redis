# Redis

Este repositório contém a configuração de um ambiente Docker com Redis, usando Docker Compose, para armazenar dados em cache ou como um banco de dados simples.

## Pré-requisitos

Certifique-se de ter instalado no seu sistema:

* Docker
* Docker-Compose

## Uso

1. Clone este repositório em sua máquina local:

```
git clone https://github.com/00MOREIRA00/docker-redis.git
```

2. Navegue até o diretório do projeto:
```
cd docker-redis
```

3. Execute o seguinte comando para iniciar os contêineres:
```
docker-compose up -d
```
> Isso iniciará os contêineres em segundo plano (-d).

4. Para acessar a instância do Redis de forma visual, você pode usar o Redis Insight:

    * Baixe e instale o Redis Insight em seu computador aqui.

    * Abra o Redis Insight e adicione uma nova instância Redis.

    * Use as seguintes configurações para conectar:
        * Host: localhost
        * Porta: 6379
        * Senha: secretpassword (ou a senha personalizada, se modificada).

5. Para parar os contêineres, execute:

```
docker-compose down
```

## Personalização

Você pode modificar as configurações do Redis no arquivo docker-compose.yml conforme necessário, como adicionar volumes, configurar senhas personalizadas etc.

## Avisos

* Não utilize essas configurações em um ambiente de produção sem adequada segurança e configuração.
As credenciais padrão são fornecidas apenas para fins de demonstração. 
* Certifique-se de alterá-las em um ambiente de produção.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir problemas (issues) e enviar solicitações de pull (pull requests).













