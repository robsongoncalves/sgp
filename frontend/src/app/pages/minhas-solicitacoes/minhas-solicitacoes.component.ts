import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

interface Solicitacao {
  numero: string;
  tipo: string;
  situacao: string;
  criadaEm: string;
  ultimaMovimentacao: string;
}

@Component({
  selector: 'app-minhas-solicitacoes',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule
  ],
  templateUrl: './minhas-solicitacoes.component.html',
  styleUrl: './minhas-solicitacoes.component.scss'
})
export class MinhasSolicitacoesComponent {
  readonly tipos = [
    'Todos',
    'Licença para Capacitação',
    'Pagamento de Substituição',
    'Promoção e Progressão Docente'
  ];

  readonly situacoes = [
    'Todas',
    'Finalizado',
    'Em análise',
    'Pendente'
  ];

  readonly solicitacoes: Solicitacao[] = [
    {
      numero: '7591790',
      tipo: 'Licença para Capacitação',
      situacao: 'Finalizado',
      criadaEm: '17/11/2025 - 12:27:10',
      ultimaMovimentacao: '02/12/2025 - 08:55:59'
    },
    {
      numero: '5941697',
      tipo: 'Pagamento de Substituição',
      situacao: 'Finalizado',
      criadaEm: '03/10/2024 - 15:34:28',
      ultimaMovimentacao: '03/10/2024 - 15:39:22'
    }
  ];

  filteredSolicitacoes = [...this.solicitacoes];

  filterForm = this.formBuilder.nonNullable.group({
    numero: [''],
    criadoAPartirDe: [''],
    tipo: ['Todos'],
    situacao: ['Todas']
  });

  constructor(private readonly formBuilder: FormBuilder) {}

  pesquisar(): void {
    const filters = this.filterForm.getRawValue();
    const numero = filters.numero.trim();
    const criadoAPartirDe = filters.criadoAPartirDe;

    this.filteredSolicitacoes = this.solicitacoes.filter((solicitacao) => {
      const matchesNumero = !numero || solicitacao.numero.includes(numero);
      const matchesTipo = filters.tipo === 'Todos' || solicitacao.tipo === filters.tipo;
      const matchesSituacao = filters.situacao === 'Todas' || solicitacao.situacao === filters.situacao;
      const matchesData = !criadoAPartirDe || this.toDate(solicitacao.criadaEm) >= criadoAPartirDe;

      return matchesNumero && matchesTipo && matchesSituacao && matchesData;
    });
  }

  limpar(): void {
    this.filterForm.reset({
      numero: '',
      criadoAPartirDe: '',
      tipo: 'Todos',
      situacao: 'Todas'
    });
    this.filteredSolicitacoes = [...this.solicitacoes];
  }

  private toDate(value: string): string {
    const [date] = value.split(' - ');
    const [day, month, year] = date.split('/');

    return `${year}-${month}-${day}`;
  }
}
