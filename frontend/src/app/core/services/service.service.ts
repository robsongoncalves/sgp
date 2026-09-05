import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Service, ServicePayload } from '../models/service';

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
}
