import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';

import { PONTUACAO_PROGRESSAO_DOCENTE } from '../../../core/data/progressao-docente-pontuacao';

interface FieldMapEntry {
  serviceName: string;
  moduleKey: string;
  requirementCode: string;
  itemNumber: number;
  itemLabel: string;
  points: string;
  measure: string;
  fieldPath: string;
}

@Component({
  selector: 'app-mapa-campos',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatPaginatorModule,
    MatSortModule,
    MatTableModule
  ],
  templateUrl: './mapa-campos.component.html',
  styleUrl: './mapa-campos.component.scss'
})
export class MapaCamposComponent implements AfterViewInit {
  readonly fieldEntries = this.buildFieldEntries();
  readonly dataSource = new MatTableDataSource<FieldMapEntry>(this.fieldEntries);
  readonly displayedColumns = [
    'serviceName',
    'requirementCode',
    'itemNumber',
    'itemLabel',
    'points',
    'measure',
    'fieldPath'
  ];
  filterTerm = '';

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  ngAfterViewInit(): void {
    this.configureDataTable();
  }

  applyFilter(value: string): void {
    this.filterTerm = value;
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  copyFieldPath(fieldPath: string): void {
    navigator.clipboard?.writeText(fieldPath);
  }

  private configureDataTable(): void {
    this.dataSource.paginator = this.paginator || null;
    this.dataSource.sort = this.sort || null;
    this.dataSource.filterPredicate = (entry, filter) => {
      const content = [
        entry.serviceName,
        entry.moduleKey,
        entry.requirementCode,
        entry.itemNumber,
        entry.itemLabel,
        entry.points,
        entry.measure,
        entry.fieldPath
      ].join(' ');

      return content.toLowerCase().includes(filter);
    };
  }

  private buildFieldEntries(): FieldMapEntry[] {
    return PONTUACAO_PROGRESSAO_DOCENTE.flatMap((requirement) =>
      requirement.items.map((item, index) => ({
        serviceName: 'Calculadora de Pontuação Progressão Docente',
        moduleKey: 'calculadora-pontuacao-docente',
        requirementCode: requirement.code,
        itemNumber: index + 1,
        itemLabel: item.label,
        points: item.points,
        measure: item.measure,
        fieldPath: `pontuacao.quantities["${requirement.code}-${index}"]`
      }))
    );
  }
}
