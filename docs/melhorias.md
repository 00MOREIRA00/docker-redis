# Melhorias e roadmap

## Objetivo e escopo

Evoluir este repositório para um laboratório independente de Redis com Docker. O caso de negócio é o **Clube de Leituras**, um catálogo fictício de artigos com ranking de leituras, sessões e notificações.

Todos os dados de exemplo, scripts e configurações ficarão neste projeto. Não haverá dependência de PostgreSQL, de outro repositório ou de serviços externos para executar os exemplos. O catálogo de origem será um arquivo JSON local; o Redis demonstrará cache e suas estruturas de dados.

Os itens abaixo são propostas pendentes, salvo os marcados como concluídos.

## 1. Organização e configuração inicial

- [x] Definir o escopo independente e o caso de negócio próprio.
- [x] Criar o roadmap em `docs/melhorias.md`.
- [ ] Corrigir a divergência entre a senha apresentada no README e a usada no Compose e no Python.
- [ ] Centralizar configurações em variáveis de ambiente e fornecer `.env.example`.
- [ ] Conferir se `.env`, dados persistidos e backups estão ignorados pelo Git.
- [ ] Declarar as dependências Python e documentar instalação e execução do exemplo.
- [ ] Configurar o cliente Python por ambiente, com timeout e tratamento de erros de conexão e autenticação.

## 2. Infraestrutura local

- [ ] Fixar uma versão da imagem Redis em vez de usar `latest`.
- [ ] Adicionar healthcheck autenticado e documentar como verificar a disponibilidade.
- [ ] Adotar volume nomeado e explicar como preservar ou remover os dados.
- [ ] Restringir a porta publicada ao acesso local por padrão.
- [ ] Organizar opções do servidor em `redis/redis.conf`, definindo como fornecer credenciais sem versionar segredos.
- [ ] Incluir Redis Insight no Compose e documentar a conexão.

Critério de conclusão: iniciar o ambiente com as instruções do próprio projeto e executar uma escrita e leitura autenticadas.

## 3. Dados e cache do Clube de Leituras

- [ ] Criar catálogo JSON local com artigos e categorias fictícios.
- [ ] Criar script de carga reproduzível com prefixo de chaves próprio do laboratório.
- [ ] Implementar cache-aside: consultar Redis, carregar o JSON em caso de miss e armazenar o resultado com TTL.
- [ ] Demonstrar hit, miss, expiração e invalidação após alteração do catálogo.
- [ ] Comparar consultas com e sem cache, explicitando as condições da medição.

Critério de conclusão: executar toda a demonstração sem buscar dados de outro projeto ou serviço.

## 4. Estruturas de dados e funcionalidades

- [ ] Ranking de artigos mais lidos com sorted sets.
- [ ] Rate limiting com contador e expiração definidos de forma atômica.
- [ ] Sessões fictícias com hashes e TTL.
- [ ] Notificação de novos artigos com Pub/Sub, mostrando o comportamento sem assinante conectado.
- [ ] Evoluir as notificações para Streams com consumer groups, confirmação e recuperação de mensagens pendentes.

## 5. Persistência e recuperação

- [ ] Comparar RDB e AOF em cenários documentados de reinício e falha.
- [ ] Criar procedimentos de backup e restauração consistentes com o modo de persistência escolhido.
- [ ] Validar a restauração com chaves, valores e TTLs esperados; usar contagem de chaves como conferência complementar.
- [ ] Documentar quais dados são descartáveis e quais precisam de persistência em cada exemplo.

## 6. Operação e tópicos avançados

- [ ] Definir ACLs para usuário da aplicação e usuário de leitura.
- [ ] Experimentar `maxmemory` e políticas de eviction com dados descartáveis.
- [ ] Medir latência, memória e comportamento sob carga com scripts reproduzíveis.
- [ ] Adicionar réplica e Sentinel como cenário avançado opcional, inteiramente contido neste repositório.

## 7. Documentação e validação

- [ ] Atualizar o README com objetivo, pré-requisitos, comandos e resultados esperados.
- [ ] Documentar o caso de negócio em `docs/caso-de-negocio.md`.
- [ ] Registrar decisões e seus motivos em `docs/decisoes.md`.
- [ ] Criar tutoriais por etapa, incluindo problemas encontrados e como resolvê-los.
- [ ] Validar os cenários de cache, expiração, rate limiting e recuperação com verificações reproduzíveis.

## Ordem sugerida

Configuração inicial → infraestrutura → catálogo e cache → estruturas de dados → persistência → operação avançada → revisão final da documentação. Documentar e validar cada etapa durante sua implementação.
