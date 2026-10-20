"""Carrega o catálogo local no Redis sem alterar chaves de outros exemplos."""

import json
import math
import os
import re
import sys
from datetime import date
from pathlib import Path

import redis
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / 'data' / 'catalogo.json'
PREFIXO = 'lab:clube:catalogo:'
CHAVE_CATEGORIAS = PREFIXO + 'categorias'
CHAVE_ARTIGOS = PREFIXO + 'artigos'
PADRAO_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def carregar_catalogo():
    dados = json.loads(CATALOGO.read_text(encoding='utf-8'))
    if not isinstance(dados, dict):
        raise ValueError('o catálogo deve ser um objeto JSON')

    for tipo, campos in (
        ('categorias', ('id', 'nome', 'descricao')),
        ('artigos', ('id', 'categoria_id', 'titulo', 'resumo', 'autor', 'publicado_em')),
    ):
        itens = dados.get(tipo)
        if not isinstance(itens, list):
            raise ValueError(f'{tipo} deve ser uma lista')
        ids = set()
        for item in itens:
            if not isinstance(item, dict) or any(
                not isinstance(item.get(campo), str) or not item[campo].strip()
                for campo in campos
            ):
                raise ValueError(f'{tipo} contém um item incompleto')
            if not PADRAO_ID.fullmatch(item['id']) or item['id'] in ids:
                raise ValueError(f'{tipo} contém um ID inválido ou duplicado')
            ids.add(item['id'])

    categorias = {item['id'] for item in dados['categorias']}
    for artigo in dados['artigos']:
        if artigo['categoria_id'] not in categorias:
            raise ValueError(f"categoria inexistente no artigo {artigo['id']}")
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', artigo['publicado_em']):
            raise ValueError(f"data inválida no artigo {artigo['id']}")
        date.fromisoformat(artigo['publicado_em'])
    return dados


def configuracao_redis():
    load_dotenv(ROOT / '.env')
    try:
        host = os.environ['REDIS_HOST']
        port = int(os.environ['REDIS_PORT'])
        db = int(os.environ['REDIS_DB'])
        password = os.environ['REDIS_PASSWORD']
        timeout = float(os.getenv('REDIS_TIMEOUT', '5'))
        if not host or not password or not 1 <= port <= 65535 or db < 0:
            raise ValueError('host, senha, porta ou banco inválido')
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('timeout inválido')
    except (KeyError, ValueError) as exc:
        raise ValueError('confira REDIS_HOST, REDIS_PORT, REDIS_DB, '
                         'REDIS_PASSWORD e REDIS_TIMEOUT no .env') from exc
    return dict(host=host, port=port, db=db, password=password,
                socket_connect_timeout=timeout, socket_timeout=timeout,
                decode_responses=True)


def gravar_catalogo(client, dados):
    # Os índices registram quais chaves este script criou na carga anterior.
    antigos_artigos = client.smembers(CHAVE_ARTIGOS)
    antigas_categorias = client.smembers(CHAVE_CATEGORIAS)
    chaves_antigas = [PREFIXO + 'artigo:' + id_ for id_ in antigos_artigos]
    chaves_antigas += [PREFIXO + 'categoria:' + id_ for id_ in antigas_categorias]

    # A transação troca os dados gerenciados pelo script de uma só vez.
    with client.pipeline(transaction=True) as pipeline:
        pipeline.delete(CHAVE_ARTIGOS, CHAVE_CATEGORIAS, *chaves_antigas)
        for categoria in dados['categorias']:
            pipeline.set(PREFIXO + 'categoria:' + categoria['id'],
                         json.dumps(categoria, ensure_ascii=False, sort_keys=True))
        for artigo in dados['artigos']:
            pipeline.set(PREFIXO + 'artigo:' + artigo['id'],
                         json.dumps(artigo, ensure_ascii=False, sort_keys=True))
        if dados['categorias']:
            pipeline.sadd(CHAVE_CATEGORIAS,
                          *(item['id'] for item in dados['categorias']))
        if dados['artigos']:
            pipeline.sadd(CHAVE_ARTIGOS,
                          *(item['id'] for item in dados['artigos']))
        pipeline.execute()


def main():
    try:
        dados = carregar_catalogo()
        config = configuracao_redis()
        with redis.Redis(**config) as client:
            gravar_catalogo(client, dados)
    except (OSError, json.JSONDecodeError, ValueError, redis.RedisError) as exc:
        print(f'Falha ao carregar catálogo: {exc}', file=sys.stderr)
        return 1

    print(f"Carga concluída: {len(dados['categorias'])} categorias e "
          f"{len(dados['artigos'])} artigos no prefixo {PREFIXO}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
