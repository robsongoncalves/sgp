import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { ServiceService } from '../../core/services/service.service';

interface ServicoLista {
  icon: string;
  label: string;
  route: string;
}

@Component({
  selector: 'app-todos-servicos',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './todos-servicos.component.html',
  styleUrl: './todos-servicos.component.scss'
})
export class TodosServicosComponent implements OnInit {
  searchTerm = '';
  isLoading = false;
  errorMessage = '';

  servicos: ServicoLista[] = [];

  constructor(private readonly serviceService: ServiceService) {}

  ngOnInit(): void {
    this.loadServices();
  }

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

  private loadServices(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.serviceService.list().subscribe({
      next: (services) => {
        this.servicos = services
          .filter((service) => service.active)
          .map((service) => ({
            icon: this.resolveIcon(service.name),
            label: service.name,
            route: `/servicos/${service.slug}`
          }));
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os servicos.';
        this.isLoading = false;
      }
    });
  }

}
