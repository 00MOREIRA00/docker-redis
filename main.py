import math
import os
import sys
from pathlib import Path

import redis
from dotenv import load_dotenv


def main():
    load_dotenv(Path(__file__).with_name('.env'))

    try:
        host = os.environ['REDIS_HOST']
        password = os.environ['REDIS_PASSWORD']
        port = int(os.environ['REDIS_PORT'])
        db = int(os.environ['REDIS_DB'])
        timeout = float(os.getenv('REDIS_TIMEOUT', '5'))
        if not host or not password:
            raise ValueError('host e senha devem ser preenchidos')
        if not 1 <= port <= 65535 or db < 0:
            raise ValueError('porta ou banco fora do intervalo permitido')
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('timeout deve ser um número positivo e finito')
    except (KeyError, ValueError):
        print('Configuração inválida. Confira REDIS_HOST, REDIS_PORT, REDIS_DB, '
              'REDIS_PASSWORD e REDIS_TIMEOUT no .env ou no ambiente.', file=sys.stderr)
        return 1

    try:
        with redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
            retry=redis.retry.Retry(redis.backoff.NoBackoff(), 0),
        ) as client:
            client.set('Teste', 'Batata')
            valor = client.get('Teste')
    except redis.exceptions.AuthenticationError:
        print('Falha de autenticação no Redis. Confira REDIS_PASSWORD.', file=sys.stderr)
        return 1
    except redis.exceptions.TimeoutError:
        print('Tempo limite de conexão ou operação no Redis excedido. '
              'Confira a disponibilidade do servidor e REDIS_TIMEOUT.', file=sys.stderr)
        return 1
    except redis.exceptions.ConnectionError:
        print('Não foi possível conectar ao Redis. Confira REDIS_HOST, REDIS_PORT '
              'e se o serviço está em execução.', file=sys.stderr)
        return 1
    except redis.exceptions.RedisError:
        print('Falha ao executar a operação no Redis.', file=sys.stderr)
        return 1

    if valor != b'Batata':
        print('Erro ao verificar o valor inserido no Redis.', file=sys.stderr)
        return 1
    print(f'Valor inserido: {valor.decode("utf-8")}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
