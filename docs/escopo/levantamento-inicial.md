# Levantamento Inicial do Escopo

Este documento registra as primeiras decisoes de dominio para o Sistema de Gestao de Processos da universidade.

## Objetivo

O sistema tem como objetivo automatizar processos administrativos, academicos e de gestao de pessoas da universidade.

Usuarios poderao acessar servicos disponiveis, iniciar solicitacoes individuais e acompanhar seus processos. Grupos responsaveis poderao receber, analisar, tramitar e finalizar solicitacoes conforme regras de permissao e fluxo definidas para cada tipo de processo.

## Perfis e Papeis

### Administrador do Sistema

Usuario com permissao total sobre o sistema.

Pode:

- gerenciar usuarios;
- gerenciar grupos de usuarios;
- gerenciar categorias de processos;
- gerenciar tipos de processos;
- gerenciar situacoes/status;
- gerenciar fluxos;
- configurar permissoes;
- visualizar e administrar todos os processos.

### Administrador de Processos

Usuario responsavel pela configuracao funcional dos processos.

Pode:

- criar categorias de processos;
- cadastrar tipos de processos;
- associar tipos de processos a categorias;
- definir fluxos;
- definir situacoes permitidas;
- configurar transicoes;
- associar grupos de usuarios a categorias e tipos de processos.

A principio, este papel configura a estrutura dos processos. A atuacao em uma solicitacao real deve depender tambem das permissoes do grupo responsavel pela etapa.

### Usuario Solicitante

Usuario comum do sistema.

Pode:

- visualizar servicos disponiveis;
- iniciar uma solicitacao individual;
- acompanhar suas solicitacoes;
- cancelar uma solicitacao quando ela ainda nao tiver sido tramitada;
- responder pendencias quando o fluxo permitir.

### Membro de Grupo

Usuario associado a um grupo responsavel por alguma etapa de processo.

Pode:

- visualizar solicitacoes recebidas pelo grupo, quando tiver permissao;
- atuar em processos atribuidos ao grupo;
- tramitar processos conforme transicoes permitidas.

### Administrador de Grupo

Usuario membro de um grupo com permissao administrativa dentro daquele grupo.

Pode:

- visualizar todos os processos relacionados ao grupo;
- acompanhar processos recebidos pelo grupo;
- eventualmente gerenciar membros ou distribuicoes internas, caso essa regra seja implementada;
- atuar conforme permissoes especificas do grupo por categoria ou tipo de processo.

## Conceitos Principais

### Tipo de Processo

Representa o modelo/base de um processo.

Exemplos:

- Progressao Docente;
- Licenca de Capacitacao;
- Afastamento Integral para Qualificacao.

Um tipo de processo pode estar associado a uma ou mais categorias.

Campos sugeridos:

- nome;
- chave tecnica/slug;
- descricao;
- ativo;
- modulo/tela associada;
- categorias vinculadas.

### Processo ou Solicitacao

Representa uma instancia real iniciada por um usuario.

Exemplo:

Uma solicitacao de Progressao Docente aberta pelo professor Joao.

Campos sugeridos:

- tipo de processo;
- solicitante;
- situacao atual;
- grupo responsavel atual;
- status geral;
- data de abertura;
- data de finalizacao;
- data de cancelamento.

Status geral sugerido:

- em andamento;
- cancelado;
- finalizado.

### Categoria de Processo

Organiza processos por grandes areas.

Exemplos:

- Administrativos;
- RH;
- Academicos;
- Gestao de Pessoas.

Campos sugeridos:

- nome;
- descricao;
- ativo;
- ordem de exibicao.

### Situacao

Representa um status possivel dentro de um processo.

Exemplos para Progressao Docente:

- Submetido para CPPD;
- Analise pela PROGEPE;
- Aprovado;
- Finalizado.

Campos sugeridos:

- nome;
- descricao;
- tipo;
- ativo.

Tipos sugeridos:

- inicial;
- intermediaria;
- final;
- cancelamento.

### Fluxo e Transicao

O fluxo define as situacoes possiveis e a sequencia permitida para cada tipo de processo.

