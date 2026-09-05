import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ServiceCategory, ServiceCategoryPayload } from '../models/service-category';

@Injectable({
  providedIn: 'root'
})
export class ServiceCategoryService {
  private readonly apiUrl = 'http://localhost:5000/api/service-categories';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<ServiceCategory[]> {
    return this.http.get<ServiceCategory[]>(this.apiUrl);
  }

  create(payload: ServiceCategoryPayload): Observable<ServiceCategory> {
    return this.http.post<ServiceCategory>(this.apiUrl, payload);
  }

  update(categoryId: number, payload: ServiceCategoryPayload): Observable<ServiceCategory> {
    return this.http.put<ServiceCategory>(`${this.apiUrl}/${categoryId}`, payload);
  }

  delete(categoryId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${categoryId}`);
  }
}
