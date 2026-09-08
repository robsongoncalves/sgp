# SGP Frontend Publico

Catalogo publico de servicos construido com Astro.

## Desenvolvimento

```bash
npm install
npm run dev
```

Por padrao, o catalogo busca os dados em `http://localhost:5000/api`.
Para gerar as paginas estaticas com servicos reais, deixe o backend acessivel antes de rodar `npm run build`.

Variaveis uteis:

```bash
API_BASE_URL=http://localhost:5000/api
PUBLIC_APP_BASE_URL=http://localhost:4200
```

## Build estatico

```bash
npm run build
```

O resultado fica em `dist/` e pode ser publicado como HTML estatico.
