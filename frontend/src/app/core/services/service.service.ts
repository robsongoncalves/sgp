import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ServiceRating, ServiceRatingPayload, ServiceRatingSummary } from '../models/service-rating';
import { Service, ServicePayload } from '../models/service';

export interface DocumentationExtractionPayload {
  url: string;
  headings?: string[];
  content_class?: string;
  heading_tags?: string[];
  text_tags?: string[];
}

export interface DocumentationExtractionSection {
  heading: string;
  text: string;
  paragraphs: string[];
  found: boolean;
}

export interface DocumentationExtractionResult {
  url: string;
  content_class: string;
  headings: string[];
  sections: DocumentationExtractionSection[];
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class ServiceService {
  private readonly apiUrl = 'http://localhost:5000/api/services';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Service[]> {
    return this.http.get<Service[]>(this.apiUrl);
  }

  create(payload: ServicePayload): Observable<Service> {
    return this.http.post<Service>(this.apiUrl, payload);
  }

  update(serviceId: number, payload: ServicePayload): Observable<Service> {
    return this.http.put<Service>(`${this.apiUrl}/${serviceId}`, payload);
  }

  delete(serviceId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${serviceId}`);
  }

  getRatings(serviceId: number, userId?: number): Observable<ServiceRatingSummary> {
    const params = userId ? { user_id: userId } : undefined;

    return this.http.get<ServiceRatingSummary>(`${this.apiUrl}/${serviceId}/ratings`, { params });
  }

  saveRating(serviceId: number, payload: ServiceRatingPayload): Observable<ServiceRating> {
    return this.http.post<ServiceRating>(`${this.apiUrl}/${serviceId}/ratings`, payload);
  }

  extractDocumentation(payload: DocumentationExtractionPayload): Observable<DocumentationExtractionResult> {
    return this.http.post<DocumentationExtractionResult>(`${this.apiUrl}/documentation/extract`, payload);
  }
}
