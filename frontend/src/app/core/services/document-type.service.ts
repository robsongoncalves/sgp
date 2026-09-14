import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { DocumentType, DocumentTypePayload } from '../models/document-type';

@Injectable({
  providedIn: 'root'
})
export class DocumentTypeService {
  private readonly apiUrl = 'http://localhost:5000/api/document-types';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<DocumentType[]> {
    return this.http.get<DocumentType[]>(this.apiUrl);
  }

  create(payload: DocumentTypePayload): Observable<DocumentType> {
    return this.http.post<DocumentType>(this.apiUrl, payload);
  }

  update(documentTypeId: number, payload: DocumentTypePayload): Observable<DocumentType> {
    return this.http.put<DocumentType>(`${this.apiUrl}/${documentTypeId}`, payload);
  }

  delete(documentTypeId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${documentTypeId}`);
  }
}
