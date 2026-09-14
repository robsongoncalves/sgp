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

import { AutomationFunction } from '../../../core/models/automation-function';
import { DocumentPurpose, DocumentType } from '../../../core/models/document-type';
import { ServiceCategory } from '../../../core/models/service-category';
import {
  ServiceHook,
  ServiceHookDraft,
  ServiceSituation,
  ServiceSituationDraft,
  Service,
  ServicePayload
} from '../../../core/models/service';
import { UserGroup } from '../../../core/models/user-group';
import { AutomationFunctionService } from '../../../core/services/automation-function.service';
import { DocumentTypeService } from '../../../core/services/document-type.service';
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
  automationFunctions: AutomationFunction[] = [];
  categories: ServiceCategory[] = [];
  documentTypes: DocumentType[] = [];
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
  categoryFilterTerm = '';
  groupFilterTerm = '';
  situationFilterTerm = '';
  documentPurposeFilters: Record<DocumentPurpose, string> = {
    attachment: '',
    form: '',
    opinion: '',
    evaluation: '',
    generated: '',
    linked_service: ''
  };
  activeDocumentPurpose: DocumentPurpose = 'attachment';
  isSituationFormVisible = false;
  editingSituationId: number | null = null;

  form: ServicePayload = this.createEmptyForm();
  situationDraft: ServiceSituationDraft = this.createEmptySituationDraft();
  hookDraft: ServiceHookDraft = this.createEmptyHookDraft();
  hookEvents = [
    { value: 'before_request_create', label: 'Antes de criar solicitação' },
    { value: 'after_request_create', label: 'Depois de criar solicitação' }
  ];
  documentPurposeTabs: { value: DocumentPurpose; label: string }[] = [
    { value: 'attachment', label: 'Anexos' },
    { value: 'form', label: 'Formulários' },
    { value: 'opinion', label: 'Pareceres' },
    { value: 'evaluation', label: 'Avaliações' },
    { value: 'generated', label: 'Gerados' },
    { value: 'linked_service', label: 'Serviços vinculados' }
  ];

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private readonly serviceService: ServiceService,
    private readonly automationFunctionService: AutomationFunctionService,
    private readonly serviceCategoryService: ServiceCategoryService,
    private readonly documentTypeService: DocumentTypeService,
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

  get isEditingSituation(): boolean {
    return this.editingSituationId !== null;
  }

  get filteredCategories(): ServiceCategory[] {
    const filter = this.categoryFilterTerm.trim().toLowerCase();
    const categories = [...this.categories].sort((first, second) => {
      const order = first.display_order - second.display_order;
      return order || first.name.localeCompare(second.name, 'pt-BR');
    });

    if (!filter) {
      return categories;
    }

    return categories.filter((category) =>
      [
        category.name,
        category.description,
        category.parent_category_name || ''
      ].join(' ').toLowerCase().includes(filter)
    );
  }

  get filteredGroups(): UserGroup[] {
    const filter = this.groupFilterTerm.trim().toLowerCase();
    const groups = [...this.groups].sort((first, second) =>
      first.name.localeCompare(second.name, 'pt-BR')
    );

    if (!filter) {
      return groups;
    }

    return groups.filter((group) =>
      [
        group.name,
        group.description,
        group.parent_group_name || '',
        group.manager_name || '',
        group.manager_email || ''
      ].join(' ').toLowerCase().includes(filter)
    );
  }

  get availablePreviousSituations(): ServiceSituation[] {
    return this.form.situations.filter((situation) => situation.id !== this.editingSituationId);
  }

  get filteredSituations(): ServiceSituation[] {
    const filter = this.situationFilterTerm.trim().toLowerCase();
    const situations = [...this.form.situations].sort(
      (first, second) => first.display_order - second.display_order
    );

    if (!filter) {
      return situations;
    }

    return situations.filter((situation) => {
      const content = [
        situation.display_order,
        situation.name,
        this.previousSituationName(situation.previous_situation_id),
        this.responsibleGroupName(situation.responsible_group_id),
        this.documentTypeNames(situation.document_type_ids || []),
        situation.is_initial ? 'inicial' : '',
        situation.is_final ? 'final' : '',
        situation.requires_opinion ? 'parecer' : '',
        situation.requires_attachment ? 'anexo' : ''
      ].join(' ');

      return content.toLowerCase().includes(filter);
    });
  }

  loadReferenceData(): void {
    forkJoin({
      automationFunctions: this.automationFunctionService.list(),
      categories: this.serviceCategoryService.list(),
      documentTypes: this.documentTypeService.list(),
      groups: this.userGroupService.list()
    }).subscribe({
      next: ({ automationFunctions, categories, documentTypes, groups }) => {
        this.automationFunctions = automationFunctions.filter((item) => item.active);
        this.categories = categories;
        this.documentTypes = documentTypes.filter((documentType) => documentType.active);
        this.groups = groups;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar categorias, documentos e unidades.';
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
      situations: service.situations.map((situation) => ({
        ...situation,
        document_type_ids: [...(situation.document_type_ids || [])]
      })),
      hooks: (service.hooks || []).map((hook) => ({
        ...hook,
        config: { ...(hook.config || {}) }
      }))
    };
    this.situationDraft = this.createEmptySituationDraft();
    this.hookDraft = this.createEmptyHookDraft();
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

  toggleDraftDocumentType(documentTypeId: number, checked: boolean): void {
    this.situationDraft.document_type_ids = this.toggleId(
      this.situationDraft.document_type_ids,
      documentTypeId,
      checked
    );
  }

  toggleSituationDocumentType(
    situation: ServiceSituation,
    documentTypeId: number,
    checked: boolean
  ): void {
    this.form.situations = this.form.situations.map((item) => {
      if (item.id !== situation.id) {
        return item;
      }

      return {
        ...item,
        document_type_ids: this.toggleId(item.document_type_ids || [], documentTypeId, checked)
      };
    });
  }

  createSituation(): void {
    this.editingSituationId = null;
    this.situationDraft = {
      ...this.createEmptySituationDraft(),
      is_initial: !this.form.situations.length,
      display_order: this.form.situations.length + 1
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isSituationFormVisible = true;
  }

  editSituation(situation: ServiceSituation): void {
    this.editingSituationId = situation.id;
    this.situationDraft = {
      ...situation,
      document_type_ids: [...(situation.document_type_ids || [])]
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isSituationFormVisible = true;
  }

  saveSituation(): void {
    if (!this.situationDraft.name.trim()) {
      this.errorMessage = 'Informe o nome da situacao.';
      return;
    }

    const otherSituations = this.form.situations.filter(
      (situation) => situation.id !== this.editingSituationId
    );
    const shouldBeInitial = !otherSituations.length || this.situationDraft.is_initial;
    const situation: ServiceSituation = {
      id: this.editingSituationId || this.nextSituationId(),
      name: this.situationDraft.name.trim(),
      previous_situation_id: shouldBeInitial ? null : this.situationDraft.previous_situation_id,
      responsible_group_id: this.situationDraft.responsible_group_id || null,
      is_initial: shouldBeInitial,
      is_final: this.situationDraft.is_final,
      requires_opinion: this.situationDraft.requires_opinion,
      requires_attachment: this.situationDraft.requires_attachment,
      document_type_ids: [...this.situationDraft.document_type_ids],
      display_order: Number(this.situationDraft.display_order) || otherSituations.length + 1
    };

    if (situation.is_initial) {
      this.form.situations = this.form.situations.map((situation) => ({
        ...situation,
        is_initial: false
      }));
    }

    const existingSituation = this.form.situations.some((item) => item.id === situation.id);
    this.form.situations = existingSituation
      ? this.form.situations.map((item) => item.id === situation.id ? situation : item)
      : [...this.form.situations, situation];
    this.form.situations = this.form.situations
      .sort((first, second) => first.display_order - second.display_order)
      .map((item, index) => ({
        ...item,
        display_order: index + 1
      }));
    this.closeSituationForm();
    this.errorMessage = '';
  }

  closeSituationForm(): void {
    this.editingSituationId = null;
    this.situationDraft = this.createEmptySituationDraft();
    this.errorMessage = '';
    this.isSituationFormVisible = false;
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

  addHook(): void {
    if (!this.hookDraft.event_name) {
      this.errorMessage = 'Informe o evento da automacao.';
      return;
    }

    if (!this.hookDraft.function_id && !this.hookDraft.handler_key.trim()) {
      this.errorMessage = 'Selecione uma function ou informe uma chave de handler.';
      return;
    }

    const config = this.parseHookConfig(this.hookDraft.config_text);

    if (config === null) {
      return;
    }

    const newHook: ServiceHook = {
      id: this.nextHookId(),
      function_id: this.hookDraft.function_id || null,
      function_name: this.functionName(this.hookDraft.function_id),
      event_name: this.hookDraft.event_name,
      handler_key: this.hookDraft.handler_key.trim(),
      config,
      execution_order: Number(this.hookDraft.execution_order) || this.form.hooks.length + 1,
      active: this.hookDraft.active
    };

    this.form.hooks = [...this.form.hooks, newHook].sort(
      (first, second) => first.execution_order - second.execution_order
    );
    this.hookDraft = this.createEmptyHookDraft();
    this.errorMessage = '';
  }

  removeHook(hook: ServiceHook): void {
    this.form.hooks = this.form.hooks.filter((item) => item.id !== hook.id);
  }

  toggleHookStatus(hook: ServiceHook): void {
    this.form.hooks = this.form.hooks.map((item) => {
      if (item.id !== hook.id) {
        return item;
      }

      return {
        ...item,
        active: !item.active
      };
    });
  }

  resetForm(): void {
    this.editingServiceId = null;
    this.form = this.createEmptyForm();
    this.situationFilterTerm = '';
    this.isSituationFormVisible = false;
    this.editingSituationId = null;
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

  documentTypeNames(documentTypeIds: number[]): string {
    const names = this.documentTypes
      .filter((documentType) => documentTypeIds.includes(documentType.id))
      .map((documentType) => documentType.name);

    return names.length ? names.join(', ') : '-';
  }

  documentTypesByIds(documentTypeIds: number[]): DocumentType[] {
    return this.documentTypes.filter((documentType) => documentTypeIds.includes(documentType.id));
  }

  documentTypesByPurpose(purpose: DocumentPurpose): DocumentType[] {
    const filter = this.documentPurposeFilters[purpose].trim().toLowerCase();
    const items = this.documentTypes
      .filter((documentType) => documentType.purpose === purpose)
      .sort((first, second) => first.name.localeCompare(second.name, 'pt-BR'));

    if (!filter) {
      return items;
    }

    return items.filter((documentType) =>
      [
        documentType.name,
        documentType.code,
        documentType.description,
        documentType.allowed_formats
      ].join(' ').toLowerCase().includes(filter)
    );
  }

  setActiveDocumentPurpose(purpose: DocumentPurpose): void {
    this.activeDocumentPurpose = purpose;
  }

  eventLabel(eventName: string): string {
    return this.hookEvents.find((event) => event.value === eventName)?.label || eventName;
  }

  functionName(functionId: number | null): string {
    if (!functionId) {
      return '-';
    }

    return this.automationFunctions.find((item) => item.id === functionId)?.name || '-';
  }

  configPreview(config: Record<string, unknown>): string {
    const value = JSON.stringify(config || {});

    return value.length > 90 ? `${value.slice(0, 87)}...` : value;
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
        document_type_ids: [...(situation.document_type_ids || [])],
        display_order: index + 1
      })),
      hooks: this.form.hooks.map((hook, index) => ({
        ...hook,
        function_name: hook.function_name || this.functionName(hook.function_id),
        function_id: hook.function_id || null,
        handler_key: (hook.handler_key || '').trim(),
        config: hook.config || {},
        execution_order: Number(hook.execution_order) || index + 1,
        active: hook.active
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
      situations: [],
      hooks: []
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
      document_type_ids: [],
      display_order: 0
    };
  }

  private createEmptyHookDraft(): ServiceHookDraft {
    return {
      function_id: null,
      event_name: 'before_request_create',
      handler_key: '',
      config: {},
      config_text: '{\n  "connection": "db2_guri"\n}',
      execution_order: 0,
      active: true
    };
  }

  private nextSituationId(): number {
    if (!this.form.situations.length) {
      return 1;
    }

    return Math.max(...this.form.situations.map((situation) => situation.id)) + 1;
  }

  private nextHookId(): number {
    if (!this.form.hooks.length) {
      return 1;
    }

    return Math.max(...this.form.hooks.map((hook) => hook.id)) + 1;
  }

  private parseHookConfig(value: string): Record<string, unknown> | null {
    const trimmedValue = value.trim();

    if (!trimmedValue) {
      return {};
    }

    try {
      const parsedValue = JSON.parse(trimmedValue);

      if (!parsedValue || Array.isArray(parsedValue) || typeof parsedValue !== 'object') {
        this.errorMessage = 'A configuracao da automacao deve ser um objeto JSON.';
        return null;
      }

      return parsedValue;
    } catch {
      this.errorMessage = 'A configuracao da automacao nao esta em um JSON valido.';
      return null;
    }
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
