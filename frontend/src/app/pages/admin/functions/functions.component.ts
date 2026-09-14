import {
  AfterViewChecked,
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  ViewChild
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { python } from '@codemirror/lang-python';
import { EditorView, keymap, lineNumbers } from '@codemirror/view';
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands';
import { bracketMatching, defaultHighlightStyle, indentOnInput, syntaxHighlighting } from '@codemirror/language';
import { closeBrackets, closeBracketsKeymap } from '@codemirror/autocomplete';
import { highlightSelectionMatches, searchKeymap } from '@codemirror/search';

import {
  AutomationFunction,
  AutomationFunctionPayload
} from '../../../core/models/automation-function';
import { AutomationFunctionService } from '../../../core/services/automation-function.service';

@Component({
  selector: 'app-functions',
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
  templateUrl: './functions.component.html',
  styleUrl: './functions.component.scss'
})
export class FunctionsComponent implements OnInit, AfterViewInit, AfterViewChecked, OnDestroy {
  functions: AutomationFunction[] = [];
  dataSource = new MatTableDataSource<AutomationFunction>([]);
  displayedColumns = ['name', 'language', 'timeout_seconds', 'status', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingFunctionId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';

  form: AutomationFunctionPayload = this.createEmptyForm();

  @ViewChild('codeEditor') codeEditor?: ElementRef<HTMLDivElement>;
  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  private editor?: EditorView;

  constructor(private readonly automationFunctionService: AutomationFunctionService) {}

  ngOnInit(): void {
    this.loadFunctions();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  ngAfterViewChecked(): void {
    if (this.isFormVisible && this.codeEditor && !this.editor) {
      this.createCodeEditor();
    }
  }

  ngOnDestroy(): void {
    this.destroyCodeEditor();
  }

  get isEditing(): boolean {
    return this.editingFunctionId !== null;
  }

  loadFunctions(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.automationFunctionService.list().subscribe({
      next: (functions) => {
        this.functions = functions;
        this.dataSource.data = functions;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar as functions.';
        this.isLoading = false;
      }
    });
  }

  saveFunction(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome da function.';
      return;
    }

    if (!this.form.slug.trim()) {
      this.form.slug = this.slugify(this.form.name);
    }

    if (!this.form.source_code.trim()) {
      this.errorMessage = 'Informe o codigo Python da function.';
      return;
    }

    const payload: AutomationFunctionPayload = {
      name: this.form.name.trim(),
      slug: this.slugify(this.form.slug),
      description: this.form.description.trim(),
      language: 'python',
      source_code: this.form.source_code,
      timeout_seconds: Number(this.form.timeout_seconds) || 10,
      active: this.form.active
    };

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.automationFunctionService.update(this.editingFunctionId as number, payload)
      : this.automationFunctionService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Function atualizada com sucesso.'
          : 'Function cadastrada com sucesso.';
        this.closeForm();
        this.loadFunctions();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar a function.';
        this.isSaving = false;
      }
    });
  }

  editFunction(functionItem: AutomationFunction): void {
    this.editingFunctionId = functionItem.id;
    this.form = {
      name: functionItem.name,
      slug: functionItem.slug,
      description: functionItem.description,
      language: 'python',
      source_code: functionItem.source_code,
      timeout_seconds: functionItem.timeout_seconds,
      active: functionItem.active
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
    this.destroyCodeEditor();
  }

  createFunction(): void {
    this.resetForm();
    this.isFormVisible = true;
    this.destroyCodeEditor();
  }

  applyFilter(value: string): void {
    this.filterTerm = value;
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  toggleFunctionStatus(functionItem: AutomationFunction): void {
    this.automationFunctionService.update(functionItem.id, {
      ...functionItem,
      active: !functionItem.active
    }).subscribe({
      next: () => this.loadFunctions(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteFunction(functionItem: AutomationFunction): void {
    const confirmed = window.confirm(`Remover a function ${functionItem.name}?`);

    if (!confirmed) {
      return;
    }

    this.automationFunctionService.delete(functionItem.id).subscribe({
      next: () => {
        this.successMessage = 'Function removida com sucesso.';
        this.loadFunctions();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover a function.';
      }
    });
  }

  syncSlugFromName(): void {
    if (this.isEditing || this.form.slug.trim()) {
      return;
    }

    this.form.slug = this.slugify(this.form.name);
  }

  resetForm(): void {
    this.editingFunctionId = null;
    this.form = this.createEmptyForm();
  }

  closeForm(): void {
    this.destroyCodeEditor();
    this.resetForm();
    this.errorMessage = '';
    this.isFormVisible = false;
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (functionItem, filter) => {
      const content = [
        functionItem.name,
        functionItem.slug,
        functionItem.description,
        functionItem.language,
        functionItem.active ? 'ativa' : 'inativa'
      ].join(' ');

      return content.toLowerCase().includes(filter);
    };
  }

  private createEmptyForm(): AutomationFunctionPayload {
    return {
      name: '',
      slug: '',
      description: '',
      language: 'python',
      source_code: 'def handle(context):\n    return {\n        "form_data_patch": {},\n        "messages": [],\n        "warnings": []\n    }\n',
      timeout_seconds: 10,
      active: true
    };
  }

  private createCodeEditor(): void {
    if (!this.codeEditor) {
      return;
    }

    this.editor = new EditorView({
      doc: this.form.source_code,
      parent: this.codeEditor.nativeElement,
      extensions: [
        lineNumbers(),
        history(),
        indentOnInput(),
        bracketMatching(),
        closeBrackets(),
        highlightSelectionMatches(),
        python(),
        syntaxHighlighting(defaultHighlightStyle),
        keymap.of([
          indentWithTab,
          ...closeBracketsKeymap,
          ...defaultKeymap,
          ...historyKeymap,
          ...searchKeymap
        ]),
        EditorView.lineWrapping,
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            this.form.source_code = update.state.doc.toString();
          }
        }),
        EditorView.theme({
          '&': {
            minHeight: '360px',
            border: '1px solid #aab3c2',
            borderRadius: '6px',
            overflow: 'hidden',
            backgroundColor: '#fbfcff'
          },
          '&.cm-focused': {
            outline: '0',
            borderColor: '#0b57d0',
            boxShadow: '0 0 0 3px rgba(11, 87, 208, 0.12)'
          },
          '.cm-scroller': {
            minHeight: '360px',
            fontFamily: '"Roboto Mono", "Courier New", monospace',
            fontSize: '0.9rem',
            lineHeight: '1.45'
          },
          '.cm-gutters': {
            backgroundColor: '#eef2f7',
            color: '#687386',
            borderRight: '1px solid #d8dde6'
          },
          '.cm-activeLineGutter, .cm-activeLine': {
            backgroundColor: '#eef6ff'
          },
          '.cm-content': {
            padding: '10px 0'
          },
          '.cm-line': {
            padding: '0 12px'
          }
        })
      ]
    });
  }

  private destroyCodeEditor(): void {
    this.editor?.destroy();
    this.editor = undefined;
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
