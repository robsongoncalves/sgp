import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { Service } from '../../core/models/service';
import { ServiceCategory } from '../../core/models/service-category';
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
  id: number;
  name: string;
  description: string;
  services: ServiceCard[];
}

@Component({
  selector: 'app-categoria-servicos',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './categoria-servicos.component.html',
  styleUrl: '../servicos/servicos.component.scss'
})
export class CategoriaServicosComponent implements OnInit {
  searchTerm = '';
  isLoading = false;
  errorMessage = '';
  selectedCategory: ServiceCategory | null = null;
  categories: ServiceCategory[] = [];
  services: ServiceCard[] = [];
  categoryGroups: ServiceCategoryGroup[] = [];
  expandedCategoryIds = new Set<string>();

  constructor(
    private readonly route: ActivatedRoute,
    private readonly serviceService: ServiceService,
    private readonly serviceCategoryService: ServiceCategoryService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      this.loadCategoryPage(Number(params.get('id')));
    });
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

  toggleCategory(group: ServiceCategoryGroup): void {
    if (this.expandedCategoryIds.has(group.key)) {
      this.expandedCategoryIds.delete(group.key);
      return;
    }

    this.expandedCategoryIds.add(group.key);
  }

  isCategoryExpanded(group: ServiceCategoryGroup): boolean {
    return this.hasFilter || this.expandedCategoryIds.has(group.key);
  }

  showAvailableServices(): void {
    this.searchTerm = '';
    this.categoryGroups.forEach((group) => this.expandedCategoryIds.add(group.key));
  }

  private loadCategoryPage(categoryId: number): void {
    if (!categoryId) {
      this.errorMessage = 'Categoria nao encontrada.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.expandedCategoryIds.clear();

    forkJoin({
      categories: this.serviceCategoryService.list(),
      services: this.serviceService.list()
    }).subscribe({
      next: ({ categories, services }) => {
        this.categories = categories;
        this.selectedCategory = categories.find((category) => category.id === categoryId) || null;
        this.services = services
          .filter((service) => service.active !== false)
          .map((service) => this.toServiceCard(service));
        this.categoryGroups = this.buildCategoryGroups(categoryId);
        this.errorMessage = this.selectedCategory ? '' : 'Categoria nao encontrada.';
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os servicos da categoria.';
        this.isLoading = false;
      }
    });
  }

  private buildCategoryGroups(categoryId: number): ServiceCategoryGroup[] {
    const childCategories = this.categories
      .filter((category) => category.active && category.parent_category_id === categoryId)
      .sort((first, second) => {
        const order = first.display_order - second.display_order;
        return order || first.name.localeCompare(second.name, 'pt-BR');
      });

    const directServices = this.sortServices(
      this.services.filter((service) => service.categoryIds.includes(categoryId))
    );
    const groups: ServiceCategoryGroup[] = [];

    if (directServices.length && this.selectedCategory) {
      groups.push({
        key: `category-${categoryId}`,
        id: categoryId,
        name: this.selectedCategory.name,
        description: this.selectedCategory.description || '',
        services: directServices
      });
    }

    groups.push(
      ...childCategories.map((category) => ({
        key: `category-${category.id}`,
        id: category.id,
        name: category.name,
        description: category.description || '',
        services: this.sortServices(
          this.services.filter((service) =>
            service.categoryIds.some((serviceCategoryId) =>
              this.descendantCategoryIds(category.id).includes(serviceCategoryId)
            )
          )
        )
      }))
    );

    if (!groups.length && this.selectedCategory) {
      groups.push({
        key: `category-${categoryId}`,
        id: categoryId,
        name: this.selectedCategory.name,
        description: this.selectedCategory.description || '',
        services: []
      });
    }

    return groups;
  }

  private toServiceCard(service: Service): ServiceCard {
    return {
      id: service.id,
      icon: this.resolveIcon(service),
      label: service.name,
      description: service.description || '',
      documentationUrl: service.documentation_url || '',
      featured: service.featured || false,
      categoryIds: Array.isArray(service.category_ids) ? service.category_ids : [],
      route: `/servicos/${service.slug}`
    };
  }

  private descendantCategoryIds(categoryId: number): number[] {
    const descendants = this.categories
      .filter((category) => category.active && category.parent_category_id === categoryId)
      .flatMap((category) => this.descendantCategoryIds(category.id));

    return [categoryId, ...descendants];
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
    if (service.module_key === 'progressao-docente') {
      return 'school';
    }

    if (service.slug.includes('licenca') || service.slug.includes('afastamento')) {
      return 'event_available';
    }

    if (service.slug.includes('auxilio') || service.slug.includes('adicional')) {
      return 'payments';
    }

    if (service.slug.includes('declaracao') || service.slug.includes('certidao')) {
      return 'description';
    }

    return 'assignment';
  }
}
