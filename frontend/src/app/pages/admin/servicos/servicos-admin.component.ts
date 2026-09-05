import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { forkJoin } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';

import { ServiceCategory } from '../../../core/models/service-category';
import {
  ServiceSituation,
  ServiceSituationDraft,
  Service,
  ServicePayload
} from '../../../core/models/service';
import { UserGroup } from '../../../core/models/user-group';
import { ServiceCategoryService } from '../../../core/services/service-category.service';
import { ServiceService } from '../../../core/services/service.service';
import { UserGroupService } from '../../../core/services/user-group.service';

@Component({
  selector: 'app-servicos-admin',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatIconModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSortModule,
    MatTableModule
  ],
  templateUrl: './servicos-admin.component.html',
  styleUrl: './servicos-admin.component.scss'
})
export class ServicosAdminComponent implements OnInit, AfterViewInit {
  services: Service[] = [];
  categories: ServiceCategory[] = [];
  groups: UserGroup[] = [];
  dataSource = new MatTableDataSource<Service>([]);
  displayedColumns = ['name', 'implementation_mode', 'categories', 'groups', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingServiceId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';

  form: ServicePayload = this.createEmptyForm();
  situationDraft: ServiceSituationDraft = this.createEmptySituationDraft();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private readonly serviceService: ServiceService,
    private readonly serviceCategoryService: ServiceCategoryService,
    private readonly userGroupService: UserGroupService
  ) {}

  ngOnInit(): void {
    this.loadReferenceData();
    this.loadServices();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingServiceId !== null;
  }

  get customModuleSelected(): boolean {
    return this.form.implementation_mode === 'custom_module';
  }

  loadReferenceData(): void {
    forkJoin({
      categories: this.serviceCategoryService.list(),
      groups: this.userGroupService.list()
    }).subscribe({
      next: ({ categories, groups }) => {
        this.categories = categories;
        this.groups = groups;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar categorias e grupos.';
      }
    });
  }

  loadServices(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.serviceService.list().subscribe({
      next: (services) => {
        this.services = services;
        this.dataSource.data = services;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os servicos.';
        this.isLoading = false;
      }
    });
  }

  saveService(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome do servico.';
      return;
    }

    if (!this.form.slug.trim()) {
      this.errorMessage = 'Informe o slug do servico.';
      return;
    }

    if (this.customModuleSelected && !this.form.module_key.trim()) {
      this.errorMessage = 'Informe a chave do modulo especifico.';
      return;
    }

    if (this.form.situations.length && !this.form.situations.some((situation) => situation.is_initial)) {
      this.errorMessage = 'Informe uma situacao inicial.';
      return;
    }

