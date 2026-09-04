import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';

interface ProgressaoStep {
  id: 'solicitacao' | 'pontuacao' | 'confirmacao' | 'enviar';
  label: string;
}

interface PontuacaoItem {
  label: string;
  points: string;
  measure: string;
  limit: string;
}

interface PontuacaoRequisito {
  code: string;
  title: string;
  description: string;
  total: string;
  displayed: number;
  scored: number;
  items: PontuacaoItem[];
}

@Component({
  selector: 'app-progressao-docente',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatRadioModule
  ],
  templateUrl: './progressao-docente.component.html',
  styleUrl: './progressao-docente.component.scss'
})
export class ProgressaoDocenteComponent {
  readonly steps: ProgressaoStep[] = [
    {
      id: 'solicitacao',
      label: 'Solicitação'
    },
    {
      id: 'pontuacao',
      label: 'Planilha de pontuação'
    },
    {
      id: 'confirmacao',
      label: 'Confirmação'
    },
    {
      id: 'enviar',
      label: 'Enviar'
    }
  ];

  currentStep: ProgressaoStep['id'] = 'solicitacao';

  readonly requisitoTotals = [
    {
      label: 'Requisito I',
      value: '8,5 pts',
      items: '1 item(ns)',
      progress: 68
    },
    {
      label: 'Requisito II',
      value: '4 pts',
      items: '2 item(ns)',
      progress: 24
    },
    {
      label: 'Requisito III',
      value: '2 pts',
      items: '1 item(ns)',
      progress: 18
    },
    {
      label: 'Requisito IV',
      value: '1,5 pts',
      items: '1 item(ns)',
      progress: 14
    },
    {
      label: 'Requisito V',
      value: '3 pts',
      items: '1 item(ns)',
      progress: 28
    },
    {
      label: 'Requisito VI',
      value: '2 pts',
      items: '1 item(ns)',
      progress: 20
    },
    {
      label: 'Requisito VII',
      value: '6 pts',
      items: '2 item(ns)',
      progress: 48
    },
    {
      label: 'Requisito VIII',
      value: '1 pt',
      items: '1 item(ns)',
      progress: 12
    },
    {
      label: 'Requisito IX',
      value: '0,5 pts',
      items: '1 item(ns)',
      progress: 8
    },
    {
      label: 'Requisito X',
      value: '5 pts',
      items: '3 item(ns)',
      progress: 42
    }
  ];

  readonly scoreHighlights = [
    {
      label: 'Pontuação total',
      value: '395 pts'
    },
    {
      label: 'Critérios utilizados',
      value: '10'
    },
    {
      label: 'Saldo do alvo',
      value: '+320 pts'
    }
  ];

  readonly requisitoFilters = [
    'Todos',
    'Req. I',
    'Req. II',
    'Req. III',
    'Req. IV',
    'Req. V',
    'Req. VI',
    'Req. VII',
    'Req. VIII',
    'Req. IX',
    'Req. X'
  ];

