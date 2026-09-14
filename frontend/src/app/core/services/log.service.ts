import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { AutomationLog } from '../models/automation-log';

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private readonly apiUrl = 'http://localhost:5000/api/logs';

  constructor(private readonly http: HttpClient) {}

  listAutomationLogs(limit = 300): Observable<AutomationLog[]> {
    const params = new HttpParams().set('limit', limit);

    return this.http.get<AutomationLog[]>(`${this.apiUrl}/automation`, { params });
  }
}