    const payload = this.normalizePayload();

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.serviceService.update(this.editingServiceId as number, payload)
      : this.serviceService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Servico atualizado com sucesso.'
          : 'Servico cadastrado com sucesso.';
        this.closeForm();
        this.loadServices();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar o servico.';
        this.isSaving = false;
      }
    });
  }

  editService(service: Service): void {
    this.editingServiceId = service.id;
    this.form = {
      name: service.name,
      slug: service.slug,
      description: service.description || '',
      documentation_url: service.documentation_url || '',
      implementation_mode: service.implementation_mode,
      module_key: service.module_key,
      active: service.active,
      featured: service.featured || false,
      updated_at: service.updated_at || '',
      category_ids: [...service.category_ids],
      group_ids: [...service.group_ids],
      situations: service.situations.map((situation) => ({ ...situation }))
    };
    this.situationDraft = this.createEmptySituationDraft();
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
  }

  createService(): void {
    this.resetForm();
    this.isFormVisible = true;
  }

  applyFilter(value: string): void {
    this.filterTerm = value;
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  toggleServiceStatus(service: Service): void {
    this.serviceService.update(service.id, {
      ...service,
      active: !service.active
    }).subscribe({
      next: () => this.loadServices(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteService(service: Service): void {
    const confirmed = window.confirm(`Remover o servico ${service.name}?`);

    if (!confirmed) {
      return;
    }

    this.serviceService.delete(service.id).subscribe({
      next: () => {
        this.successMessage = 'Servico removido com sucesso.';
        this.loadServices();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover o servico.';
      }
    });
  }

  toggleCategory(categoryId: number, checked: boolean): void {
    this.form.category_ids = this.toggleId(this.form.category_ids, categoryId, checked);
  }

  toggleGroup(groupId: number, checked: boolean): void {
    this.form.group_ids = this.toggleId(this.form.group_ids, groupId, checked);
  }

  addSituation(): void {
    if (!this.situationDraft.name.trim()) {
      this.errorMessage = 'Informe o nome da situacao.';
      return;
    }

    const nextId = this.nextSituationId();
    const shouldBeInitial = this.form.situations.length === 0 || this.situationDraft.is_initial;
    const newSituation: ServiceSituation = {
      id: nextId,
      name: this.situationDraft.name.trim(),
      previous_situation_id: shouldBeInitial ? null : this.situationDraft.previous_situation_id,
      responsible_group_id: this.situationDraft.responsible_group_id || null,
      is_initial: shouldBeInitial,
      is_final: this.situationDraft.is_final,
      requires_opinion: this.situationDraft.requires_opinion,
      requires_attachment: this.situationDraft.requires_attachment,
      display_order: this.form.situations.length + 1
    };

    if (newSituation.is_initial) {
      this.form.situations = this.form.situations.map((situation) => ({
        ...situation,
        is_initial: false
      }));
    }

    this.form.situations = [...this.form.situations, newSituation];
    this.situationDraft = this.createEmptySituationDraft();
    this.errorMessage = '';
  }

  removeSituation(situation: ServiceSituation): void {
    this.form.situations = this.form.situations
      .filter((item) => item.id !== situation.id)
      .map((item, index) => ({
        ...item,
        previous_situation_id:
          item.previous_situation_id === situation.id ? null : item.previous_situation_id,
        display_order: index + 1
      }));
  }

  markInitialSituation(situation: ServiceSituation): void {
    this.form.situations = this.form.situations.map((item) => ({
      ...item,
      is_initial: item.id === situation.id,
      previous_situation_id: item.id === situation.id ? null : item.previous_situation_id
    }));
  }

  resetForm(): void {
    this.editingServiceId = null;
    this.form = this.createEmptyForm();
    this.situationDraft = this.createEmptySituationDraft();
  }

  closeForm(): void {
    this.resetForm();
    this.errorMessage = '';
    this.isFormVisible = false;
  }

  categoryNames(categoryIds: number[]): string {
    const names = this.categories
      .filter((category) => categoryIds.includes(category.id))
      .map((category) => category.name);

    return names.length ? names.join(', ') : '-';
  }

  groupNames(groupIds: number[]): string {
    const names = this.groups
      .filter((group) => groupIds.includes(group.id))
      .map((group) => group.name);

    return names.length ? names.join(', ') : '-';
  }

  implementationModeLabel(service: Service): string {
    return service.implementation_mode === 'custom_module'
      ? 'Modulo especifico'
      : 'Servico padrao';
  }

  previousSituationName(situationId: number | null): string {
    if (!situationId) {
      return '-';
    }

    return this.form.situations.find((situation) => situation.id === situationId)?.name || '-';
  }

  responsibleGroupName(groupId: number | null): string {
    if (!groupId) {
      return '-';
    }

    return this.groups.find((group) => group.id === groupId)?.name || '-';
  }

  syncSlugFromName(): void {
    if (this.isEditing || this.form.slug.trim()) {
      return;
    }

    this.form.slug = this.slugify(this.form.name);
  }

  syncModuleKey(): void {
    if (this.customModuleSelected && !this.form.module_key.trim()) {
      this.form.module_key = this.form.slug;
    }
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (service, filter) => {
      const content = [
        service.name,
        service.slug,
        service.description || '',
        service.documentation_url || '',
        this.implementationModeLabel(service),
        this.categoryNames(service.category_ids),
        this.groupNames(service.group_ids),
        service.featured ? 'destaque' : '',
        service.active ? 'ativo' : 'inativo'
      ].join(' ');

      return content.toLowerCase().includes(filter);
    };
  }

  private normalizePayload(): ServicePayload {
    return {
      ...this.form,
      name: this.form.name.trim(),
      slug: this.slugify(this.form.slug),
      description: (this.form.description || '').trim(),
      documentation_url: (this.form.documentation_url || '').trim(),
      module_key: (this.form.module_key || '').trim(),
      featured: this.form.featured,
      updated_at: this.form.updated_at || '',
      category_ids: [...this.form.category_ids],
      group_ids: [...this.form.group_ids],
      situations: this.form.situations.map((situation, index) => ({
        ...situation,
        display_order: index + 1
      }))
    };
  }

  private createEmptyForm(): ServicePayload {
    return {
      name: '',
      slug: '',
      description: '',
      documentation_url: '',
      implementation_mode: 'custom_module',
      module_key: '',
      active: true,
      featured: false,
      updated_at: '',
      category_ids: [],
      group_ids: [],
      situations: []
    };
  }

  private createEmptySituationDraft(): ServiceSituationDraft {
    return {
      name: '',
      previous_situation_id: null,
      responsible_group_id: null,
      is_initial: false,
      is_final: false,
      requires_opinion: false,
      requires_attachment: false,
      display_order: 0
    };
  }

  private nextSituationId(): number {
    if (!this.form.situations.length) {
      return 1;
    }

    return Math.max(...this.form.situations.map((situation) => situation.id)) + 1;
  }

  private toggleId(ids: number[], id: number, checked: boolean): number[] {
    if (checked) {
      return [...new Set([...ids, id])];
    }

    return ids.filter((item) => item !== id);
  }

  private slugify(value: string): string {
    return value
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/-+/g, '-');
  }
}