  readonly pontuacaoRequisitos: PontuacaoRequisito[] = [
    {
      code: 'I',
      title: 'Atividades de Ensino na Educação Superior',
      description: 'Atividades conforme estabelece o Art. 44 da Lei no 9.394, de 20 de dezembro de 1996 (LDB), assim compreendidas aquelas formalmente incluídas nos planos de integralização curricular, ou Projetos Pedagógicos, dos Cursos de Graduação e Pós-Graduação da UNIPAMPA;',
      total: '0 pts',
      displayed: 1,
      scored: 0,
      items: [
        {
          label: 'Média semestral do encargo docente do número de horas-aulas semanais ministradas em componentes curriculares de graduação e pós-graduação.',
          points: '1,0 ponto',
          measure: 'por hora-aula',
          limit: 'Mínimo de 8,0 pontos'
        }
      ]
    },
    {
      code: 'II',
      title: 'Atividades de produção intelectual',
      description: 'Atividades abrangendo a produção científica, artística, técnica e cultural, representada por publicações ou formas de expressão usuais e pertinentes aos ambientes acadêmicos específicos, avaliadas de acordo com a sistemática da CAPES e CNPq para as diferentes áreas do conhecimento;',
      total: '0 pts',
      displayed: 18,
      scored: 0,
      items: [
        { label: 'Publicação de livro (autoria, organização e tradução)', points: '4,0 pts', measure: 'por livro', limit: 'Sem limite' },
        { label: 'Publicação de capítulo de livro (autoria e tradução)', points: '1,0 pt', measure: 'por capítulo', limit: 'Sem limite' },
        { label: 'Publicação de artigo com Qualis ou Fator de Impacto', points: '2,0 pts', measure: 'por artigo', limit: 'Sem limite' },
        { label: 'Publicação de artigo sem Qualis e sem Fator de Impacto', points: '1,0 pt', measure: 'por artigo', limit: 'Sem limite' },
        { label: 'Membro de corpo editorial de periódico ou revista', points: '0,5 pt', measure: 'por participação', limit: 'Até 1,0 ponto/ano' },
        { label: 'Consultor ad hoc de projetos de ensino, pesquisa e extensão', points: '0,25 pt', measure: 'por avaliação', limit: 'Até 1,0 ponto/ano' },
        { label: 'Avaliador de artigos em revistas especializadas', points: '0,25 pt', measure: 'por avaliação', limit: 'Até 1,0 ponto/ano' },
        { label: 'Avaliador de trabalhos em eventos', points: '0,25 pt', measure: 'por evento', limit: 'Até 1,0 ponto/ano' },
        { label: 'Autoria de trabalho completo publicado em anais de eventos', points: '1,0 pt', measure: 'por trabalho', limit: 'Sem limite' },
        { label: 'Resumo publicado em anais de eventos', points: '0,5 pt', measure: 'por trabalho', limit: 'Sem limite' },
        { label: 'Autoria de produto artístico ou técnico', points: '1,0 pt', measure: 'por produto', limit: 'Sem limite' },
        { label: 'Produto tecnológico e processo técnico com obtenção de patente', points: '6,0 pts', measure: 'por patente obtida', limit: 'Sem limite' },
        { label: 'Curadoria de coleção artística ou científica registrada na UNIPAMPA', points: '1,0 pt', measure: 'por curadoria', limit: 'Até 2,0 pontos/ano' },
        { label: 'Premiação de produção artístico-cultural e científica', points: '1,0 pt', measure: 'por premiação', limit: 'Sem limite' },
        { label: 'Palestrante em eventos', points: '0,5 pt', measure: 'por atividade', limit: 'Sem limite' },
        { label: 'Ministrante de minicurso, workshop, oficinas ou semelhantes', points: '1,0 pt', measure: 'por atividade', limit: 'Até 2,0 pontos/ano' },
        { label: 'Membro de organização de eventos de pesquisa, ensino ou extensão', points: '0,5 pt', measure: 'por participação', limit: 'Até 1,0 ponto/ano' },
        { label: 'Trabalho apresentado em eventos de pesquisa, ensino ou extensão', points: '0,5 pt', measure: 'por trabalho', limit: 'Sem limite' }
      ]
    },
    {
      code: 'III',
      title: 'Atividades de ensino relacionadas a projetos de ensino',
      description: 'Atividades de Ensino relacionadas a projetos de ensino aprovados pelas instâncias competentes da Instituição e/ou pelos órgãos de fomento;',
      total: '0 pts',
      displayed: 2,
      scored: 0,
      items: [
        { label: 'Coordenação de projeto de ensino', points: '2,0 pts', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' },
        { label: 'Participação em projeto de ensino', points: '1,0 pt', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' }
      ]
    },
    {
      code: 'IV',
      title: 'Cursos, estágios de aperfeiçoamento e pós-graduação',
      description: 'Cursos ou estágios de aperfeiçoamento, especialização e atualização, bem como obtenção de créditos e títulos de pós-graduação stricto sensu, exceto quando contabilizados para fins de promoção acelerada.',
      total: '0 pts',
      displayed: 5,
      scored: 0,
      items: [
        { label: 'Cursos ou minicursos até 30h de carga horária', points: '0,1 pt', measure: 'por curso', limit: 'Sem limite' },
        { label: 'Cursos ou minicursos acima de 30h de carga horária', points: '0,2 pt', measure: 'por curso', limit: 'Sem limite' },
        { label: 'Curso de especialização ou estágio de aperfeiçoamento', points: '0,25 pt', measure: 'por semestre cursado', limit: 'Sem limite' },
        { label: 'Curso de Mestrado', points: '0,75 pt', measure: 'por semestre cursado', limit: 'Sem limite' },
        { label: 'Curso de Doutorado', points: '0,75 pt', measure: 'por semestre cursado', limit: 'Sem limite' }
      ]
    },
    {
      code: 'V',
      title: 'Atividades de pesquisa',
      description: 'Atividades de Pesquisa relacionadas a projetos de pesquisa aprovados pelas instâncias competentes da Instituição e/ou pelos órgãos de fomento;',
      total: '0 pts',
      displayed: 2,
      scored: 0,
      items: [
        { label: 'Coordenação de projeto de pesquisa', points: '2,0 pts', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' },
        { label: 'Participação em projeto de pesquisa', points: '1,0 pt', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' }
      ]
    },
    {
      code: 'VI',
      title: 'Atividades de extensão',
      description: 'Atividades de Extensão relacionadas a projetos de extensão aprovados pelas instâncias competentes da Instituição e/ou pelos órgãos de fomento;',
      total: '0 pts',
      displayed: 2,
      scored: 0,
      items: [
        { label: 'Coordenação de projeto de extensão', points: '2,0 pts', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' },
        { label: 'Participação em projeto de extensão', points: '1,0 pt', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' }
      ]
    },
    {
      code: 'VII',
      title: 'Atividades de gestão',
      description: 'Atividades de gestão, compreendendo atividades de Direção, Coordenação, Assessoramento, Chefia e Assistência na UNIPAMPA, ou em órgão dos Ministérios da Educação, da Cultura e da Ciência, Tecnologia e Inovação, ou outro, relacionado à área de atuação do docente; para estas atividades de gestão, o período mínimo para pontuação será de 15 dias (1/24 ano) de efetivo exercício na atividade. Para demais itens em que a pontuação seja feita por ano, também poderá adotar-se este critério de período mínimo para cálculo da pontuação proporcional ser de 15 dias, quando o tempo de atividade for inferior a 1 ano.',
      total: '0 pts',
      displayed: 17,
      scored: 0,
      items: [
        { label: 'Coordenação ou Presidência de Comissão do CONSUNI', points: '0,5 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenação de Comissão em nível de Campus', points: '1,0 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenação ou Presidência de Conselhos/Comissões Permanentes abrangendo toda Universidade', points: '2,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenador ou Presidente do Conselho Curador', points: '3,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Chefia de Divisão', points: '2,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenações de órgãos na Reitoria ou Pró-Reitorias', points: '4,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Assessoramento da Reitoria', points: '4,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenação ou Direção de órgãos complementares e/ou suplementares', points: '4,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenação de Curso', points: '4,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenação de Projeto Institucional', points: '4,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Chefe de Gabinete', points: '7,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Coordenação Acadêmica', points: '7,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Diretor', points: '7,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Pró-Reitor ou Pró-Reitor Adjunto', points: '7,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Vice-Reitor', points: '7,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Reitor', points: '7,0 pts', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Assessoramento técnico nível INEP/MEC', points: '1,0 pt', measure: 'por ano', limit: 'Sem limite' }
      ]
    },
    {
      code: 'VIII',
      title: 'Representação',
      description: 'Representação, compreendendo a participação em órgãos ou comissões, na UNIPAMPA, ou em órgãos dos Ministérios da Educação, da Cultura e da Ciência, Tecnologia e Inovação, ou outros, relacionados à área de atuação do Docente, na condição de indicado ou eleito;',
      total: '0 pts',
      displayed: 7,
      scored: 0,
      items: [
        { label: 'Representação em órgão relacionado à área de atuação profissional do Docente', points: '0,25 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Representação em órgão dos Ministérios da Educação, Cultura, Ciência, Tecnologia e Inovação', points: '1,0 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Membro do CONSUNI', points: '0,5 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Membro de Comissões de Curso', points: '0,1 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Membro de Comissão/Conselho/NDE em nível de Campus', points: '0,25 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Membro de Conselhos/Comissões Permanentes abrangendo toda Universidade', points: '0,5 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Membro do Conselho Curador', points: '1,0 pt', measure: 'por ano', limit: 'Sem limite' }
      ]
    },
    {
      code: 'IX',
      title: 'Demais atividades de gestão',
      description: 'Demais atividades de gestão no âmbito da UNIPAMPA, podendo ser considerada a representação sindical, desde que o servidor não esteja licenciado nos termos do Art. 92 da Lei 8.112, de 1990;',
      total: '0 pts',
      displayed: 2,
      scored: 0,
      items: [
        { label: 'Demais atividades de gestão no âmbito da UNIPAMPA', points: '0,25 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Representação sindical', points: '0,25 pt', measure: 'por ano', limit: 'Sem limite' }
      ]
    },
    {
      code: 'X',
      title: 'Outras atividades não incluídas no Plano Curricular',
      description: 'Outras atividades não incluídas no Plano Curricular;',
      total: '0 pts',
      displayed: 10,
      scored: 0,
      items: [
        { label: 'Participação em banca avaliadora de Mestrado/Doutorado/Concurso Público Docente', points: '0,5 pt', measure: 'por banca', limit: 'Sem limite' },
        { label: 'Participação em banca de monografia lato sensu, TCC e defesas de estágio', points: '0,25 pt', measure: 'por avaliação', limit: 'Sem limite' },
        { label: 'Orientação de Dissertação/Tese concluída', points: '2,0 pts', measure: 'por orientação', limit: 'Sem limite' },
        { label: 'Orientação de Monografia de Especialização/TCC concluída', points: '1,0 pt', measure: 'por orientação', limit: 'Sem limite' },
        { label: 'Coorientação de Dissertação/Tese concluída', points: '0,5 pt', measure: 'por orientação', limit: 'Sem limite' },
        { label: 'Coorientação de Monografia de Especialização/TCC concluída', points: '0,25 pt', measure: 'por orientação', limit: 'Sem limite' },
        { label: 'Orientações de iniciação científica, ensino, monitoria e extensão', points: '0,5 pt', measure: 'por aluno/ano', limit: 'Sem limite' },
        { label: 'Orientação de estágio supervisionado', points: '0,25 pt', measure: 'por aluno/ano', limit: 'Sem limite' },
        { label: 'Líder de grupo de pesquisa cadastrado no CNPq', points: '0,5 pt', measure: 'por ano', limit: 'Até 0,5 ponto/ano' },
        { label: 'Participante de grupo de pesquisa cadastrado no CNPq', points: '0,25 pt', measure: 'por ano', limit: 'Até 1,0 ponto/ano' }
      ]
    }
  ];

  solicitacaoForm = this.formBuilder.nonNullable.group({
    nome: ['', Validators.required],
    siape: ['', Validators.required],
    cargo: ['', Validators.required],
    classeNivel: ['', Validators.required],
    localExercicio: ['', Validators.required],
    emailInstitucional: ['', [Validators.required, Validators.email]],
    telefone: [''],
    tipoSolicitacao: ['', Validators.required],
    dataUltimaPromocaoProgressao: ['']
  });

  constructor(private readonly formBuilder: FormBuilder) {}

  selectStep(step: ProgressaoStep['id']): void {
    this.currentStep = step;
  }

  isStepDone(index: number): boolean {
    return this.steps.findIndex((step) => step.id === this.currentStep) > index;
  }

  nextStep(): void {
    const currentIndex = this.steps.findIndex((step) => step.id === this.currentStep);
    const next = this.steps[currentIndex + 1];

    if (next) {
      this.currentStep = next.id;
    }
  }

  previousStep(): void {
    const currentIndex = this.steps.findIndex((step) => step.id === this.currentStep);
    const previous = this.steps[currentIndex - 1];

    if (previous) {
      this.currentStep = previous.id;
    }
  }
}
