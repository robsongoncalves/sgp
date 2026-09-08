import { Component, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { RouterLink } from '@angular/router';

import { ServiceRequest } from '../../core/models/service-request';
import { AuthService } from '../../core/services/auth.service';
import { ServiceRequestService } from '../../core/services/service-request.service';

@Component({
  selector: 'app-minhas-solicitacoes',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
    RouterLink
  ],
  templateUrl: './minhas-solicitacoes.component.html',
  styleUrl: './minhas-solicitacoes.component.scss'
})
export class MinhasSolicitacoesComponent implements OnInit {
  readonly tipoTodos = 'Todos';
  readonly situacaoTodas = 'Todas';

  tipos = [this.tipoTodos];
  situacoes = [this.situacaoTodas];
  solicitacoes: ServiceRequest[] = [];
  filteredSolicitacoes: ServiceRequest[] = [];
  isLoading = false;
  errorMessage = '';

  filterForm = this.formBuilder.nonNullable.group({
    numero: [''],
    criadoAPartirDe: [''],
    tipo: ['Todos'],
    situacao: ['Todas']
  });

  constructor(
    private readonly formBuilder: FormBuilder,
    private readonly authService: AuthService,
    private readonly serviceRequestService: ServiceRequestService
  ) {}

  ngOnInit(): void {
    this.loadSolicitacoes();
  }

  loadSolicitacoes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    const currentUser = this.authService.currentUser;

    if (!currentUser) {
      this.errorMessage = 'Usuario nao autenticado.';
      this.isLoading = false;
      return;
    }

    this.serviceRequestService.list(currentUser.id).subscribe({
      next: (solicitacoes) => {
        this.solicitacoes = solicitacoes;
        this.filteredSolicitacoes = [...solicitacoes];
        this.updateFilterOptions();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar suas solicitacoes.';
        this.isLoading = false;
      }
    });
  }

  pesquisar(): void {
    const filters = this.filterForm.getRawValue();
    const numero = filters.numero.trim();
    const criadoAPartirDe = filters.criadoAPartirDe;

    this.filteredSolicitacoes = this.solicitacoes.filter((solicitacao) => {
      const matchesNumero = !numero || solicitacao.number.includes(numero);
      const matchesTipo = filters.tipo === this.tipoTodos || solicitacao.service_name === filters.tipo;
      const matchesSituacao = filters.situacao === this.situacaoTodas || solicitacao.status === filters.situacao;
      const matchesData = !criadoAPartirDe || this.toDate(solicitacao.created_at) >= criadoAPartirDe;

      return matchesNumero && matchesTipo && matchesSituacao && matchesData;
    });
  }

  limpar(): void {
    this.filterForm.reset({
      numero: '',
      criadoAPartirDe: '',
      tipo: this.tipoTodos,
      situacao: this.situacaoTodas
    });
    this.filteredSolicitacoes = [...this.solicitacoes];
  }

  formatDate(value: string): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return '-';
    }

    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  }

  getContinueRoute(solicitacao: ServiceRequest): string[] {
    const moduleRoutes: Record<string, string> = {
      'calculadora-pontuacao-docente': '/calculadora-pontuacao-docente',
      'progressao-docente': '/progressao-docente'
    };

    const moduleRoute = moduleRoutes[solicitacao.module_key];
    return [moduleRoute || '/servicos', ...(moduleRoute ? [] : [solicitacao.service_slug])];
  }

  getContinueQueryParams(solicitacao: ServiceRequest): Record<string, string | number> {
    if (!this.getContinueRoute(solicitacao)[0].startsWith('/servicos')) {
      return {
        requestId: solicitacao.id,
        requestNumber: solicitacao.number
      };
    }

    return {};
  }

  private toDate(value: string): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return '';
    }

    return date.toISOString().slice(0, 10);
  }

  private updateFilterOptions(): void {
    const tipos = new Set(this.solicitacoes.map((solicitacao) => solicitacao.service_name));
    const situacoes = new Set(this.solicitacoes.map((solicitacao) => solicitacao.status));

    this.tipos = [this.tipoTodos, ...[...tipos].sort((first, second) => first.localeCompare(second, 'pt-BR'))];
    this.situacoes = [this.situacaoTodas, ...[...situacoes].sort((first, second) => first.localeCompare(second, 'pt-BR'))];
  }
}
