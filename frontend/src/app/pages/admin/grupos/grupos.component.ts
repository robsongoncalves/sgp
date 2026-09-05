import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { switchMap } from 'rxjs';

import { User } from '../../../core/models/user';
import { UserGroup, UserGroupPayload } from '../../../core/models/user-group';
import { UserService } from '../../../core/services/user.service';
import { UserGroupService } from '../../../core/services/user-group.service';

@Component({
  selector: 'app-grupos',
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
  templateUrl: './grupos.component.html',
  styleUrl: './grupos.component.scss'
})
export class GruposComponent implements OnInit, AfterViewInit {
  groups: UserGroup[] = [];
  dataSource = new MatTableDataSource<UserGroup>([]);
  displayedColumns = ['name', 'description', 'actions'];
  isFormVisible = false;
  filterTerm = '';
  editingGroupId: number | null = null;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';
  allUsers: User[] = [];
  associatedUserIds: number[] = [];
  selectedAvailableUserIds: number[] = [];
  selectedAssociatedUserIds: number[] = [];
  availableUsersFilter = '';
  associatedUsersFilter = '';

  form: UserGroupPayload = this.createEmptyForm();

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private readonly userGroupService: UserGroupService,
    private readonly userService: UserService
  ) {}

  ngOnInit(): void {
    this.loadGroups();
    this.loadUsers();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  get isEditing(): boolean {
    return this.editingGroupId !== null;
  }

  get availableUsers(): User[] {
    const filter = this.availableUsersFilter.trim().toLowerCase();

    return this.allUsers
      .filter((user) => !this.associatedUserIds.includes(user.id))
      .filter((user) => this.matchesUserFilter(user, filter));
  }

  get associatedUsers(): User[] {
    const filter = this.associatedUsersFilter.trim().toLowerCase();

    return this.allUsers
      .filter((user) => this.associatedUserIds.includes(user.id))
      .filter((user) => this.matchesUserFilter(user, filter));
  }

  loadGroups(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.userGroupService.list().subscribe({
      next: (groups) => {
        this.groups = groups;
        this.dataSource.data = groups;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os grupos.';
        this.isLoading = false;
      }
    });
  }

  loadUsers(): void {
    this.userService.list().subscribe({
      next: (users) => {
        this.allUsers = users;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os usuarios para associacao.';
      }
    });
  }

  saveGroup(): void {
    if (!this.form.name.trim()) {
      this.errorMessage = 'Informe o nome do grupo.';
      return;
    }

    const payload: UserGroupPayload = {
      name: this.form.name.trim(),
      description: this.form.description.trim(),
      active: this.form.active
    };

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const request = this.isEditing
      ? this.userGroupService.update(this.editingGroupId as number, payload)
      : this.userGroupService.create(payload);

    request.pipe(
      switchMap((group) =>
        this.userGroupService.updateMemberUserIds(group.id, this.associatedUserIds)
      )
    ).subscribe({
      next: () => {
        this.successMessage = this.isEditing
          ? 'Grupo atualizado com sucesso.'
          : 'Grupo cadastrado com sucesso.';
        this.closeForm();
        this.loadGroups();
        this.isSaving = false;
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel salvar o grupo.';
        this.isSaving = false;
      }
    });
  }

  editGroup(group: UserGroup): void {
    this.editingGroupId = group.id;
    this.form = {
      name: group.name,
      description: group.description,
      active: group.active
    };
    this.errorMessage = '';
    this.successMessage = '';
    this.isFormVisible = true;
    this.loadGroupMembers(group.id);
  }

  createGroup(): void {
    this.resetForm();
    this.clearUserSelection();
    this.isFormVisible = true;
  }

  applyFilter(value: string): void {
    this.filterTerm = value;
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  toggleGroupStatus(group: UserGroup): void {
    this.userGroupService.update(group.id, {
      name: group.name,
      description: group.description,
      active: !group.active
    }).subscribe({
      next: () => this.loadGroups(),
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel alterar o status.';
      }
    });
  }

  deleteGroup(group: UserGroup): void {
    const confirmed = window.confirm(`Remover o grupo ${group.name}?`);

    if (!confirmed) {
      return;
    }

    this.userGroupService.delete(group.id).subscribe({
      next: () => {
        this.successMessage = 'Grupo removido com sucesso.';
        this.loadGroups();
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel remover o grupo.';
      }
    });
  }

  resetForm(): void {
    this.editingGroupId = null;
    this.form = this.createEmptyForm();
    this.clearUserSelection();
  }

  closeForm(): void {
    this.resetForm();
    this.errorMessage = '';
    this.isFormVisible = false;
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (group, filter) => {
      const content = `${group.name} ${group.description} ${group.active ? 'ativo' : 'inativo'}`;
      return content.toLowerCase().includes(filter);
    };
  }

  private createEmptyForm(): UserGroupPayload {
    return {
      name: '',
      description: '',
      active: true
    };
  }

  loadGroupMembers(groupId: number): void {
    this.userGroupService.getMemberUserIds(groupId).subscribe({
      next: (response) => {
        this.associatedUserIds = response.user_ids;
        this.selectedAvailableUserIds = [];
        this.selectedAssociatedUserIds = [];
      },
      error: (response) => {
        this.errorMessage = response?.error?.message || 'Nao foi possivel carregar os usuarios do grupo.';
      }
    });
  }

  toggleAvailableUserSelection(userId: number, checked: boolean): void {
    this.selectedAvailableUserIds = this.toggleSelection(
      this.selectedAvailableUserIds,
      userId,
      checked
    );
  }

  toggleAssociatedUserSelection(userId: number, checked: boolean): void {
    this.selectedAssociatedUserIds = this.toggleSelection(
      this.selectedAssociatedUserIds,
      userId,
      checked
    );
  }

  associateSelectedUsers(): void {
    this.associatedUserIds = [
      ...new Set([
        ...this.associatedUserIds,
        ...this.selectedAvailableUserIds
      ])
    ];
    this.selectedAvailableUserIds = [];
  }

  dissociateSelectedUsers(): void {
    this.associatedUserIds = this.associatedUserIds.filter(
      (userId) => !this.selectedAssociatedUserIds.includes(userId)
    );
    this.selectedAssociatedUserIds = [];
  }

  private clearUserSelection(): void {
    this.associatedUserIds = [];
    this.selectedAvailableUserIds = [];
    this.selectedAssociatedUserIds = [];
    this.availableUsersFilter = '';
    this.associatedUsersFilter = '';
  }

  private toggleSelection(selectedIds: number[], userId: number, checked: boolean): number[] {
    if (checked) {
      return [...new Set([...selectedIds, userId])];
    }

    return selectedIds.filter((selectedId) => selectedId !== userId);
  }

  private matchesUserFilter(user: User, filter: string): boolean {
    if (!filter) {
      return true;
    }

    return `${user.name} ${user.email}`.toLowerCase().includes(filter);
  }
}
