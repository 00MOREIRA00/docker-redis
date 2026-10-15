# Ideia de projeto: laboratório de Redis com Docker

> Evolução independente do repositório `docker-redis`: um caso de negócio próprio, infraestrutura, documentação das decisões e roadmap.

---

## Objetivo

Transformar o `docker-redis` (hoje um compose básico) em um laboratório independente que mostra **para que o Redis serve na prática**.

O caso de negócio será o **Clube de Leituras**, uma aplicação fictícia de catálogo de artigos, ranking de leituras e notificações. Dados de origem serão arquivos JSON locais e os exemplos serão executados neste repositório, sem PostgreSQL ou serviços de outros projetos.

## Caso de negócio: o Redis na Clube de Leituras

| Problema do Clube | Recurso do Redis | O que se aprende |
|---|---|---|
| Listar artigos e categorias é lento e repetitivo | Cache-aside com TTL (`strings` / `hashes`) | Invalidação de cache, TTL, hit/miss |
| Ranking das publicações mais lidas | `sorted sets` (`ZINCRBY`, `ZREVRANGE`) | Estruturas de dados |
| Login e API sendo abusados | Rate limiting (`INCR` + `EXPIRE`) | Contadores atômicos |
| Sessão de usuário | `hashes` com expiração | Sessões fora da aplicação |
| Avisar sobre nova edição | Pub/Sub e depois `Streams` | Mensageria, consumer groups |

## Parte de infraestrutura

- `docker-compose.yml` com healthcheck (`redis-cli ping`), volume nomeado, rede e `.env`.
- `redis.conf` montado em vez de flags soltas, com `requirepass` vindo do `.env`.
- Redis Insight no compose, com a conexão pré-configurada.
- Persistência comparada: **RDB vs AOF**, com teste de reiniciar o container e ver o que sobrou.
- `maxmemory` + política de eviction (`allkeys-lru`): encher a memória de propósito e observar o comportamento.
- **ACL:** usuário só leitura e usuário da aplicação, em vez de uma senha única.
- Backup e restore do RDB/AOF, conferidos com `DBSIZE` ou hash do conteúdo.
- Script de carga que popula chaves de exemplo.
- Etapa avançada: réplica + **Sentinel**, simulando a queda do primário.
- Benchmark com `redis-benchmark`, comparando com e sem cache.

## Estrutura sugerida do repositório

```
docker-redis/
├── docker-compose.yml
├── .env.example              # senha, portas — copie para .env
├── .gitignore
├── README.md
├── redis/
│   ├── redis.conf
│   └── users.acl
├── insight/                  # conexão pré-configurada
├── scripts/                  # carga de dados, benchmark
├── app/                      # main.py evoluído (cache sobre arquivos JSON locais)
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
- [x] Criar `docs/melhorias.md` e um roadmap com checkboxes.

## Roadmap sugerido

- [ ] 1. Compose sólido: healthcheck, `.env`, `redis.conf`, Redis Insight
- [ ] 2. Persistência (RDB vs AOF) e backup/restore
- [ ] 3. Cache-aside sobre dados JSON locais do Clube de Leituras
- [ ] 4. Ranking (`sorted sets`), rate limiting e sessões
- [ ] 5. Pub/Sub e Streams
- [ ] 6. ACL, eviction e Sentinel
- [ ] 7. README final e documentação das decisões

## Decisão de escopo

**Independente:** caso de negócio próprio para o Redis, sem dependência de outro repositório. Docker Compose deverá iniciar a infraestrutura necessária; dados de exemplo, scripts e documentação ficarão neste projeto. O cache usará um catálogo JSON local como fonte de dados.

## Aviso

Projeto de estudo. As credenciais do `.env.example` são apenas para uso local, não use esta configuração em produção.