A transicao define uma passagem permitida de uma situacao para outra.

Campos sugeridos:

- tipo de processo;
- situacao origem;
- situacao destino;
- grupo responsavel pela acao;
- exige parecer;
- permite anexo;
- exige anexo;
- finaliza processo;
- ordem.

Regras:

- uma solicitacao so pode mudar para uma situacao permitida pelo fluxo;
- cada transicao pode exigir parecer;
- cada transicao pode permitir ou exigir anexo;
- cada transicao pode ter um grupo autorizado;
- transicoes finais encerram a solicitacao.

### Grupo de Usuarios

Agrupa usuarios para permissao, recebimento e tramitacao de processos.

Campos sugeridos:

- nome;
- descricao;
- ativo.

### Membro de Grupo

Relaciona usuario e grupo.

Campos sugeridos:

- usuario;
- grupo;
- papel no grupo.

Papeis sugeridos:

- membro;
- administrador do grupo.

### Usuario

Usuario do sistema.

Campos sugeridos:

- nome;
- email;
- senha local temporaria para DEV;
- ativo.

Observacoes:

- o login sera integrado com LDAP futuramente;
- a tabela de usuarios devera ser sincronizada com o GURI;
- em producao, a senha local tende a ser removida ou usada apenas em ambiente de desenvolvimento;
- email sera o login principal.

### Historico de Tramitacao

Registra cada mudanca de situacao de uma solicitacao.

Campos sugeridos:

- solicitacao;
- situacao anterior;
- situacao nova;
- usuario responsavel pela acao;
- grupo em nome do qual atuou;
- parecer;
- data/hora.

Regras:

- toda tramitacao deve gerar historico;
- historico nao deve ser apagado em uso normal;
- historico e essencial para auditoria institucional.

### Anexo

Representa documento enviado pelo solicitante ou por um grupo durante a tramitacao.

Campos sugeridos:

- solicitacao;
- tramitacao opcional;
- usuario que enviou;
- nome do arquivo;
- caminho/storage;
- tipo MIME;
- tamanho;
- data/hora.

Regras futuras:

- controlar tipos permitidos;
- controlar tamanho maximo;
- definir se anexo e obrigatorio por transicao;
- definir visibilidade por grupo quando necessario.

## Menus e Permissoes

O menu deve mudar conforme o usuario logado, seus grupos e as permissoes associadas.

Itens iniciais sugeridos:

- Servicos Disponiveis;
- Minhas Solicitacoes;
- Solicitacoes Recebidas;
- Relatorios;
- Administracao.

Menu administrativo sugerido:

- Usuarios;
- Grupos;
- Categorias;
- Tipos de Processo;
- Situacoes;
- Fluxos;
- Permissoes;
- Configuracoes.

Regras:

- "Servicos Disponiveis" mostra processos que o usuario pode iniciar;
- "Minhas Solicitacoes" mostra processos iniciados pelo usuario;
- "Solicitacoes Recebidas" aparece quando o usuario pertence a grupo com permissao de receber ou tramitar processos;
- permissoes devem ser especificas por categoria e/ou tipo de processo;
- um grupo pode ter permissoes diferentes em tipos de processos diferentes.

Permissoes sugeridas:

- visualizar servico;
- iniciar solicitacao;
- receber solicitacoes;
- visualizar solicitacoes do grupo;
- tramitar solicitacoes;
- administrar processos do grupo;
- configurar categoria;
- configurar tipo de processo;
- configurar fluxo;
- configurar usuarios;
- configurar grupos.

## Regras de Negocio Iniciais

### Abertura de Solicitacao

- Um processo sempre nasce de um usuario solicitante.
- O usuario acessa Servicos Disponiveis.
- O usuario escolhe um tipo de processo.
- O sistema cria uma solicitacao individual.
- A solicitacao inicia na situacao inicial configurada para o tipo de processo.

### Cancelamento

- O solicitante pode cancelar uma solicitacao apenas se ela ainda nao tiver sido tramitada.
- Se ja existir tramitacao posterior ao registro inicial, o cancelamento pelo solicitante nao deve ser permitido.

