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

import { TemplateExecutionMode, TemplateField } from '../../../core/models/form-template';
import { OpinionTemplate, OpinionTemplatePayload } from '../../../core/models/opinion-template';
import { UserGroup } from '../../../core/models/user-group';
import { OpinionTemplateService } from '../../../core/services/opinion-template.service';
import { UserGroupService } from '../../../core/services/user-group.service';

@Component({
  selector: 'app-modelos-parecer',
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
  templateUrl: './modelos-parecer.component.html',
  styleUrl: './modelos-parecer.component.scss'
})
export class ModelosParecerComponent implements OnInit, AfterViewInit {
  groups: UserGroup[] = [];
  dataSource = new MatTableDataSource<OpinionTemplate>([]);
  displayedColumns = ['name', 'execution_mode', 'group', 'rules', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingTemplateId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';
  decisionOptionsText = 'aprovado\nindeferido\ndiligencia';
  fieldsJson = '[]';

  readonly executionModeOptions: { value: TemplateExecutionMode; label: string }[] = [
    { value: 'dynamic', label: 'Dinâmico' },
    { value: 'custom', label: 'Customizado' }
  ];

  form: OpinionTemplatePayload = this.createEmptyForm();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private readonly opinionTemplateService: OpinionTemplateService,
    private readonly userGroupService: UserGroupService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingTemplateId !== null;
  }

  loadData(): void {
    this.isLoading = true;
    this.errorMessage = '';

    forkJoin({
      templates: this.opinionTemplateService.list(),
      groups: this.userGroupService.list()
    }).subscribe({
      next: ({ templates, groups }) => {
        this.groups = groups;
        this.dataSource.data = templates;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os modelos de parecer.';
        this.isLoading = false;
      }
    });
  }

  saveTemplate(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome do modelo de parecer.';
      return;
    }

    const fields = this.parseFieldsJson();
    if (fields === null) {
      return;
    }

    if (!this.form.slug.trim()) {
      this.form.slug = this.slugify(this.form.name);
    }

    const payload: OpinionTemplatePayload = {
      name: this.form.name.trim(),
      slug: this.slugify(this.form.slug),
      description: this.form.description.trim(),
      execution_mode: this.form.execution_mode,
      default_responsible_group_id: this.form.default_responsible_group_id || null,
      decision_options: this.decisionOptionsText
        .split('\n')
        .map((option) => option.trim())
        .filter(Boolean),
      fields_schema: fields,
      requires_justification: this.form.requires_justification,
      requires_signature: this.form.requires_signature,
      allow_attachments: this.form.allow_attachments,
      active: this.form.active
    };

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.opinionTemplateService.update(this.editingTemplateId as number, payload)
      : this.opinionTemplateService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Modelo de parecer atualizado com sucesso.'
          : 'Modelo de parecer cadastrado com sucesso.';
        this.closeForm();
        this.loadData();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar o modelo de parecer.';
        this.isSaving = false;
      }
    });
  }

  editTemplate(template: OpinionTemplate): void {
    this.editingTemplateId = template.id;
    this.form = {
      name: template.name,
      slug: template.slug,
      description: template.description,
      execution_mode: template.execution_mode,
      default_responsible_group_id: template.default_responsible_group_id,
      decision_options: template.decision_options,
      fields_schema: template.fields_schema,
      requires_justification: template.requires_justification,
      requires_signature: template.requires_signature,
      allow_attachments: template.allow_attachments,
      active: template.active
    };
    this.decisionOptionsText = template.decision_options.join('\n');
    this.fieldsJson = JSON.stringify(template.fields_schema || [], null, 2);
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
  }

  createTemplate(): void {
    this.resetForm();
    this.isFormVisible = true;
  }

  toggleTemplateStatus(template: OpinionTemplate): void {
    this.opinionTemplateService.update(template.id, {
      ...template,
      active: !template.active
    }).subscribe({
      next: () => this.loadData(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteTemplate(template: OpinionTemplate): void {
    const confirmed = window.confirm(`Remover o modelo de parecer ${template.name}?`);

    if (!confirmed) {
      return;
    }

    this.opinionTemplateService.delete(template.id).subscribe({
      next: () => {
        this.successMessage = 'Modelo de parecer removido com sucesso.';
        this.loadData();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover o modelo de parecer.';
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
    this.decisionOptionsText = 'aprovado\nindeferido\ndiligencia';
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
      `${template.name} ${template.slug} ${template.description} ${template.default_responsible_group_name}`
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

  private createEmptyForm(): OpinionTemplatePayload {
    return {
      name: '',
      slug: '',
      description: '',
      execution_mode: 'dynamic',
      default_responsible_group_id: null,
      decision_options: ['aprovado', 'indeferido', 'diligencia'],
      fields_schema: [],
      requires_justification: true,
      requires_signature: true,
      allow_attachments: true,
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
