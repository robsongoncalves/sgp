import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';

import { ServiceRequest } from '../../core/models/service-request';
import { UserGroup } from '../../core/models/user-group';
import { AuthService } from '../../core/services/auth.service';
import { ServiceRequestService } from '../../core/services/service-request.service';
import { UserGroupService } from '../../core/services/user-group.service';

@Component({
  selector: 'app-caixa-postal',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSortModule,
    MatTableModule,
    RouterLink
  ],
  templateUrl: './caixa-postal.component.html',
  styleUrl: './caixa-postal.component.scss'
})
export class CaixaPostalComponent implements OnInit, AfterViewInit {
  groups: UserGroup[] = [];
  dataSource = new MatTableDataSource<ServiceRequest>([]);
  displayedColumns = ['number', 'service_name', 'requester_name', 'status', 'created_at', 'updated_at', 'actions'];
  isLoadingGroups = false;
  isLoadingRequests = false;
  errorMessage = '';

  filterForm = this.formBuilder.nonNullable.group({
    groupId: [0, Validators.required],
    term: ['']
  });

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private readonly authService: AuthService,
    private readonly formBuilder: FormBuilder,
    private readonly serviceRequestService: ServiceRequestService,
    private readonly userGroupService: UserGroupService
  ) {}

  ngOnInit(): void {
    this.configureFilter();
    this.loadGroups();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  loadGroups(): void {
    this.isLoadingGroups = true;
    this.errorMessage = '';
    const currentUser = this.authService.currentUser;

    if (!currentUser) {
      this.errorMessage = 'Usuario nao autenticado.';
      this.isLoadingGroups = false;
      return;
    }

    this.userGroupService.listByUser(currentUser.id).subscribe({
      next: (groups) => {
        this.groups = groups;
        this.isLoadingGroups = false;

        if (groups.length) {
          this.filterForm.patchValue({ groupId: groups[0].id });
          this.consultar();
        }
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os grupos do usuario.';
        this.isLoadingGroups = false;
      }
    });
  }

  consultar(): void {
    const groupId = Number(this.filterForm.controls.groupId.value);

    if (!groupId) {
      this.dataSource.data = [];
      return;
    }

    this.isLoadingRequests = true;
    this.errorMessage = '';

    this.serviceRequestService.list({ groupId }).subscribe({
      next: (requests) => {
        this.dataSource.data = requests;
        this.applyTableFilter(this.filterForm.controls.term.value);
        this.configureDataTable();
        this.isLoadingRequests = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel consultar as solicitacoes.';
        this.isLoadingRequests = false;
      }
    });
  }

  limpar(): void {
    this.filterForm.patchValue({ term: '' });
    this.applyTableFilter('');
  }

  formatDate(value: string): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return '-';
    }

    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }

  private configureFilter(): void {
    this.dataSource.filterPredicate = (request, filter) => {
      const normalizedFilter = filter.trim().toLowerCase();
      const searchable = [
        request.number,
        request.service_name,
        request.requester_name,
        request.requester_email,
        request.status,
        request.current_situation_name
      ].join(' ').toLowerCase();

      return searchable.includes(normalizedFilter);
    };

    this.filterForm.controls.term.valueChanges.subscribe((value) => {
      this.applyTableFilter(value);
    });
  }

  private applyTableFilter(value: string): void {
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  private configureDataTable(): void {
    if (this.paginator) {
      this.dataSource.paginator = this.paginator;
    }

    if (this.sort) {
      this.dataSource.sort = this.sort;
    }
  }
}
