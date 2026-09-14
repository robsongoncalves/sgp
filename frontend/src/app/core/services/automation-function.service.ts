import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { AutomationFunction, AutomationFunctionPayload } from '../models/automation-function';

@Injectable({
  providedIn: 'root'
})
export class AutomationFunctionService {
  private readonly apiUrl = 'http://localhost:5000/api/automation-functions';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<AutomationFunction[]> {
    return this.http.get<AutomationFunction[]>(this.apiUrl);
  }

  create(payload: AutomationFunctionPayload): Observable<AutomationFunction> {
    return this.http.post<AutomationFunction>(this.apiUrl, payload);
  }

  update(functionId: number, payload: AutomationFunctionPayload): Observable<AutomationFunction> {
    return this.http.put<AutomationFunction>(`${this.apiUrl}/${functionId}`, payload);
  }

  delete(functionId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${functionId}`);
  }
}
