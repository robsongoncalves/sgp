import { Component, OnDestroy, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { Subject, debounceTime, takeUntil } from 'rxjs';

import { User } from '../../core/models/user';
import { ServiceRequest, ServiceRequestAttachment } from '../../core/models/service-request';
import { AuthService } from '../../core/services/auth.service';
import { ServiceRequestService } from '../../core/services/service-request.service';
import { UserService } from '../../core/services/user.service';

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
  items: PontuacaoItem[];
}

interface FilteredPontuacaoItem {
  item: PontuacaoItem;
  originalIndex: number;
}

interface FilteredPontuacaoRequisito extends PontuacaoRequisito {
  filteredItems: FilteredPontuacaoItem[];
}

interface RequisitoTotal {
  label: string;
  value: string;
  items: string;
  progress: number;
}

interface ScoreHighlight {
  label: string;
  value: string;
}

interface CalculatorFormData {
  pontuacao?: {
    quantities?: Record<string, number>;
    totals?: Record<string, unknown>;
    updatedAt?: string;
  };
}

@Component({
  selector: 'app-progressao-docente',
  standalone: true,
  imports: [
    DatePipe,
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
export class ProgressaoDocenteComponent implements OnInit, OnDestroy {
  readonly steps: ProgressaoStep[] = [
    {
      id: 'solicitacao',
      label: 'Solicitação'
    },
    {
      id: 'pontuacao',
      label: 'Dados do Serviço'
    },
    {
      id: 'confirmacao',
      label: 'Validação'
    },
    {
      id: 'enviar',
      label: 'Conclusão'
    }
  ];

  currentStep: ProgressaoStep['id'] = 'solicitacao';

  readonly requiredScore = 14;
  readonly requiredTeachingScore = 8;
  readonly itemQuantities: Record<string, number> = {};
  requestId: number | null = null;
  attachments: ServiceRequestAttachment[] = [];
  readyScoreCalculations: ServiceRequest[] = [];
  selectedScoreCalculationId: number | null = null;
  uploadingItemKeys = new Set<string>();
  attachmentErrorMessage = '';
  scoreCalculationMessage = '';
  activeRequirementFilter = 'Todos';
  scoreSearchTerm = '';
  scoredOnly = false;
  autosaveStatus: 'idle' | 'saving' | 'saved' | 'error' = 'idle';
  lastAutosaveAt: Date | null = null;

  private readonly autosaveTrigger = new Subject<void>();
  private readonly destroy$ = new Subject<void>();

  get isCalculatorMode(): boolean {
    return this.route.snapshot.routeConfig?.path === 'calculadora-pontuacao-docente';
  }

  get pageTitle(): string {
    return this.isCalculatorMode
      ? 'Calculadora de Pontuação Progressão Docente'
      : 'Progressão Docente';
  }

  get scoreHighlights(): ScoreHighlight[] {
    const totalScore = this.totalScore;
    const balance = totalScore - this.requiredScore;

    return [
      {
        label: 'Pontuação total',
        value: this.formatScore(totalScore)
      },
      {
        label: 'Pontuação necessária',
        value: this.formatScore(this.requiredScore)
      },
      {
        label: 'Critérios utilizados',
        value: String(this.usedCriteriaCount)
      },
      {
        label: 'Saldo do alvo',
        value: `${balance >= 0 ? '+' : ''}${this.formatScore(balance)}`
      }
    ];
  }

  get autosaveLabel(): string {
    if (this.autosaveStatus === 'saving') {
      return 'Salvando...';
    }

    if (this.autosaveStatus === 'saved' && this.lastAutosaveAt) {
      return `Salvo as ${this.lastAutosaveAt.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
      })}`;
    }

    if (this.autosaveStatus === 'error') {
      return 'Erro ao salvar automaticamente';
    }

    return '';
  }

  get requisitoTotals(): RequisitoTotal[] {
    return this.pontuacaoRequisitos.map((requisito) => {
      const total = this.getRequirementTotal(requisito);
      const scoredItems = this.getRequirementScoredCount(requisito);
      const target = requisito.code === 'I' ? this.requiredTeachingScore : this.requiredScore;

      return {
        label: `Requisito ${requisito.code}`,
        value: this.formatScore(total),
        items: `${scoredItems} item(ns)`,
        progress: Math.min((total / target) * 100, 100)
      };
    });
  }

  get filteredPontuacaoRequisitos(): FilteredPontuacaoRequisito[] {
    const selectedCode = this.getFilterRequirementCode(this.activeRequirementFilter);
    const searchTerm = this.normalizeText(this.scoreSearchTerm);

    return this.pontuacaoRequisitos
      .filter((requisito) => !selectedCode || requisito.code === selectedCode)
      .map((requisito) => {
        const requirementMatchesSearch = !searchTerm || this.matchesRequirement(requisito, searchTerm);
        const filteredItems = requisito.items
          .map((item, originalIndex) => ({ item, originalIndex }))
          .filter(({ item, originalIndex }) => {
            const matchesSearch = requirementMatchesSearch || this.matchesItem(item, searchTerm);
            const matchesScored = !this.scoredOnly || this.getItemStoredQuantity(requisito.code, originalIndex) > 0;

            return matchesSearch && matchesScored;
          });

        return {
          ...requisito,
          filteredItems
        };
      })
      .filter((requisito) => requisito.filteredItems.length > 0);
  }

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
      items: [
        { label: 'Coordenação de projeto de ensino', points: '2,0 pts', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' },
        { label: 'Participação em projeto de ensino', points: '1,0 pt', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' }
      ]
    },
    {
      code: 'IV',
      title: 'Cursos, estágios de aperfeiçoamento e pós-graduação',
      description: 'Cursos ou estágios de aperfeiçoamento, especialização e atualização, bem como obtenção de créditos e títulos de pós-graduação stricto sensu, exceto quando contabilizados para fins de promoção acelerada.',
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
      items: [
        { label: 'Coordenação de projeto de pesquisa', points: '2,0 pts', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' },
        { label: 'Participação em projeto de pesquisa', points: '1,0 pt', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' }
      ]
    },
    {
      code: 'VI',
      title: 'Atividades de extensão',
      description: 'Atividades de Extensão relacionadas a projetos de extensão aprovados pelas instâncias competentes da Instituição e/ou pelos órgãos de fomento;',
      items: [
        { label: 'Coordenação de projeto de extensão', points: '2,0 pts', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' },
        { label: 'Participação em projeto de extensão', points: '1,0 pt', measure: 'por projeto', limit: 'Até 3,0 pontos/ano' }
      ]
    },
    {
      code: 'VII',
      title: 'Atividades de gestão',
      description: 'Atividades de gestão, compreendendo atividades de Direção, Coordenação, Assessoramento, Chefia e Assistência na UNIPAMPA, ou em órgão dos Ministérios da Educação, da Cultura e da Ciência, Tecnologia e Inovação, ou outro, relacionado à área de atuação do docente; para estas atividades de gestão, o período mínimo para pontuação será de 15 dias (1/24 ano) de efetivo exercício na atividade. Para demais itens em que a pontuação seja feita por ano, também poderá adotar-se este critério de período mínimo para cálculo da pontuação proporcional ser de 15 dias, quando o tempo de atividade for inferior a 1 ano.',
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
      items: [
        { label: 'Demais atividades de gestão no âmbito da UNIPAMPA', points: '0,25 pt', measure: 'por ano', limit: 'Sem limite' },
        { label: 'Representação sindical', points: '0,25 pt', measure: 'por ano', limit: 'Sem limite' }
      ]
    },
    {
      code: 'X',
      title: 'Outras atividades não incluídas no Plano Curricular',
      description: 'Outras atividades não incluídas no Plano Curricular;',
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

  constructor(
    private readonly route: ActivatedRoute,
    private readonly authService: AuthService,
    private readonly formBuilder: FormBuilder,
    private readonly serviceRequestService: ServiceRequestService,
    private readonly userService: UserService
  ) {}

  ngOnInit(): void {
    this.requestId = Number(this.route.snapshot.queryParamMap.get('requestId')) || null;

    if (this.isCalculatorMode) {
      this.currentStep = 'pontuacao';
      this.autosaveTrigger
        .pipe(debounceTime(700), takeUntil(this.destroy$))
        .subscribe(() => this.saveCalculatorData());
    }

    if (this.requestId) {
      this.loadServiceRequest();
      this.loadAttachments();
    }

    const currentUser = this.authService.currentUser;

    if (!currentUser) {
      return;
    }

    this.fillIdentification(currentUser);
    this.loadReadyScoreCalculations(currentUser.id);

    this.userService.get(currentUser.id).subscribe({
      next: (user) => this.fillIdentification(user)
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.autosaveTrigger.complete();
  }

  updateItemQuantity(requisitoCode: string, itemIndex: number, event: Event): void {
    const input = event.target as HTMLInputElement;
    const quantity = Number(input.value.replace(',', '.'));
    const key = this.getItemKey(requisitoCode, itemIndex);

    this.itemQuantities[key] = Number.isFinite(quantity) && quantity > 0 ? quantity : 0;

    if (this.isCalculatorMode) {
      this.autosaveTrigger.next();
    }
  }

  selectRequirementFilter(filter: string): void {
    this.activeRequirementFilter = filter;
  }

  updateScoreSearch(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.scoreSearchTerm = input.value;
  }

  toggleScoredOnly(checked: boolean): void {
    this.scoredOnly = checked;
  }

  selectScoreCalculation(calculationId: number): void {
    this.selectedScoreCalculationId = calculationId;
  }

  markCalculationReady(): void {
    if (!this.requestId) {
      this.scoreCalculationMessage = 'Nao foi possivel identificar a calculadora atual.';
      return;
    }

    const savedAt = new Date();
    this.scoreCalculationMessage = '';
    this.autosaveStatus = 'saving';

    this.serviceRequestService.updateFormData(this.requestId, this.buildCalculatorFormData(savedAt)).subscribe({
      next: () => {
        this.lastAutosaveAt = savedAt;
        this.autosaveStatus = 'saved';
        this.updateCalculationSituationReady();
      },
      error: (response) => {
        this.autosaveStatus = 'error';
        this.scoreCalculationMessage = response?.error?.message || 'Nao foi possivel salvar a pontuacao antes de marcar como pronta.';
      }
    });
  }

  uploadDocumentation(requisitoCode: string, itemIndex: number, event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';

    if (!file) {
      return;
    }

    const currentUser = this.authService.currentUser;

    if (!this.requestId || !currentUser) {
      this.attachmentErrorMessage = 'Nao foi possivel identificar a solicitacao para anexar o arquivo.';
      return;
    }

    const key = this.getItemKey(requisitoCode, itemIndex);
    this.uploadingItemKeys.add(key);
    this.attachmentErrorMessage = '';

    this.serviceRequestService.uploadAttachment(this.requestId, {
      uploadedByUserId: currentUser.id,
      contextType: 'pontuacao',
      requirementCode: requisitoCode,
      itemIndex: itemIndex + 1,
      file
    }).subscribe({
      next: (attachment) => {
        this.attachments = [attachment, ...this.attachments];
        this.uploadingItemKeys.delete(key);
      },
      error: (response) => {
        this.attachmentErrorMessage = response?.error?.message || 'Nao foi possivel anexar o arquivo.';
        this.uploadingItemKeys.delete(key);
      }
    });
  }

  getItemAttachments(requisitoCode: string, itemIndex: number): ServiceRequestAttachment[] {
    return this.attachments.filter((attachment) => (
      attachment.context_type === 'pontuacao'
      && attachment.requirement_code === requisitoCode
      && attachment.item_index === itemIndex + 1
    ));
  }

  isItemUploading(requisitoCode: string, itemIndex: number): boolean {
    return this.uploadingItemKeys.has(this.getItemKey(requisitoCode, itemIndex));
  }

  downloadAttachment(attachment: ServiceRequestAttachment): void {
    if (!this.requestId) {
      return;
    }

    window.open(
      this.serviceRequestService.getAttachmentDownloadUrl(this.requestId, attachment.id),
      '_blank',
      'noopener'
    );
  }

  deleteAttachment(attachment: ServiceRequestAttachment): void {
    if (!this.requestId) {
      return;
    }

    this.serviceRequestService.deleteAttachment(this.requestId, attachment.id).subscribe({
      next: () => {
        this.attachments = this.attachments.filter((item) => item.id !== attachment.id);
      },
      error: (response) => {
        this.attachmentErrorMessage = response?.error?.message || 'Nao foi possivel remover o anexo.';
      }
    });
  }

  getItemQuantity(requisitoCode: string, itemIndex: number): number | string {
    return this.getItemStoredQuantity(requisitoCode, itemIndex) || '';
  }

  getItemTotal(requisitoCode: string, itemIndex: number, item: PontuacaoItem): number {
    const quantity = this.getItemStoredQuantity(requisitoCode, itemIndex);
    return quantity * this.getItemPointValue(item);
  }

  getRequirementTotal(requisito: PontuacaoRequisito): number {
    return requisito.items.reduce(
      (total, item, index) => total + this.getItemTotal(requisito.code, index, item),
      0
    );
  }

  getRequirementScoredCount(requisito: PontuacaoRequisito): number {
    return requisito.items.filter((_, index) => {
      const quantity = this.itemQuantities[this.getItemKey(requisito.code, index)] || 0;
      return quantity > 0;
    }).length;
  }

  get totalScore(): number {
    return this.pontuacaoRequisitos.reduce(
      (total, requisito) => total + this.getRequirementTotal(requisito),
      0
    );
  }

  get usedCriteriaCount(): number {
    return this.pontuacaoRequisitos.reduce(
      (total, requisito) => total + this.getRequirementScoredCount(requisito),
      0
    );
  }

  formatScore(value: number): string {
    const formatted = new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: Number.isInteger(value) ? 0 : 2,
      maximumFractionDigits: 2
    }).format(value);

    return `${formatted} pts`;
  }

  formatFileSize(sizeBytes: number): string {
    if (sizeBytes < 1024) {
      return `${sizeBytes} B`;
    }

    if (sizeBytes < 1024 * 1024) {
      return `${(sizeBytes / 1024).toFixed(1).replace('.', ',')} KB`;
    }

    return `${(sizeBytes / (1024 * 1024)).toFixed(1).replace('.', ',')} MB`;
  }

  private fillIdentification(user: User): void {
    this.solicitacaoForm.patchValue({
      nome: user.name,
      siape: user.siape || '',
      cargo: user.cargo || '',
      classeNivel: user.classe_nivel || '',
      localExercicio: user.local_exercicio || '',
      emailInstitucional: user.email,
      telefone: user.telefone || ''
    });
  }

  private loadServiceRequest(): void {
    if (!this.requestId) {
      return;
    }

    this.serviceRequestService.get(this.requestId).subscribe({
      next: (serviceRequest) => this.loadCalculatorData(serviceRequest.form_data),
      error: () => {
        this.autosaveStatus = this.isCalculatorMode ? 'error' : this.autosaveStatus;
      }
    });
  }

  private loadCalculatorData(formData: Record<string, unknown> | undefined): void {
    const calculatorData = formData as CalculatorFormData | undefined;
    const quantities = calculatorData?.pontuacao?.quantities;

    if (!quantities || typeof quantities !== 'object') {
      return;
    }

    Object.entries(quantities).forEach(([key, value]) => {
      const quantity = Number(value);
      this.itemQuantities[key] = Number.isFinite(quantity) && quantity > 0 ? quantity : 0;
    });

    if (calculatorData?.pontuacao?.updatedAt) {
      this.lastAutosaveAt = new Date(calculatorData.pontuacao.updatedAt);
      this.autosaveStatus = 'saved';
    }
  }

  private saveCalculatorData(): void {
    if (!this.requestId) {
      return;
    }

    const savedAt = new Date();
    this.autosaveStatus = 'saving';

    this.serviceRequestService.updateFormData(this.requestId, this.buildCalculatorFormData(savedAt)).subscribe({
      next: () => {
        this.lastAutosaveAt = savedAt;
        this.autosaveStatus = 'saved';
      },
      error: () => {
        this.autosaveStatus = 'error';
      }
    });
  }

  private buildCalculatorFormData(savedAt: Date): Record<string, unknown> {
    return {
      pontuacao: {
        quantities: this.itemQuantities,
        totals: {
          totalScore: this.totalScore,
          requiredScore: this.requiredScore,
          requiredTeachingScore: this.requiredTeachingScore,
          usedCriteriaCount: this.usedCriteriaCount,
          requirements: this.requisitoTotals.map((total) => ({
            label: total.label,
            value: total.value,
            items: total.items
          }))
        },
        updatedAt: savedAt.toISOString()
      }
    };
  }

  private updateCalculationSituationReady(): void {
    if (!this.requestId) {
      return;
    }

    this.serviceRequestService.updateSituation(this.requestId, 'Pronta para uso').subscribe({
      next: () => {
        this.scoreCalculationMessage = 'Pontuacao marcada como pronta para uso.';
      },
      error: (response) => {
        this.scoreCalculationMessage = response?.error?.message || 'Nao foi possivel atualizar a situacao da calculadora.';
      }
    });
  }

  private getItemKey(requisitoCode: string, itemIndex: number): string {
    return `${requisitoCode}-${itemIndex}`;
  }

  private getItemStoredQuantity(requisitoCode: string, itemIndex: number): number {
    return this.itemQuantities[this.getItemKey(requisitoCode, itemIndex)] || 0;
  }

  private getItemPointValue(item: PontuacaoItem): number {
    const match = item.points.match(/\d+(?:,\d+)?/);

    if (!match) {
      return 0;
    }

    return Number(match[0].replace(',', '.'));
  }

  private getFilterRequirementCode(filter: string): string {
    return filter === 'Todos' ? '' : filter.replace('Req. ', '');
  }

  private matchesRequirement(requisito: PontuacaoRequisito, searchTerm: string): boolean {
    return [
      requisito.code,
      `requisito ${requisito.code}`,
      requisito.title,
      requisito.description
    ].some((value) => this.normalizeText(value).includes(searchTerm));
  }

  private matchesItem(item: PontuacaoItem, searchTerm: string): boolean {
    if (!searchTerm) {
      return true;
    }

    return [
      item.label,
      item.points,
      item.measure,
      item.limit
    ].some((value) => this.normalizeText(value).includes(searchTerm));
  }

  private normalizeText(value: string): string {
    return value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
  }

  private loadAttachments(): void {
    if (!this.requestId) {
      return;
    }

    this.serviceRequestService.listAttachments(this.requestId, {
      contextType: 'pontuacao'
    }).subscribe({
      next: (attachments) => {
        this.attachments = attachments;
      },
      error: () => {
        this.attachmentErrorMessage = 'Nao foi possivel carregar os anexos da solicitacao.';
      }
    });
  }

  private loadReadyScoreCalculations(userId: number): void {
    if (this.isCalculatorMode) {
      return;
    }

    this.serviceRequestService.list({
      requesterUserId: userId,
      serviceSlug: 'calculadora-de-pontuacao-progressao-docente',
      status: 'Pronta para uso'
    }).subscribe({
      next: (calculations) => {
        this.readyScoreCalculations = calculations;
        this.selectedScoreCalculationId = calculations[0]?.id || null;
      }
    });
  }

  selectStep(step: ProgressaoStep['id']): void {
    if (this.isCalculatorMode) {
      return;
    }

    this.currentStep = step;
  }

  isStepDone(index: number): boolean {
    return this.steps.findIndex((step) => step.id === this.currentStep) > index;
  }

  nextStep(): void {
    if (this.isCalculatorMode) {
      return;
    }

    const currentIndex = this.steps.findIndex((step) => step.id === this.currentStep);
    const next = this.steps[currentIndex + 1];

    if (next) {
      this.currentStep = next.id;
    }
  }

  previousStep(): void {
    if (this.isCalculatorMode) {
      return;
    }

    const currentIndex = this.steps.findIndex((step) => step.id === this.currentStep);
    const previous = this.steps[currentIndex - 1];

    if (previous) {
      this.currentStep = previous.id;
    }
  }
}
