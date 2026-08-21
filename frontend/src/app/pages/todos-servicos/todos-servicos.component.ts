import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

interface ServicoLista {
  icon: string;
  label: string;
}

@Component({
  selector: 'app-todos-servicos',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './todos-servicos.component.html',
  styleUrl: './todos-servicos.component.scss'
})
export class TodosServicosComponent {
  searchTerm = '';

  readonly servicos: ServicoLista[] = [
    'Abono de Permanência',
    'Aceleração da Progressão por Capacitação',
    'Aceleração da Promoção',
    'Afastamento do País',
    'Afastamento para Colaboração Técnica',
    'Afastamento para participar de Curso de Formação',
    'Alteração de RT',
    'Acidente em Serviço',
    'Acumulação de Cargo, Emprego, Função Pública ou Outros Vínculos',
    'Adicionais Ocupacionais',
    'Adicional Noturno',
    'Adicional por Serviço Extraordinário',
    'Ajuda de Custo',
    'Alterações Cadastrais',
    'Alteração de Nome, Estado Civil e União Estável',
    'Alteração de Conta Salário',
    'Cadastro e Alteração de Conta para Recebimento de Diárias',
    'Aposentadoria Especial do(a) servidor(a) com deficiência',
    'Aposentadoria Especial por exposição a agentes prejudiciais à saúde',
    'Aposentadoria Voluntária',
    'Aposentadoria por Incapacidade Permanente para o Trabalho',
    'Auxílio Funeral',
    'Auxílio Moradia',
    'Auxílio Natalidade',
    'Auxílio-Transporte',
    'Avaliação da Capacidade Laborativa para fins de Restrição de Atividades ou Readaptação Funcional',
    'Avaliação de Desempenho, Servidores TAE',
    'Averbação de Tempo de Contribuição',
    'Averbação de Tempo de Contribuição com conversão de tempo especial em comum',
    'Boletim de Frequência',
    'Cadastro de Dependentes (Inclusão/Exclusão)',
    'Certidão de Tempo de Contribuição',
    'Cessão de Servidor',
    'Comunicação de Exercício',
    'Concessão de Horário Especial para Servidor, Cônjuge, Filho ou Dependente com Deficiência',
    'Concessões - Alistamento ou Recadastramento Eleitoral',
    'Concessões - Doação de Sangue',
    'Concessões - Falecimento de Pessoa da Família',
    'Concessões - Licença para Casamento',
    'Concessões - Participação em Tribunal do Júri',
    'Concessões - Requisição da Justiça Eleitoral (TRE)',
    'Consultas, Exames e Outros Procedimentos de Saúde Preventiva (Servidor e Dependentes)',
    'Consulta necessidade de capacitação cadastrada no Plano de Desenvolvimento de Pessoas (PDP)',
    'Conversão de tempo especial em comum',
    'Declaração de Vínculo',
    'Desconto de Faltas',
    'Estágio Probatório (TAE e Docentes)',
    'Exames Médicos Periódicos',
    'Exoneração',
    'Férias',
    'Fluxo de prevenção de casos de Nepotismo e de Inobservância do inciso VI do art. 4º da Lei nº 8.027/1990',
    'Gratificação por Encargo de Curso ou Concurso',
    'Gratificação por Trabalhos com Raios-X ou Substâncias Radioativas',
    'Incentivo à Qualificação',
    'Licença Adotante',
    'Licença à Gestante/Adotante - Prorrogação',
    'Licença à Gestante com Avaliação Pericial (Técnicos-Administrativos em Educação)',
    'Licença à Gestante (Natimorto)',
    'Licença à Gestante sem Avaliação Pericial (Docentes)',
    'Licença à Gestante sem Avaliação Pericial (Técnicos-Administrativos em Educação)',
    'Licença para Atividade Política',
    'Licença para Capacitação',
    'Licença para Tratamento de Saúde',
    'Licença para Tratar de Interesses Particulares',
    'Licença Paternidade e Prorrogação (Docentes)',
    'Licença Paternidade e Prorrogação (Técnicos-Administrativos em Educação)',
    'Licença por Motivo de Afastamento do Cônjuge - sem remuneração',
    'Licença por Motivo de Afastamento do Cônjuge - exercício provisório',
    'Licença por Motivo de Doença em Pessoa da Família',
    'Pagamento de Exercícios Anteriores',
    'Pensão Alimentícia',
    'Pensão por Morte',
    'Perfil Profissiográfico Previdenciário (PPP)',
    'Progressão Funcional por Capacitação Profissional',
    'Progressão Funcional por Mérito Profissional',
    'Promoção e Progressão Docente para as Classes A e B',
    'Promoção e Progressão Docente para Classe C - Professor Associado',
    'Promoção Docente para Classe D - Professor Titular',
    'Registro de Frequência (Módulo Frequência/SOUGOV)',
    'Remoção a Pedido (a critério da Administração)',
    'Remoção por Motivo de Saúde',
    'Requisição de Servidor',
    'Rescisão a Pedido de Professor Substituto/Temporário',
    'Ressarcimento de Plano de Saúde',
    'Solicitação de Afastamento Integral para Qualificação (Necessário aprovação em Chamada Interna)',
    'Solicitação de Documentos Funcionais e Declarações Personalizadas',
    'Solicitação de Abertura Concurso Público (Professor Efetivo)',
    'Solicitação de Abertura Processo Seletivo Simplificado (Professor Substituto)',
    'Substituição de Chefia'
  ].map((label) => ({
    icon: this.resolveIcon(label),
    label
  }));

  get filteredServicos(): ServicoLista[] {
    const term = this.searchTerm.trim().toLowerCase();

    if (!term) {
      return this.servicos;
    }

    return this.servicos.filter((servico) =>
      servico.label.toLowerCase().includes(term)
    );
  }

  private resolveIcon(label: string): string {
    const normalizedLabel = label.toLowerCase();

    if (normalizedLabel.includes('licença') || normalizedLabel.includes('afastamento')) {
      return 'event_busy';
    }

    if (normalizedLabel.includes('auxílio') || normalizedLabel.includes('pagamento') || normalizedLabel.includes('gratificação')) {
      return 'payments';
    }

    if (normalizedLabel.includes('aposentadoria') || normalizedLabel.includes('pensão') || normalizedLabel.includes('permanência')) {
      return 'account_balance';
    }

    if (normalizedLabel.includes('promoção') || normalizedLabel.includes('progressão') || normalizedLabel.includes('qualificação')) {
      return 'school';
    }

    if (normalizedLabel.includes('saúde') || normalizedLabel.includes('gestante') || normalizedLabel.includes('acidente')) {
      return 'health_and_safety';
    }

    if (normalizedLabel.includes('cadastro') || normalizedLabel.includes('alteração') || normalizedLabel.includes('declaração')) {
      return 'badge';
    }

    return 'article';
  }
}
