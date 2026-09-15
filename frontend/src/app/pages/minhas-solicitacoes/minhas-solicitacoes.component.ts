import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';

import { ServiceRequest } from '../../core/models/service-request';
import { AuthService } from '../../core/services/auth.service';
import { ServiceRequestService } from '../../core/services/service-request.service';

@Component({
  selector: 'app-minhas-solicitacoes',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatIconModule,
    RouterLink
  ],
  templateUrl: './minhas-solicitacoes.component.html',
  styleUrl: './minhas-solicitacoes.component.scss'
})
export class MinhasSolicitacoesComponent implements OnInit {
  solicitacoes: ServiceRequest[] = [];
  filteredSolicitacoes: ServiceRequest[] = [];
  filterTerm = '';
  isLoading = false;
  errorMessage = '';

  constructor(
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
        this.applyFilter(this.filterTerm);
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar suas solicitacoes.';
        this.isLoading = false;
      }
    });
  }

  applyFilter(value: string): void {
    this.filterTerm = value;
    const term = value.trim().toLowerCase();

    if (!term) {
      this.filteredSolicitacoes = [...this.solicitacoes];
      return;
    }

    this.filteredSolicitacoes = this.solicitacoes.filter((solicitacao) => {
      const content = [
        solicitacao.number,
        solicitacao.service_name,
        solicitacao.service_slug,
        solicitacao.status,
        solicitacao.current_situation_name || '',
        this.formatDate(solicitacao.created_at),
        this.formatDate(solicitacao.updated_at)
      ].join(' ');

      return content.toLowerCase().includes(term);
    });
  }

  limpar(): void {
    this.filterTerm = '';
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

}
