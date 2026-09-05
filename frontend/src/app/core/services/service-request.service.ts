import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { CreateServiceRequestPayload, ServiceRequest } from '../models/service-request';

@Injectable({
  providedIn: 'root'
})
export class ServiceRequestService {
  private readonly apiUrl = 'http://localhost:5000/api/service-requests';

  constructor(private readonly http: HttpClient) {}

  list(requesterUserId?: number): Observable<ServiceRequest[]> {
    const params = requesterUserId
      ? new HttpParams().set('requester_user_id', requesterUserId)
      : undefined;

    return this.http.get<ServiceRequest[]>(this.apiUrl, { params });
  }

  create(payload: CreateServiceRequestPayload): Observable<ServiceRequest> {
    return this.http.post<ServiceRequest>(this.apiUrl, payload);
  }
}
