import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';

import { AutomationLog } from '../../../core/models/automation-log';
import { LogService } from '../../../core/services/log.service';

@Component({
  selector: 'app-logs',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSortModule,
    MatTableModule
  ],
  templateUrl: './logs.component.html',
  styleUrl: './logs.component.scss'
})
export class LogsComponent implements OnInit, AfterViewInit {
  logs: AutomationLog[] = [];
  dataSource = new MatTableDataSource<AutomationLog>([]);
  displayedColumns = [
    'created_at',
    'status',
    'service_name',
    'automation',
    'event_name',
    'service_request_number',
    'user_name',
    'duration_ms',
    'details'
  ];
  filterTerm = '';
  isLoading = false;
  errorMessage = '';

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(private readonly logService: LogService) {}

  ngOnInit(): void {
    this.loadLogs();
  }

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  loadLogs(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.logService.listAutomationLogs().subscribe({
      next: (logs) => {
        this.logs = logs;
        this.dataSource.data = logs;
        this.configureDataTable();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Nao foi possivel carregar os logs.';
        this.isLoading = false;
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

  automationName(log: AutomationLog): string {
    return log.function_name || log.handler_key || '-';
  }

  eventLabel(eventName: string): string {
    const labels: Record<string, string> = {
      before_request_create: 'Antes de criar solicitação',
      after_request_create: 'Depois de criar solicitação'
    };

    return labels[eventName] || eventName;
  }

  details(log: AutomationLog): string {
    const parts = [
      ...log.messages.map((message) => `Mensagem: ${message}`),
      ...log.warnings.map((warning) => `Aviso: ${warning}`),
      log.error_message ? `Erro: ${log.error_message}` : ''
    ].filter(Boolean);

    return parts.length ? parts.join(' | ') : '-';
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (log, filter) => {
      const content = [
        log.created_at,
        log.status,
        log.service_name,
        log.service_slug,
        this.automationName(log),
        this.eventLabel(log.event_name),
        log.service_request_number,
        log.user_name,
        log.user_email,
        this.details(log)
      ].join(' ');

      return content.toLowerCase().includes(filter);
    };
  }
}
