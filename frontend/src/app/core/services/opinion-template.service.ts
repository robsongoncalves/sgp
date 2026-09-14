import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { OpinionTemplate, OpinionTemplatePayload } from '../models/opinion-template';

@Injectable({
  providedIn: 'root'
})
export class OpinionTemplateService {
  private readonly apiUrl = 'http://localhost:5000/api/opinion-templates';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<OpinionTemplate[]> {
    return this.http.get<OpinionTemplate[]>(this.apiUrl);
  }

  create(payload: OpinionTemplatePayload): Observable<OpinionTemplate> {
    return this.http.post<OpinionTemplate>(this.apiUrl, payload);
  }

  update(templateId: number, payload: OpinionTemplatePayload): Observable<OpinionTemplate> {
    return this.http.put<OpinionTemplate>(`${this.apiUrl}/${templateId}`, payload);
  }

  delete(templateId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${templateId}`);
  }
}
