import { DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { DocumentType } from '../../core/models/document-type';
import { Service } from '../../core/models/service';
import { ServiceRating } from '../../core/models/service-rating';
import { AuthService } from '../../core/services/auth.service';
import { DocumentTypeService } from '../../core/services/document-type.service';
import { ServiceRequestService } from '../../core/services/service-request.service';
import { ServiceService } from '../../core/services/service.service';

@Component({
  selector: 'app-servico-detalhe',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './servico-detalhe.component.html',
  styleUrl: './servico-detalhe.component.scss'
})
export class ServicoDetalheComponent implements OnInit {
  service?: Service;
  documentTypes: DocumentType[] = [];
  isLoading = false;
  isStarting = false;
  isSavingRating = false;
  errorMessage = '';
  ratingMessage = '';
  averageRating = 0;
  ratingCount = 0;
  selectedRating = 0;
  hoveredRating = 0;
  ratingComment = '';
  comments: ServiceRating[] = [];
  readonly starOptions = [1, 2, 3, 4, 5];

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly authService: AuthService,
    private readonly documentTypeService: DocumentTypeService,
    private readonly serviceRequestService: ServiceRequestService,
    private readonly serviceService: ServiceService
  ) {}

  ngOnInit(): void {
    this.loadDocumentTypes();
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

  get displayRating(): string {
    return this.ratingCount ? this.averageRating.toFixed(1).replace('.', ',') : '-';
  }

  get activeRating(): number {
    return this.hoveredRating || this.selectedRating || Math.round(this.averageRating);
  }

  get descriptionParagraphs(): string[] {
    return (this.service?.description || '')
      .split(/\n+/)
      .map((paragraph) => paragraph.trim())
      .filter(Boolean);
  }

  get serviceSituationsWithDocuments() {
    return (this.service?.situations || [])
      .filter((situation) => this.getSituationDocumentTypes(situation.document_type_ids).length);
  }

  getSituationDocumentTypes(documentTypeIds: number[]): DocumentType[] {
    return documentTypeIds
      .map((documentTypeId) => this.documentTypes.find((documentType) => documentType.id === documentTypeId))
      .filter((documentType): documentType is DocumentType => Boolean(documentType));
  }

  starIcon(star: number, ratingValue = this.activeRating): string {
    return star <= Math.round(ratingValue) ? 'star' : 'star_border';
  }

  setRating(rating: number): void {
    this.selectedRating = rating;
    this.ratingMessage = '';
  }

  saveRating(): void {
    if (!this.service || this.isSavingRating) {
      return;
    }

    const currentUser = this.authService.currentUser;

    if (!currentUser) {
      this.router.navigate(['/login'], {
        queryParams: { returnUrl: this.router.url }
      });
      return;
    }

    if (!this.selectedRating) {
      this.ratingMessage = 'Selecione uma nota para avaliar o servico.';
      return;
    }

    this.isSavingRating = true;
    this.ratingMessage = '';

    this.serviceService.saveRating(this.service.id, {
      user_id: currentUser.id,
      rating: this.selectedRating,
      comment: this.ratingComment
    }).subscribe({
      next: () => {
        this.ratingMessage = 'Avaliacao registrada.';
        this.isSavingRating = false;
        this.loadRatings();
      },
      error: (response) => {
        this.ratingMessage = response?.error?.message || 'Nao foi possivel salvar a avaliacao.';
        this.isSavingRating = false;
      }
    });
  }

  printPage(): void {
    window.print();
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
        this.errorMessage = this.service ? '' : 'Servico nao encontrado.';
        this.isLoading = false;
        this.loadRatings();
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar o servico.';
        this.isLoading = false;
      }
    });
  }

  private loadDocumentTypes(): void {
    this.documentTypeService.list().subscribe({
      next: (documentTypes) => {
        this.documentTypes = documentTypes.filter((documentType) => documentType.active);
      }
    });
  }

  private loadRatings(): void {
    if (!this.service) {
      return;
    }

    const currentUser = this.authService.currentUser;

    this.serviceService.getRatings(this.service.id, currentUser?.id).subscribe({
      next: (summary) => {
        this.averageRating = summary.average_rating || 0;
        this.ratingCount = summary.rating_count || 0;
        this.comments = summary.comments || [];
        this.selectedRating = summary.user_rating?.rating || 0;
        this.ratingComment = summary.user_rating?.comment || '';
      }
    });
  }
}
