import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

interface Servico {
  icon: string;
  label: string;
  route?: string;
}

@Component({
  selector: 'app-servicos',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './servicos.component.html',
  styleUrl: './servicos.component.scss'
})
export class ServicosComponent {
  searchTerm = '';
  rating = 0;
  hoveredRating = 0;
  comment = '';
  readonly ratingOptions = [1, 2, 3, 4, 5];

  services: Servico[] = [
    {
      icon: 'school',
      label: 'Promoção e Progressão Docente para as Classes A e B',
      route: '/progressao-docente'
    },
    {
      icon: 'workspace_premium',
      label: 'Promoção e Progressão Docente para Classe C - Professor Associado',
      route: '/progressao-docente'
    },
    {
      icon: 'military_tech',
      label: 'Promoção Docente para Classe D - Professor Titular',
      route: '/progressao-docente'
    },
    {
      icon: 'travel_explore',
      label: 'Solicitação de Afastamento Integral para Qualificação'
    }
  ];

  get filteredServices(): Servico[] {
    const term = this.searchTerm.trim().toLowerCase();

    if (!term) {
      return this.services;
    }

    return this.services.filter((service) =>
      service.label.toLowerCase().includes(term)
    );
  }

  setRating(value: number): void {
    this.rating = value;
  }

  submitRating(): void {
    if (!this.rating) {
      return;
    }
  }
}
