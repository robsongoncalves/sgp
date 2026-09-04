import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';

import { User, UserPayload } from '../../../core/models/user';
import { UserService } from '../../../core/services/user.service';

@Component({
  selector: 'app-usuarios',
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
  templateUrl: './usuarios.component.html',
  styleUrl: './usuarios.component.scss'
})
export class UsuariosComponent implements OnInit, AfterViewInit {
  users: User[] = [];
  dataSource = new MatTableDataSource<User>([]);
  displayedColumns = ['name', 'email', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingUserId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';

  form: UserPayload = this.createEmptyForm();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(private readonly userService: UserService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingUserId !== null;
  }

  loadUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.userService.list().subscribe({
      next: (users) => {
        this.users = users;
        this.dataSource.data = users;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os usuarios.';
        this.isLoading = false;
      }
    });
  }

  saveUser(): void {
    if (!this.form.name.trim() || !this.form.email.trim()) {
      this.errorMessage = 'Informe nome e email para salvar o usuario.';
      return;
    }

    if (!this.isEditing && !this.form.password?.trim()) {
      this.errorMessage = 'Informe a senha para cadastrar o usuario.';
      return;
    }

    const payload: UserPayload = {
      name: this.form.name.trim(),
      email: this.form.email.trim().toLowerCase(),
      active: this.form.active
    };

    if (this.form.password?.trim()) {
      payload.password = this.form.password;
    }

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.userService.update(this.editingUserId as number, payload)
      : this.userService.create(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Usuario atualizado com sucesso.'
          : 'Usuario cadastrado com sucesso.';
        this.closeForm();
        this.loadUsers();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar o usuario.';
        this.isSaving = false;
      }
    });
  }

  editUser(user: User): void {
    this.editingUserId = user.id;
    this.form = {
      name: user.name,
      email: user.email,
      password: '',
      active: user.active
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
  }

  createUser(): void {
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

  toggleUserStatus(user: User): void {
    this.userService.update(user.id, {
      name: user.name,
      email: user.email,
      active: !user.active
    }).subscribe({
      next: () => this.loadUsers(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteUser(user: User): void {
    const confirmed = window.confirm(`Remover o usuario ${user.name}?`);

    if (!confirmed) {
      return;
    }

    this.userService.delete(user.id).subscribe({
      next: () => {
        this.successMessage = 'Usuario removido com sucesso.';
        this.loadUsers();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover o usuario.';
      }
    });
  }

  resetForm(): void {
    this.editingUserId = null;
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
    this.dataSource.filterPredicate = (user, filter) => {
      const content = `${user.name} ${user.email} ${user.active ? 'ativo' : 'inativo'}`;
      return content.toLowerCase().includes(filter);
    };
  }

  private createEmptyForm(): UserPayload {
    return {
      name: '',
      email: '',
      password: '',
      active: true
    };
  }
}
