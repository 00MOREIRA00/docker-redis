import redis

# Conectar ao Redis com senha
r = redis.Redis(
    host='localhost',    # Endereço do Redis
    port=6379,           # Porta do Redis
    db=0,                # Banco de dados padrão
    password='RedisSenha' # Senha configurada no Redis via Docker Compose
)

# Inserir um dado no Redis
r.set('Teste', 'Batata')

# Verificar se a inserção foi bem-sucedida
valor = r.get('Teste')

if valor:
    print(f'Valor inserido: {valor.decode("utf-8")}')
else:
    print('Erro ao inserir valor no Redis.')
