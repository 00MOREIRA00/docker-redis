# Redis

Este repositório contém a configuração de um ambiente Docker com Redis, usando Docker Compose, para armazenar dados em cache ou como um banco de dados simples.

## Pré-requisitos

Certifique-se de ter instalado no seu sistema:

* Docker
* Docker Compose v2 ou superior (`docker compose`)
* Python 3 com suporte a `venv` e `pip`, para executar o exemplo Python

## Uso

1. Clone este repositório em sua máquina local:

```
git clone https://github.com/00MOREIRA00/docker-redis.git
```

2. Navegue até o diretório do projeto:
```
cd docker-redis
```

3. Copie o exemplo de configuração e ajuste os valores no `.env` se necessário:

```bash
cp .env.example .env
```

O Compose lê o `.env` automaticamente. `REDIS_INSIGHT_PORT` define a porta local da interface web (padrão: `5540`). `REDIS_PASSWORD` define a senha do servidor e do cliente Python; `REDIS_PORT` define a porta publicada na máquina e usada pelo cliente. A porta interna do contêiner continua sendo `6379`. `REDIS_HOST` e `REDIS_DB` configuram o cliente Python.

Execute o seguinte comando para iniciar os contêineres:
```
docker compose up -d --wait
```
> Isso iniciará os contêineres em segundo plano (-d).

4. Abra o Redis Insight em <http://localhost:5540> (ou na porta `REDIS_INSIGHT_PORT` do `.env`) e adicione uma conexão:

    * Host: `redis` (nome do serviço na rede do Compose).
    * Porta: `6379` (porta interna, mesmo se `REDIS_PORT` for alterada).
    * Usuário: `default`.
    * Senha: valor de `REDIS_PASSWORD` no `.env`.

O Python executado na máquina continua usando `REDIS_HOST=localhost` e a porta `REDIS_PORT`. O Redis Insight guarda suas conexões no volume `redisinsight-data`.

5. Para parar os contêineres, execute:

```
docker compose down
```

## Infraestrutura local

