import { DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { Service } from '../../core/models/service';
import { AuthService } from '../../core/services/auth.service';
import { ServiceRequestService } from '../../core/services/service-request.service';
import { ServiceService } from '../../core/services/service.service';

@Component({
  selector: 'app-servico-detalhe',
  standalone: true,
  imports: [
    DatePipe,
    RouterLink,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './servico-detalhe.component.html',
  styleUrl: './servico-detalhe.component.scss'
})
export class ServicoDetalheComponent implements OnInit {
  service?: Service;
  isLoading = false;
  isStarting = false;
  isDescriptionExpanded = false;
  errorMessage = '';
  readonly rating = 4.6;
  readonly ratingCount = 66511;
  readonly starOptions = [1, 2, 3, 4, 5];

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly authService: AuthService,
    private readonly serviceRequestService: ServiceRequestService,
    private readonly serviceService: ServiceService
  ) {}

  ngOnInit(): void {
    this.loadService();
  }

  get moduleRoute(): string | undefined {
    const moduleRoutes: Record<string, string> = {
      'calculadora-pontuacao-docente': '/calculadora-pontuacao-docente',
      'progressao-docente': '/progressao-docente'
    };

    if (!this.service?.module_key) {
      return undefined;
    }

    return moduleRoutes[this.service.module_key];
  }

  get updatedAt(): Date | null {
    if (!this.service?.updated_at) {
      return null;
    }

    const date = new Date(`${this.service.updated_at}T00:00:00`);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  get descriptionParagraphs(): string[] {
    return (this.service?.description || '')
      .split(/\n+/)
      .map((paragraph) => paragraph.trim())
      .filter(Boolean);
  }

  get hasLongDescription(): boolean {
    return (this.service?.description || '').length > 360 || this.descriptionParagraphs.length > 2;
  }

  startService(): void {
    if (!this.service || !this.moduleRoute || this.isStarting) {
      return;
    }

    this.isStarting = true;
    this.errorMessage = '';
    const currentUser = this.authService.currentUser;

    if (!currentUser) {
      this.router.navigate(['/login'], {
        queryParams: { returnUrl: this.router.url }
      });
      return;
    }

    this.serviceRequestService.create({
      service_id: this.service.id,
      requester_user_id: currentUser.id
    }).subscribe({
      next: (serviceRequest) => {
        this.router.navigate([this.moduleRoute], {
          queryParams: {
            requestId: serviceRequest.id,
            requestNumber: serviceRequest.number
          }
        });
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel iniciar a solicitacao.';
        this.isStarting = false;
      }
    });
  }

  private loadService(): void {
    const slug = this.route.snapshot.paramMap.get('slug') || '';

    if (!slug) {
      this.errorMessage = 'Servico nao encontrado.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.serviceService.list().subscribe({
      next: (services) => {
        this.service = services.find((service) => service.slug === slug && service.active !== false);
        this.isDescriptionExpanded = false;
        this.errorMessage = this.service ? '' : 'Servico nao encontrado.';
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar o servico.';
        this.isLoading = false;
      }
    });
  }
}
