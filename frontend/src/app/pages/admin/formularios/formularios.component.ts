import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';

import {
  FormTemplate,
  FormTemplatePayload,
  TemplateExecutionMode,
  TemplateField
} from '../../../core/models/form-template';
import { FormTemplateService } from '../../../core/services/form-template.service';

@Component({
  selector: 'app-formularios',
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
  templateUrl: './formularios.component.html',
  styleUrl: './formularios.component.scss'
})
export class FormulariosComponent implements OnInit, AfterViewInit {
  dataSource = new MatTableDataSource<FormTemplate>([]);
  displayedColumns = ['name', 'execution_mode', 'fields', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingTemplateId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';
  fieldsJson = '[]';

  readonly executionModeOptions: { value: TemplateExecutionMode; label: string }[] = [
    { value: 'dynamic', label: 'Dinâmico' },
    { value: 'custom', label: 'Customizado' }
  ];

  form: FormTemplatePayload = this.createEmptyForm();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(private readonly formTemplateService: FormTemplateService) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingTemplateId !== null;
  }

  loadTemplates(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.formTemplateService.list().subscribe({
      next: (templates) => {
        this.dataSource.data = templates;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os formularios.';
        this.isLoading = false;
      }
    });
  }

  saveTemplate(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome do formulario.';
      return;
    }

    const fields = this.parseFieldsJson();
    if (fields === null) {
      return;
    }

    if (!this.form.slug.trim()) {
      this.form.slug = this.slugify(this.form.name);
    }

    const payload: FormTemplatePayload = {
      name: this.form.name.trim(),
      slug: this.slugify(this.form.slug),
      description: this.form.description.trim(),
      execution_mode: this.form.execution_mode,
      fields_schema: fields,
      active: this.form.active
    };

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.formTemplateService.update(this.editingTemplateId as number, payload)
      : this.formTemplateService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Formulario atualizado com sucesso.'
          : 'Formulario cadastrado com sucesso.';
        this.closeForm();
        this.loadTemplates();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar o formulario.';
        this.isSaving = false;
      }
    });
  }

  editTemplate(template: FormTemplate): void {
    this.editingTemplateId = template.id;
    this.form = {
      name: template.name,
      slug: template.slug,
      description: template.description,
      execution_mode: template.execution_mode,
      fields_schema: template.fields_schema,
      active: template.active
    };
    this.fieldsJson = JSON.stringify(template.fields_schema || [], null, 2);
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
  }

  createTemplate(): void {
    this.resetForm();
    this.isFormVisible = true;
  }

  toggleTemplateStatus(template: FormTemplate): void {
    this.formTemplateService.update(template.id, {
      ...template,
      active: !template.active
    }).subscribe({
      next: () => this.loadTemplates(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteTemplate(template: FormTemplate): void {
    const confirmed = window.confirm(`Remover o formulario ${template.name}?`);

    if (!confirmed) {
      return;
    }

    this.formTemplateService.delete(template.id).subscribe({
      next: () => {
        this.successMessage = 'Formulario removido com sucesso.';
        this.loadTemplates();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover o formulario.';
      }
    });
  }

  applyFilter(value: string): void {
    this.filterTerm = value;
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  executionModeLabel(mode: TemplateExecutionMode): string {
    return this.executionModeOptions.find((option) => option.value === mode)?.label || mode;
  }

  syncSlugFromName(): void {
    if (this.isEditing || this.form.slug.trim()) {
      return;
    }

    this.form.slug = this.slugify(this.form.name);
  }

  resetForm(): void {
    this.editingTemplateId = null;
    this.form = this.createEmptyForm();
    this.fieldsJson = '[]';
  }

  closeForm(): void {
    this.resetForm();
    this.errorMessage = '';
    this.isFormVisible = false;
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (template, filter) => (
      `${template.name} ${template.slug} ${template.description} ${this.executionModeLabel(template.execution_mode)}`
        .toLowerCase()
        .includes(filter)
    );
  }

  private parseFieldsJson(): TemplateField[] | null {
    try {
      const fields = JSON.parse(this.fieldsJson || '[]');

      if (!Array.isArray(fields)) {
        this.errorMessage = 'Informe os campos como uma lista JSON.';
        return null;
      }

      return fields;
    } catch {
      this.errorMessage = 'JSON dos campos invalido.';
      return null;
    }
  }

  private createEmptyForm(): FormTemplatePayload {
    return {
      name: '',
      slug: '',
      description: '',
      execution_mode: 'dynamic',
      fields_schema: [],
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