### Tramitacao

- A solicitacao so pode seguir transicoes permitidas pelo fluxo.
- A transicao deve validar a situacao atual.
- A transicao deve validar se o usuario pertence ao grupo autorizado.
- A transicao deve validar parecer obrigatorio quando configurado.
- A transicao deve validar anexo obrigatorio quando configurado.
- A cada tramitacao, a situacao atual da solicitacao deve ser atualizada.
- A cada tramitacao, um registro de historico deve ser criado.

### Responsabilidade por Etapa

- A solicitacao e individual, mas a responsabilidade por etapa pode ser de um grupo.
- Membros do grupo responsavel visualizam a solicitacao em Solicitacoes Recebidas.
- Administradores do grupo podem visualizar todos os processos relacionados ao grupo.

### Prazos

- Prazos por etapa nao serao tratados inicialmente.
- A modelagem pode deixar espaco para incluir prazos futuramente.

## Formularios Especificos por Processo

Inicialmente, cada tipo de processo tera telas desenvolvidas especificamente.

Sugestao de organizacao futura:

```text
modules/
  processos/
    progressao-docente/
      pages/
      components/
      rules/
      schema/
    licenca-capacitacao/
      pages/
      components/
      rules/
      schema/
```

Cada tipo de processo devera ter uma chave tecnica/slug.

Exemplos:

- progressao-docente;
- licenca-capacitacao;
- afastamento-qualificacao.

Essa chave pode ser usada para associar o cadastro do tipo de processo a tela especifica correspondente.

## Convencao para Telas CRUD

Todas as telas CRUD devem seguir o mesmo padrao visual e funcional.

### Tela Inicial: Registros

Tela inicial do CRUD.

Deve conter:

- listagem dos registros existentes;
- tabela com filtro;
- ordenacao por colunas quando possivel;
- paginacao quando possivel;
- acoes compactas por linha;
- duplo clique no registro para editar.

Quando houver suporte da stack, usar um datatable com filtros, ordenacao e paginacao.

### Tela de Formulario

Tela aberta a partir da listagem.

Deve conter:

- formulario de novo registro;
- formulario de edicao;
- validacoes basicas;
- botao salvar;
- opcao de cancelar edicao;
- mensagens de erro e sucesso.

Ao clicar em "Novo", a tela deve abrir o formulario limpo.

Ao clicar em editar ou dar duplo clique em um registro, a tela deve abrir o formulario preenchido para edicao.

Ao clicar em "Cancelar", a tela deve voltar para a listagem de registros.

## CRUDs Prioritarios

Ordem sugerida de implementacao:

1. Usuarios;
2. Grupos;
3. Membros de grupos;
4. Categorias de processos;
5. Tipos de processos;
6. Associacao tipos x categorias;
7. Situacoes;
8. Fluxos e transicoes;
9. Permissoes por grupo/categoria/tipo;
10. Solicitacoes;
11. Tramitacoes;
12. Anexos.

## Implementacao Temporaria para DEV

Enquanto o banco definitivo e a autenticacao LDAP nao forem integrados, o backend pode usar arquivos JSON para emular persistencia dos CRUDs.

Exemplo atual:

```text
backend/data/users.json
```

Essa abordagem permite testar o frontend e validar experiencia de uso sem bloquear o desenvolvimento inicial.

Senhas nao devem ser persistidas em texto puro. Quando houver senha temporaria para DEV, o backend deve armazenar apenas hash.

## Decisoes Ja Tomadas

- Processos sao sempre iniciados por um usuario individual.
- Solicitante pode cancelar apenas antes da primeira tramitacao.
- Prazos por etapa nao serao tratados no inicio.
- Algumas transicoes exigirao parecer obrigatorio.
- Formularios serao especificos por tipo de processo inicialmente.
- Login futuro sera integrado com LDAP.
- Usuarios serao sincronizados com GURI.
- Grupos podem ter usuarios administradores.
- Permissoes serao especificas por categoria e/ou tipo de processo.
- CRUDs iniciam na listagem de registros e abrem o formulario somente para novo registro ou edicao.
