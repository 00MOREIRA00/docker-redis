# Ideia de projeto: laboratório de Redis com Docker

> Evolução do repositório `docker-redis`, seguindo o padrão do `docker-postgresql-pgadmin`: um caso de negócio, infraestrutura bem feita, documentação das decisões e roadmap.

---

## Objetivo

Transformar o `docker-redis` (hoje um compose básico) em um laboratório que mostra **para que o Redis serve na prática**, usando o mesmo universo fictício da **Pauta Digital** (plataforma de revistas e newsletters por assinatura) do repositório de PostgreSQL.

O Redis entra como camada ao lado do Postgres: cache, ranking, rate limiting, sessões e mensageria.

## Caso de negócio: o Redis na Pauta Digital

| Problema da Pauta | Recurso do Redis | O que se aprende |
|---|---|---|
| Listar planos e publicações é lento e repetitivo | Cache-aside com TTL (`strings` / `hashes`) | Invalidação de cache, TTL, hit/miss |
| Ranking das publicações mais lidas | `sorted sets` (`ZINCRBY`, `ZREVRANGE`) | Estruturas de dados |
| Login e API sendo abusados | Rate limiting (`INCR` + `EXPIRE`) | Contadores atômicos |
| Sessão de usuário | `hashes` com expiração | Sessões fora da aplicação |
| Avisar sobre nova edição | Pub/Sub e depois `Streams` | Mensageria, consumer groups |

## Parte de infraestrutura

- `docker-compose.yml` com healthcheck (`redis-cli ping`), volume nomeado, rede e `.env`.
- `redis.conf` montado em vez de flags soltas, com `requirepass` vindo do `.env`.
- Redis Insight no compose, com a conexão pré-configurada (equivalente ao pgAdmin com `servers.json`).
- Persistência comparada: **RDB vs AOF**, com teste de reiniciar o container e ver o que sobrou.
- `maxmemory` + política de eviction (`allkeys-lru`): encher a memória de propósito e observar o comportamento.
- **ACL:** usuário só leitura e usuário da aplicação, em vez de uma senha única.
- Backup e restore do RDB/AOF, conferidos com `DBSIZE` ou hash do conteúdo (como o `pg_dump` + `md5` do outro repo).
- Script de carga que popula chaves de exemplo (equivalente ao `dados_exemplo.sql`).
- Etapa avançada: réplica + **Sentinel**, simulando a queda do primário.
- Benchmark com `redis-benchmark`, comparando com e sem cache.

## Estrutura sugerida do repositório

```
docker-redis/
├── docker-compose.yml
├── .env.example              # senha, portas — copie para .env
├── .gitignore
├── README.md
├── melhorias.md
├── redis/
│   ├── redis.conf
│   └── users.acl
├── insight/                  # conexão pré-configurada
├── scripts/                  # carga de dados, benchmark
├── app/                      # main.py evoluído (cache sobre o Postgres)
├── backups/                  # fora do git (.gitignore)
└── docs/
    ├── caso-de-negocio.md
    ├── decisoes.md
    └── tutoriais/            # passo a passo de cada etapa, com os problemas encontrados
```

## Ajustes rápidos no repositório atual

- [ ] Remover `secretpassword` do README e usar `.env.example`.
- [ ] Conferir se `data/` está no `.gitignore` e não foi commitada.
- [ ] Explicar no README o que o `main.py` demonstra.
- [ ] Criar `melhorias.md` e um roadmap com checkboxes.

## Roadmap sugerido

- [ ] 1. Compose sólido: healthcheck, `.env`, `redis.conf`, Redis Insight
- [ ] 2. Persistência (RDB vs AOF) e backup/restore
- [ ] 3. Cache-aside sobre o Postgres da Pauta Digital (rede compartilhada)
- [ ] 4. Ranking (`sorted sets`), rate limiting e sessões
- [ ] 5. Pub/Sub e Streams
- [ ] 6. ACL, eviction e Sentinel
- [ ] 7. README final e documentação das decisões

## Decisão em aberto

- **Integrado:** Redis conectado ao Postgres da Pauta Digital (rede compartilhada entre os dois repos). Conta uma história mais completa.
- **Independente:** caso de negócio próprio para o Redis. Mais simples, sem dependência do outro repo.

## Aviso

Projeto de estudo. As credenciais do `.env.example` são apenas para uso local, não use esta configuração em produção.
