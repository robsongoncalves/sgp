# Levantamento Inicial do Escopo

Este documento registra as primeiras decisoes de dominio para o Sistema de Gestao de Servicos da universidade.

## Objetivo

O sistema tem como objetivo automatizar servicos administrativos, academicos e de gestao de pessoas da universidade.

Usuarios poderao acessar servicos disponiveis, iniciar solicitacoes individuais e acompanhar seus servicos. Unidades responsaveis poderao receber, analisar, tramitar e finalizar solicitacoes conforme regras de permissao e fluxo definidas para cada servico.

Nota de arquitetura: o conceito inicialmente chamado de "Grupo de Usuarios" passa a ser tratado na interface e no dominio como "Unidade". Uma unidade representa setores, divisoes, comissoes, campi ou grupos funcionais, pode possuir unidade pai e unidades filhas, e continua sendo usada para associar usuarios, permissoes, responsabilidades por situacao e caixa postal.

## Perfis e Papeis

### Administrador do Sistema

Usuario com permissao total sobre o sistema.

Pode:

- gerenciar usuarios;
- gerenciar unidades;
- gerenciar categorias de servicos;
- gerenciar servicoss;
- gerenciar situacoes/status dentro de cada servico;
- gerenciar fluxos dentro de cada servico;
- configurar permissoes;
- visualizar e administrar todos os servicos.

### Administrador de Servicos

Usuario responsavel pela configuracao funcional dos servicos.

Pode:

- criar categorias de servicos;
- cadastrar servicoss;
- associar servicoss a categorias;
- definir situacoes permitidas dentro do servico;
- configurar transicoes do fluxo dentro do servico;
- associar unidades a categorias e servicoss.

A principio, este papel configura a estrutura dos servicos. A atuacao em uma solicitacao real deve depender tambem das permissoes da unidade responsavel pela etapa.

### Usuario Solicitante

Usuario comum do sistema.

Pode:

- visualizar servicos disponiveis;
- iniciar uma solicitacao individual;
- acompanhar suas solicitacoes;
- cancelar uma solicitacao quando ela ainda nao tiver sido tramitada;
- responder pendencias quando o fluxo permitir.

### Membro de Unidade

Usuario associado a uma unidade responsavel por alguma etapa de servico.

Pode:

- visualizar solicitacoes recebidas pela unidade, quando tiver permissao;
- atuar em servicos atribuidos a unidade;
- tramitar servicos conforme transicoes permitidas.

### Administrador de Unidade

Usuario membro de uma unidade com permissao administrativa dentro daquela unidade.

Pode:

- visualizar todos os servicos relacionados a unidade;
- acompanhar servicos recebidos pela unidade;
- eventualmente gerenciar membros ou distribuicoes internas, caso essa regra seja implementada;
- atuar conforme permissoes especificas da unidade por categoria ou servico.

## Conceitos Principais

### Servico

Representa o modelo/base de um servico.

Exemplos:

- Progressao Docente;
- Licenca de Capacitacao;
- Afastamento Integral para Qualificacao.

Um servico pode estar associado a uma ou mais categorias.

Cada servico tambem possui suas proprias situacoes e seu proprio fluxo. Nao havera um cadastro geral de situacoes compartilhado entre todos os servicos.

Inicialmente, alguns servicos poderao ter codigo desenvolvido especificamente para eles. O primeiro caso sera o Servico de Progressao Docente. Futuramente, o sistema podera ter uma logica de servico padrao, permitindo configurar formularios e fluxos sem desenvolver uma tela especifica para cada servico.

Campos sugeridos:

- nome;
- chave tecnica/slug;
- descricao;
- ativo;
- modo de implementacao;
- modulo/tela associada;
- categorias vinculadas;
- grupos de usuarios associados;
- situacoes do servico;
- transicoes permitidas entre situacoes.

Modos de implementacao sugeridos:

- modulo especifico: servico atendido por codigo/tela propria, exemplo Progressao Docente;
- servico padrao: servico atendido por uma estrutura generica do sistema, a ser implementada futuramente.

Campos tecnicos sugeridos para implementacao:

- slug: chave unica usada em rotas, permissoes e associacoes;
- implementation_mode: indica se usa modulo especifico ou servico padrao;
- module_key: chave do modulo especifico quando houver tela/codigo proprio;
- form_schema: reservado para formularios configuraveis no futuro;
- active: indica se o tipo aparece ou nao para uso.

### Grupos Associados ao Servico

O Servico deve permitir associar um ou mais grupos de usuarios.

Essa associacao serve para controlar quais grupos podem visualizar, receber, administrar ou tramitar solicitacoes daquele tipo.

