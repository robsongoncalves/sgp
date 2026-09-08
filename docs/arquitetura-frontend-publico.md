# Arquitetura do Frontend Publico

## Objetivo

O projeto passa a ter dois frontends com responsabilidades separadas:

- `frontend`: aplicacao Angular autenticada, usada para administracao, abertura de solicitacoes e fluxos internos.
- `frontend_public`: catalogo publico em Astro, usado para divulgar servicos, documentacoes e direcionar usuarios para o sistema autenticado.

## Responsabilidades do Astro

O `frontend_public` deve ser estatico sempre que possivel. Ele apresenta:

- pagina inicial do catalogo;
- lista de servicos ativos;
- agrupamento por categorias;
- busca publica;
- pagina publica de detalhe de cada servico;
- link para documentacao;
- botao para iniciar o servico no Angular.

O Astro nao deve criar solicitacoes diretamente. Ao clicar em iniciar, o usuario e encaminhado para o Angular, que cuida da autenticacao e da chamada transacional ao backend.

## Responsabilidades do Angular

O `frontend` permanece como sistema operacional/autenticado:

- login;
- CRUDs administrativos;
- gestao de usuarios, grupos, categorias e servicos;
- abertura de solicitacoes;
- minhas solicitacoes;
- fluxos e tramitacoes futuras.

## Integracao com o Backend

O backend expoe uma API publica especifica para o catalogo:

```text
GET /api/public/services
```

Essa rota retorna apenas dados seguros para publicacao:

- id;
- nome;
- slug;
- descricao;
- link de documentacao;
- destaque;
- ultima atualizacao;
- categorias publicas associadas.

## Build e Publicacao

O Astro gera arquivos estaticos com:

```bash
npm run build
```

O resultado fica em `frontend_public/dist/` e pode ser publicado como HTML estatico.

Para gerar paginas com dados reais, o backend deve estar acessivel durante o build.

## Variaveis de Ambiente

```text
API_BASE_URL=http://localhost:5000/api
PUBLIC_APP_BASE_URL=http://localhost:4200
```

`API_BASE_URL` e usada pelo Astro para consultar o catalogo durante o build ou desenvolvimento.

`PUBLIC_APP_BASE_URL` define para onde o botao iniciar deve encaminhar o usuario.