As imagens estão fixadas em `redis:8.4.7-trixie` e `redis/redisinsight:3.8.0`, disponíveis nos catálogos oficiais do [Redis](https://hub.docker.com/_/redis/tags) e do [Redis Insight](https://hub.docker.com/r/redis/redisinsight/tags). As opções do servidor ficam em `redis/redis.conf`, montado somente para leitura. A senha é injetada pelo Compose a partir do `.env`, sem gravá-la no arquivo de configuração versionado. Ela ainda pode ser consultada por quem tem acesso administrativo ao Docker.

As portas do Redis e do Redis Insight são publicadas somente em `127.0.0.1`. O Redis Insight inicia depois que o healthcheck autenticado do Redis retorna `PONG`. Seu próprio healthcheck HTTP permite que `docker compose up -d --wait` aguarde também a interface web ficar disponível.

Confira o estado e faça um ping autenticado:

```bash
docker compose ps
docker compose exec redis sh -c 'REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli ping'
```

O serviço Redis deve aparecer como `healthy` e o ping deve retornar `PONG`. Depois execute `python main.py` conforme as instruções abaixo para validar escrita e leitura autenticadas.

### Persistência

O volume nomeado `redis-data` armazena os dados. O Redis salva um snapshot RDB após 60 segundos se houver alterações e também no encerramento normal. Para forçar um snapshot antes de reiniciar:

```bash
docker compose exec redis sh -c 'REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli SAVE'
docker compose restart redis
```

`docker compose stop` e `docker compose down` preservam os volumes. Para descartar **todos os dados do Redis e as conexões salvas no Redis Insight**, use explicitamente:

```bash
docker compose down --volumes
```

A pasta local `data/` usada anteriormente deixa de ser montada. Seu conteúdo continua no disco e não é migrado automaticamente para o volume nomeado. Preserve essa pasta se precisar dos dados antigos.

## Personalização

### Catálogo de artigos

O arquivo [`data/catalogo.json`](data/catalogo.json) é a fonte local de dados do Clube de Leituras. Ele contém as listas `categorias` e `artigos`. Cada artigo tem um `id` único e usa `categoria_id` para apontar para o `id` de uma categoria. Para adicionar um artigo, inclua um objeto em `artigos` com `id`, `categoria_id`, `titulo`, `resumo`, `autor` e `publicado_em` (data no formato `AAAA-MM-DD`). O `main.py` ainda não lê esse catálogo; o script de carga abaixo envia uma cópia ao Redis.

Confira a sintaxe e leia os dados sem instalar dependências:

```bash
python3 -m json.tool data/catalogo.json > /dev/null
python3 -c 'import json; from pathlib import Path; catalogo = json.loads(Path("data/catalogo.json").read_text(encoding="utf-8")); print(len(catalogo["categorias"]), "categorias,", len(catalogo["artigos"]), "artigos")'
```

Edite o `.env` para personalizar a conexão. Após alterar a senha ou a porta, execute `docker compose up -d` novamente para recriar o serviço com a nova configuração. Variáveis já exportadas no ambiente têm prioridade sobre o `.env`, tanto no Compose quanto no Python.

Para executar o exemplo Python, com Python 3 instalado:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

O script carrega o `.env` da raiz do projeto e deve imprimir `Valor inserido: Batata`.

As dependências estão declaradas em `requirements.txt`: `redis` é o cliente Redis e `python-dotenv` carrega o `.env`. Inicie o Redis com `docker compose up -d` antes de executar o exemplo.

### Carregar o catálogo no Redis

Com o Redis iniciado e as dependências instaladas no ambiente Python, execute:

```bash
python scripts/carregar_catalogo.py
```

O script lê `data/catalogo.json`, valida os IDs, as categorias e as datas, e grava cada item como JSON em uma chave com prefixo `lab:clube:catalogo:`. Ele mantém os conjuntos `lab:clube:catalogo:artigos` e `lab:clube:catalogo:categorias` com os IDs carregados. Você pode executá-lo novamente após editar o arquivo: ele substitui as chaves da carga anterior e remove os itens que saíram do catálogo, sem usar `FLUSHDB` ou apagar outras chaves. Os dados carregados não têm TTL; o cache com expiração será uma etapa separada.

Confira um artigo e os IDs no Redis:

```bash
docker compose exec redis sh -c 'REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli --raw GET lab:clube:catalogo:artigo:primeiros-passos-com-cache'
docker compose exec redis sh -c 'REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli --raw SMEMBERS lab:clube:catalogo:artigos'
```

`REDIS_TIMEOUT` define, em segundos, o limite de conexão e de cada operação do cliente Python (padrão: `5`; deve ser positivo e finito). O cliente não repete automaticamente operações após falhas. Em caso de configuração inválida, falha de autenticação, conexão ou timeout, o script imprime uma mensagem em stderr e termina com código `1`; em caso de sucesso, termina com código `0`.

Se houver falha de conexão, confira `REDIS_HOST`, `REDIS_PORT` e se o contêiner está em execução. Para falhas de autenticação, confira `REDIS_PASSWORD` e recrie o serviço após alterar a senha. Para timeout, verifique a disponibilidade do servidor e ajuste `REDIS_TIMEOUT` se necessário.

O `.env` e suas variantes locais, os arquivos em `data/` exceto `catalogo.json`, os diretórios `backup/` e `backups/` e arquivos Redis `*.rdb` e `*.aof` são ignorados pelo Git. Guarde backups nesses diretórios. O `.env.example` é versionado apenas como modelo.

## Avisos

* Não utilize essas configurações em um ambiente de produção sem adequada segurança e configuração.
As credenciais padrão são fornecidas apenas para fins de demonstração.
* Certifique-se de alterá-las em um ambiente de produção.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir problemas (issues) e enviar solicitações de pull (pull requests).