Regras sugeridas:

- um servico pode ter varios grupos associados;
- um grupo pode estar associado a varios servicos;
- a associacao deve permitir definir permissoes especificas do grupo naquele tipo;
- membros do grupo podem visualizar areas de menu conforme as permissoes recebidas;
- administradores do grupo podem acompanhar todos os servicos vinculados ao grupo, conforme regra definida para aquela associacao.

Permissoes sugeridas na associacao entre Servico e Grupo:

- visualizar servico;
- iniciar solicitacao em nome proprio, quando aplicavel;
- receber solicitacoes;
- visualizar solicitacoes do grupo;
- tramitar solicitacoes;
- administrar solicitacoes do grupo;
- configurar fluxo do servico, quando aplicavel.

Na primeira implementacao, essa associacao pode comecar simples, apenas vinculando grupos ao servico. Em seguida, pode evoluir para permissoes detalhadas por grupo.

### Servico ou Solicitacao

Representa uma instancia real iniciada por um usuario.

Exemplo:

Uma solicitacao de Progressao Docente aberta pelo professor Joao.

Campos sugeridos:

- servico;
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

### Categoria de Servico

Organiza servicos por grandes areas. Categorias podem possuir uma categoria pai e categorias filhas, permitindo estruturar o catalogo por coordenadorias, divisoes, setores ou temas.

Exemplos:

- Administrativos;
- RH;
- Academicos;
- Gestao de Pessoas.

Campos sugeridos:

- nome;
- descricao;
- categoria pai;
- ativo;
- mostrar no menu principal;
- ordem de exibicao.

Quando uma categoria estiver marcada para aparecer no menu principal, o sistema deve criar uma entrada de navegacao para ela. Ao acessar essa entrada, a tela deve listar suas categorias filhas e os servicos vinculados a cada filha, considerando tambem os servicos de categorias descendentes.

### Situacao do Servico

Representa um status possivel dentro de um servico especifico.

Situacoes nao sao cadastradas em uma tela global. Elas sao cadastradas dentro da tela de Servico, pois cada tipo pode ter seu conjunto proprio de status.

Exemplos para Progressao Docente:

- Submetido para CPPD;
- Analise pela PROGEPE;
- Aprovado;
- Finalizado.

Campos sugeridos:

- nome;
- descricao;
- tipo;
- situacao anterior;
- ordem no fluxo;
- ativo.

Tipos sugeridos:

- inicial;
- intermediaria;
- final;
- cancelamento.

### Fluxo e Transicao

O fluxo pertence ao Servico e define as situacoes possiveis e a sequencia permitida para aquele tipo.

A transicao define uma passagem permitida de uma situacao para outra.

Campos sugeridos:

- servico;
- situacao origem;
- situacao destino;
- grupo responsavel pela acao;
- exige parecer;
- permite anexo;
- exige anexo;
- finaliza servico;
- ordem.

Regras:

- uma solicitacao so pode mudar para uma situacao permitida pelo fluxo;
- cada transicao pode exigir parecer;
- cada transicao pode permitir ou exigir anexo;
- cada transicao pode ter um grupo autorizado;
- transicoes finais encerram a solicitacao.

### Cadastro de Situacoes no Servico

Na tela de Servico deve existir uma area para configuracao das situacoes e do fluxo.

Modelo inicial simples:

- campo de texto para informar a nova situacao;
- select para escolher a situacao anterior;
- opcao para marcar se a situacao e inicial;
- opcao para marcar se a situacao finaliza o servico;
- opcao para marcar se a transicao exige parecer;
- opcao para marcar se a transicao exige anexo;
- grupo responsavel pela etapa/transicao, quando aplicavel.

Ao adicionar uma nova situacao, o sistema deve criar a situacao e, quando houver situacao anterior selecionada, tambem criar a transicao entre elas.

Sugestao de interface:

- manter uma lista/tabela de situacoes ja cadastradas para o servico;
- exibir colunas como ordem, situacao anterior, situacao atual, grupo responsavel, exige parecer, exige anexo e finaliza;
- permitir reordenar ou editar cada situacao;
- impedir mais de uma situacao inicial para o mesmo servico;
- permitir multiplas transicoes saindo da mesma situacao quando o servico puder seguir caminhos alternativos, por exemplo "Aprovar" ou "Devolver para ajuste".

Esse modelo e melhor que apenas uma lista linear, porque deixa espaco para fluxos com bifurcacoes sem complicar a primeira implementacao.

### Unidade

