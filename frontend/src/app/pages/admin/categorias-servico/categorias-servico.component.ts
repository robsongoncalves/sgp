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
  ServiceCategory,
  ServiceCategoryPayload
} from '../../../core/models/service-category';
import { ServiceCategoryService } from '../../../core/services/service-category.service';

@Component({
  selector: 'app-categorias-servico',
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
  templateUrl: './categorias-servico.component.html',
  styleUrl: './categorias-servico.component.scss'
})
export class CategoriasServicoComponent implements OnInit, AfterViewInit {
  categories: ServiceCategory[] = [];
  dataSource = new MatTableDataSource<ServiceCategory>([]);
  displayedColumns = ['display_order', 'name', 'parent_category_name', 'description', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingCategoryId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';

  form: ServiceCategoryPayload = this.createEmptyForm();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(private readonly serviceCategoryService: ServiceCategoryService) {}

  ngOnInit(): void {
    this.loadCategories();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingCategoryId !== null;
  }

  get availableParentCategories(): ServiceCategory[] {
    return this.categories.filter((category) => category.id !== this.editingCategoryId);
  }

  loadCategories(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.serviceCategoryService.list().subscribe({
      next: (categories) => {
        this.categories = categories;
        this.dataSource.data = categories;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar as categorias.';
        this.isLoading = false;
      }
    });
  }

  saveCategory(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome da categoria.';
      return;
    }

    const payload: ServiceCategoryPayload = {
      name: this.form.name.trim(),
      description: this.form.description.trim(),
      parent_category_id: this.form.parent_category_id,
      display_order: Number(this.form.display_order) || 0,
      show_on_main_menu: this.form.show_on_main_menu,
      active: this.form.active
    };

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.serviceCategoryService.update(this.editingCategoryId as number, payload)
      : this.serviceCategoryService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Categoria atualizada com sucesso.'
          : 'Categoria cadastrada com sucesso.';
        this.closeForm();
        this.loadCategories();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar a categoria.';
        this.isSaving = false;
      }
    });
  }

  editCategory(category: ServiceCategory): void {
    this.editingCategoryId = category.id;
    this.form = {
      name: category.name,
      description: category.description,
      parent_category_id: category.parent_category_id,
      display_order: category.display_order,
      show_on_main_menu: category.show_on_main_menu,
      active: category.active
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
  }

  createCategory(): void {
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

  toggleCategoryStatus(category: ServiceCategory): void {
    this.serviceCategoryService.update(category.id, {
      name: category.name,
      description: category.description,
      parent_category_id: category.parent_category_id,
      display_order: category.display_order,
      show_on_main_menu: category.show_on_main_menu,
      active: !category.active
    }).subscribe({
      next: () => this.loadCategories(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteCategory(category: ServiceCategory): void {
    const confirmed = window.confirm(`Remover a categoria ${category.name}?`);

    if (!confirmed) {
      return;
    }

    this.serviceCategoryService.delete(category.id).subscribe({
      next: () => {
        this.successMessage = 'Categoria removida com sucesso.';
        this.loadCategories();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover a categoria.';
      }
    });
  }

  resetForm(): void {
    this.editingCategoryId = null;
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
    this.dataSource.filterPredicate = (category, filter) => {
      const content = [
        category.display_order,
        category.name,
        category.parent_category_name || '',
        category.description,
        category.show_on_main_menu ? 'menu principal' : '',
        category.active ? 'ativo' : 'inativo'
      ].join(' ');

      return content.toLowerCase().includes(filter);
    };
  }

  private createEmptyForm(): ServiceCategoryPayload {
    return {
      name: '',
      description: '',
      parent_category_id: null,
      display_order: this.categories.length + 1,
      show_on_main_menu: false,
      active: true
    };
  }
}
