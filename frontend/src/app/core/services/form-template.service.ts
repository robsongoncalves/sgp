import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { FormTemplate, FormTemplatePayload } from '../models/form-template';

@Injectable({
  providedIn: 'root'
})
export class FormTemplateService {
  private readonly apiUrl = 'http://localhost:5000/api/form-templates';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<FormTemplate[]> {
    return this.http.get<FormTemplate[]>(this.apiUrl);
  }

  create(payload: FormTemplatePayload): Observable<FormTemplate> {
    return this.http.post<FormTemplate>(this.apiUrl, payload);
  }

  update(templateId: number, payload: FormTemplatePayload): Observable<FormTemplate> {
    return this.http.put<FormTemplate>(`${this.apiUrl}/${templateId}`, payload);
  }

  delete(templateId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${templateId}`);
  }
}