Agrupa usuarios para permissao, recebimento e tramitacao de servicos. Pode representar uma unidade administrativa real, uma comissao, um campus ou um grupo funcional. Uma unidade pode possuir uma unidade pai, permitindo hierarquias como coordenadoria, divisao e setor.

Campos sugeridos:

- nome;
- descricao;
- unidade pai;
- chefia;
- ativo.

### Membro de Unidade

Relaciona usuario e unidade.

Campos sugeridos:

- usuario;
- unidade;
- papel na unidade.

Papeis sugeridos:

- membro;
- administrador da unidade.

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
- Servicos;
- Permissoes;
- Configuracoes.

Regras:

- "Servicos Disponiveis" mostra servicos que o usuario pode iniciar;
- "Minhas Solicitacoes" mostra servicos iniciados pelo usuario;
- "Solicitacoes Recebidas" aparece quando o usuario pertence a grupo com permissao de receber ou tramitar servicos;
- permissoes devem ser especificas por categoria e/ou servico;
- um grupo pode ter permissoes diferentes em servicoss diferentes.

Permissoes sugeridas:

- visualizar servico;
- iniciar solicitacao;
- receber solicitacoes;
- visualizar solicitacoes do grupo;
- tramitar solicitacoes;
- administrar servicos do grupo;
- configurar categoria;
- configurar servico;
- configurar fluxo;
- configurar usuarios;
- configurar grupos.

As permissoes por grupo poderao ser configuradas por Servico. Em uma etapa inicial, o vinculo simples entre grupo e tipo ja permite controlar menus e responsabilidades basicas. Em uma etapa posterior, cada vinculo podera guardar permissoes especificas.

## Regras de Negocio Iniciais

### Abertura de Solicitacao

- Um servico sempre nasce de um usuario solicitante.
- O usuario acessa Servicos Disponiveis.
- O usuario escolhe um servico.
- O sistema cria uma solicitacao individual.
- A solicitacao inicia na situacao inicial configurada para o servico.

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
- Administradores do grupo podem visualizar todos os servicos relacionados ao grupo.

### Prazos

- Prazos por etapa nao serao tratados inicialmente.
- A modelagem pode deixar espaco para incluir prazos futuramente.

## Formularios Especificos por Servico

Inicialmente, alguns servicos terao telas desenvolvidas especificamente. O primeiro modulo especifico sera Progressao Docente.

Futuramente, o sistema podera ter um mecanismo de servico padrao, no qual o administrador configura formulario, situacoes e fluxo sem precisar criar codigo especifico para cada novo tipo.

Sugestao de organizacao futura:

```text
modules/
  servicos/
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

Cada servico devera ter uma chave tecnica/slug.

Exemplos:

- progressao-docente;
- licenca-capacitacao;
- afastamento-qualificacao.

Essa chave pode ser usada para associar o cadastro do servico a tela especifica correspondente.

Quando o Servico usar modulo especifico, o campo `module_key` deve apontar para o modulo correspondente. Quando usar servico padrao, o sistema deve usar a estrutura generica de formulario/fluxo.

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
4. Categorias de servicos;
5. Tipos de servicos;
6. Situacoes e transicoes dentro de servicoss;
7. Associacao tipos x categorias;
8. Permissoes por grupo/categoria/tipo;
9. Solicitacoes;
10. Tramitacoes;
11. Anexos.

## Implementacao Temporaria para DEV

Enquanto o banco definitivo e a autenticacao LDAP nao forem integrados, o backend pode usar arquivos JSON para emular persistencia dos CRUDs.

Exemplo atual:

```text
backend/data/users.json
```

Essa abordagem permite testar o frontend e validar experiencia de uso sem bloquear o desenvolvimento inicial.

Senhas nao devem ser persistidas em texto puro. Quando houver senha temporaria para DEV, o backend deve armazenar apenas hash.

## Decisoes Ja Tomadas

- Servicos sao sempre iniciados por um usuario individual.
- Solicitante pode cancelar apenas antes da primeira tramitacao.
- Prazos por etapa nao serao tratados no inicio.
- Algumas transicoes exigirao parecer obrigatorio.
- Situacoes pertencem ao Servico e nao terao CRUD geral separado.
- O Servico de Progressao Docente sera o primeiro tipo com modulo/codigo especifico.
- O sistema podera ter servico padrao configuravel futuramente.
- Servicos terao grupos de usuarios associados.
- Formularios poderao ser especificos por servico inicialmente.
- Login futuro sera integrado com LDAP.
- Usuarios serao sincronizados com GURI.
- Grupos podem ter usuarios administradores.
- Permissoes serao especificas por categoria e/ou servico.
- CRUDs iniciam na listagem de registros e abrem o formulario somente para novo registro ou edicao.
