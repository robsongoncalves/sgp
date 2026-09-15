import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DocumentationExtractionPayload, DocumentationExtractionResult } from './service.service';

export interface Documentation {
  id: number;
  url: string;
  description: string;
  description_html?: string;
  description_text?: string;
  headings: string[];
  sync_enabled: boolean;
}
export type DocumentationPayload = Pick<Documentation, 'url' | 'description' | 'headings' | 'sync_enabled'>;
export interface DocumentationSyncResult {
  total: number;
  updated: number;
  failed: number;
  errors: { id: number; url: string; message: string }[];
}

@Injectable({ providedIn: 'root' })
export class DocumentationService {
  private readonly apiUrl = 'http://localhost:5000/api/documentations';
  constructor(private readonly http: HttpClient) {}
  list() { return this.http.get<Documentation[]>(this.apiUrl); }
  create(payload: DocumentationPayload) { return this.http.post<Documentation>(this.apiUrl, payload); }
  update(id: number, payload: DocumentationPayload) { return this.http.put<Documentation>(`${this.apiUrl}/${id}`, payload); }
  delete(id: number) { return this.http.delete<void>(`${this.apiUrl}/${id}`); }
  syncAll() { return this.http.post<DocumentationSyncResult>(`${this.apiUrl}/sync`, {}); }
  import(payload: DocumentationExtractionPayload) {
    return this.http.post<DocumentationExtractionResult>(`${this.apiUrl}/import`, payload);
  }
}
