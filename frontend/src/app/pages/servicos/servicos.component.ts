import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { ServiceCategory } from '../../core/models/service-category';
import { Service } from '../../core/models/service';
import { ServiceCategoryService } from '../../core/services/service-category.service';
import { ServiceService } from '../../core/services/service.service';

interface ServiceCard {
  id: number;
  icon: string;
  label: string;
  description: string;
  documentationUrl: string;
  featured: boolean;
  categoryIds: number[];
  route: string;
}

interface ServiceCategoryGroup {
  key: string;
  id: number | null;
  name: string;
  description: string;
  services: ServiceCard[];
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
export class ServicosComponent implements OnInit {
  searchTerm = '';
  rating = 0;
  hoveredRating = 0;
  comment = '';
  isLoading = false;
  errorMessage = '';
  readonly ratingOptions = [1, 2, 3, 4, 5];

  services: ServiceCard[] = [];
  categories: ServiceCategory[] = [];
  categoryGroups: ServiceCategoryGroup[] = [];
  expandedCategoryIds = new Set<string>();

  constructor(
    private readonly serviceService: ServiceService,
    private readonly serviceCategoryService: ServiceCategoryService
  ) {}

  ngOnInit(): void {
    this.loadAvailableServices();
  }

  get filteredCategoryGroups(): ServiceCategoryGroup[] {
    const term = this.searchTerm.trim().toLowerCase();

    if (!term) {
      return this.categoryGroups;
    }

    return this.categoryGroups
      .map((group) => ({
        ...group,
        services: group.services.filter((service) =>
          `${service.label} ${service.description} ${group.name}`.toLowerCase().includes(term)
        )
      }))
      .filter((group) => group.services.length);
  }

  get hasFilter(): boolean {
    return Boolean(this.searchTerm.trim());
  }

  loadAvailableServices(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.serviceService.list().subscribe({
      next: (services) => {
        this.services = services
          .filter((service) => service.active !== false)
          .map((service) => this.toServiceCard(service));
        this.categoryGroups = this.buildCategoryGroups();
        this.errorMessage = this.services.length
          ? ''
          : 'Nenhum servico disponivel no momento.';
        this.loadCategories();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os servicos disponiveis.';
        this.isLoading = false;
      }
    });
  }

  loadCategories(): void {
    this.serviceCategoryService.list().subscribe({
      next: (categories) => {
        this.categories = categories;
        this.categoryGroups = this.buildCategoryGroups();
      },
      error: () => {
        this.categories = [];
        this.categoryGroups = this.buildCategoryGroups();
      }
    });
  }

  setRating(value: number): void {
    this.rating = value;
  }

  submitRating(): void {
    if (!this.rating) {
      return;
    }
  }

  toggleCategory(group: ServiceCategoryGroup): void {
    const key = this.categoryKey(group);

    if (this.expandedCategoryIds.has(key)) {
      this.expandedCategoryIds.delete(key);
      return;
    }

    this.expandedCategoryIds.add(key);
  }

  isCategoryExpanded(group: ServiceCategoryGroup): boolean {
    return this.hasFilter || this.expandedCategoryIds.has(this.categoryKey(group));
  }

  private toServiceCard(service: Service): ServiceCard {
    return {
      id: service.id,
      icon: this.resolveIcon(service),
      label: service.name,
      description: service.description_text ?? service.description ?? '',
      documentationUrl: service.documentation_url || '',
      featured: service.featured || false,
      categoryIds: Array.isArray(service.category_ids) ? service.category_ids : [],
      route: `/servicos/${service.slug}`
    };
  }

  private categoryKey(group: ServiceCategoryGroup): string {
    return group.key;
  }

  private buildCategoryGroups(): ServiceCategoryGroup[] {
    if (!this.categories.length) {
      return this.services.length
        ? [
            {
              key: 'all',
              id: null,
              name: 'Todos os serviços',
              description: '',
              services: this.sortServices(this.services)
            }
          ]
        : [];
    }

    const activeCategories = this.categories
      .filter((category) => category.active !== false)
      .sort((first, second) => {
        const order = first.display_order - second.display_order;
        return order || first.name.localeCompare(second.name, 'pt-BR');
      });

    const groups: ServiceCategoryGroup[] = activeCategories
      .map((category) => ({
        key: `category-${category.id}`,
        id: category.id,
        name: category.name,
        description: category.description || '',
        services: this.sortServices(
          this.services.filter((service) => service.categoryIds.includes(category.id))
        )
      }))
      .filter((group) => group.services.length);

    const categorizedIds = new Set(groups.flatMap((group) => group.services.map((service) => service.id)));
    const uncategorizedServices = this.services.filter((service) => !categorizedIds.has(service.id));

    if (uncategorizedServices.length) {
      groups.push({
        key: 'uncategorized',
        id: null,
        name: 'Sem categoria',
        description: '',
        services: this.sortServices(uncategorizedServices)
      });
    }

    return groups;
  }

  private sortServices(services: ServiceCard[]): ServiceCard[] {
    return [...services].sort((first, second) => {
      if (first.featured !== second.featured) {
        return first.featured ? -1 : 1;
      }

      return first.label.localeCompare(second.label, 'pt-BR');
    });
  }

  private resolveIcon(service: Service): string {
    if (service.module_key === 'progressao-docente' || service.slug.includes('progressao')) {
      return 'school';
    }

    if (service.slug.includes('afastamento')) {
      return 'travel_explore';
    }

    if (service.slug.includes('licenca')) {
      return 'workspace_premium';
    }

    return 'description';
  }

}
