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

import {
  DocumentOrigin,
  DocumentPurpose,
  DocumentType,
  DocumentTypePayload
} from '../../../core/models/document-type';
import { FormTemplate } from '../../../core/models/form-template';
import { OpinionTemplate } from '../../../core/models/opinion-template';
import { Service } from '../../../core/models/service';
import { DocumentTypeService } from '../../../core/services/document-type.service';
import { FormTemplateService } from '../../../core/services/form-template.service';
import { OpinionTemplateService } from '../../../core/services/opinion-template.service';
import { ServiceService } from '../../../core/services/service.service';

@Component({
  selector: 'app-tipos-documentos',
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
  templateUrl: './tipos-documentos.component.html',
  styleUrl: './tipos-documentos.component.scss'
})
export class TiposDocumentosComponent implements OnInit, AfterViewInit {
  documentTypes: DocumentType[] = [];
  formTemplates: FormTemplate[] = [];
  opinionTemplates: OpinionTemplate[] = [];
  services: Service[] = [];
  dataSource = new MatTableDataSource<DocumentType>([]);
  displayedColumns = ['name', 'origin', 'purpose', 'template', 'rules', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingDocumentTypeId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';

  readonly originOptions: { value: DocumentOrigin; label: string }[] = [
    { value: 'requester', label: 'Solicitante' },
    { value: 'responsible_group', label: 'Unidade responsável' },
    { value: 'system', label: 'Gerado pelo sistema' },
    { value: 'external', label: 'Externo' }
  ];

  readonly purposeOptions: { value: DocumentPurpose; label: string }[] = [
    { value: 'attachment', label: 'Anexo' },
    { value: 'form', label: 'Formulário' },
    { value: 'opinion', label: 'Parecer' },
    { value: 'evaluation', label: 'Avaliação' },
    { value: 'generated', label: 'Gerado pelo sistema' },
    { value: 'linked_service', label: 'Serviço vinculado' }
  ];

  form: DocumentTypePayload = this.createEmptyForm();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private readonly documentTypeService: DocumentTypeService,
    private readonly formTemplateService: FormTemplateService,
    private readonly opinionTemplateService: OpinionTemplateService,
    private readonly serviceService: ServiceService
  ) {}

  ngOnInit(): void {
    this.loadDocumentTypes();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingDocumentTypeId !== null;
  }

  loadDocumentTypes(): void {
    this.isLoading = true;
    this.errorMessage = '';

    forkJoin({
      documentTypes: this.documentTypeService.list(),
      formTemplates: this.formTemplateService.list(),
      opinionTemplates: this.opinionTemplateService.list(),
      services: this.serviceService.list()
    }).subscribe({
      next: ({ documentTypes, formTemplates, opinionTemplates, services }) => {
        this.documentTypes = documentTypes;
        this.formTemplates = formTemplates;
        this.opinionTemplates = opinionTemplates;
        this.services = services.filter((service) => service.active);
        this.dataSource.data = documentTypes;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os tipos de documentos.';
        this.isLoading = false;
      }
    });
  }

  saveDocumentType(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome do tipo de documento.';
      return;
    }

    if (!this.form.code.trim()) {
      this.form.code = this.slugify(this.form.name);
    }

    const payload: DocumentTypePayload = {
      name: this.form.name.trim(),
      code: this.slugify(this.form.code),
      description: this.form.description.trim(),
      origin: this.form.origin,
      purpose: this.form.purpose,
      module_slug: this.form.module_slug.trim(),
      form_template_id: this.form.form_template_id || null,
      opinion_template_id: this.form.opinion_template_id || null,
      linked_service_id: this.form.linked_service_id || null,
      linked_service_required_status: this.form.linked_service_required_status.trim(),
      allowed_formats: this.form.allowed_formats.trim() || 'PDF',
      required_by_default: this.form.required_by_default,
      allow_multiple_files: this.form.allow_multiple_files,
      active: this.form.active
    };

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.documentTypeService.update(this.editingDocumentTypeId as number, payload)
      : this.documentTypeService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Tipo de documento atualizado com sucesso.'
          : 'Tipo de documento cadastrado com sucesso.';
        this.closeForm();
        this.loadDocumentTypes();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar o tipo de documento.';
        this.isSaving = false;
      }
    });
  }

  editDocumentType(documentType: DocumentType): void {
    this.editingDocumentTypeId = documentType.id;
    this.form = {
      name: documentType.name,
      code: documentType.code,
      description: documentType.description,
      origin: documentType.origin,
      purpose: documentType.purpose,
      module_slug: documentType.module_slug,
      form_template_id: documentType.form_template_id,
      opinion_template_id: documentType.opinion_template_id,
      linked_service_id: documentType.linked_service_id,
      linked_service_required_status: documentType.linked_service_required_status,
      allowed_formats: documentType.allowed_formats,
      required_by_default: documentType.required_by_default,
      allow_multiple_files: documentType.allow_multiple_files,
      active: documentType.active
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
  }

  createDocumentType(): void {
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

  toggleDocumentTypeStatus(documentType: DocumentType): void {
    this.documentTypeService.update(documentType.id, {
      ...documentType,
      active: !documentType.active
    }).subscribe({
      next: () => this.loadDocumentTypes(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteDocumentType(documentType: DocumentType): void {
    const confirmed = window.confirm(`Remover o tipo de documento ${documentType.name}?`);

    if (!confirmed) {
      return;
    }

    this.documentTypeService.delete(documentType.id).subscribe({
      next: () => {
        this.successMessage = 'Tipo de documento removido com sucesso.';
        this.loadDocumentTypes();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover o tipo de documento.';
      }
    });
  }

  originLabel(origin: DocumentOrigin): string {
    return this.originOptions.find((option) => option.value === origin)?.label || origin;
  }

  purposeLabel(purpose: DocumentPurpose): string {
    return this.purposeOptions.find((option) => option.value === purpose)?.label || purpose;
  }

  templateLabel(documentType: DocumentType): string {
    return documentType.linked_service_name
      || documentType.form_template_name
      || documentType.opinion_template_name
      || documentType.module_slug
      || '-';
  }

  syncCodeFromName(): void {
    if (this.isEditing || this.form.code.trim()) {
      return;
    }

    this.form.code = this.slugify(this.form.name);
  }

  resetForm(): void {
    this.editingDocumentTypeId = null;
    this.form = this.createEmptyForm();
  }

  closeForm(): void {
    this.resetForm();
    this.errorMessage = '';
    this.isFormVisible = false;
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (documentType, filter) => {
      const content = [
        documentType.name,
        documentType.code,
        documentType.description,
        this.originLabel(documentType.origin),
        this.purposeLabel(documentType.purpose),
        this.templateLabel(documentType),
        documentType.allowed_formats,
        documentType.required_by_default ? 'obrigatorio' : '',
        documentType.allow_multiple_files ? 'multiplos' : '',
        documentType.active ? 'ativo' : 'inativo'
      ].join(' ');

      return content.toLowerCase().includes(filter);
    };
  }

  private createEmptyForm(): DocumentTypePayload {
    return {
      name: '',
      code: '',
      description: '',
      origin: 'requester',
      purpose: 'attachment',
      module_slug: '',
      form_template_id: null,
      opinion_template_id: null,
      linked_service_id: null,
      linked_service_required_status: '',
      allowed_formats: 'PDF',
      required_by_default: false,
      allow_multiple_files: false,
      active: true
    };
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
