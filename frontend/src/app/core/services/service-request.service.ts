import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { CreateServiceRequestPayload, ServiceRequest } from '../models/service-request';

export interface ServiceRequestListFilters {
  requesterUserId?: number;
  groupId?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ServiceRequestService {
  private readonly apiUrl = 'http://localhost:5000/api/service-requests';

  constructor(private readonly http: HttpClient) {}

  list(filters?: number | ServiceRequestListFilters): Observable<ServiceRequest[]> {
    let params = new HttpParams();

    if (typeof filters === 'number') {
      params = params.set('requester_user_id', filters);
    } else {
      if (filters?.requesterUserId) {
        params = params.set('requester_user_id', filters.requesterUserId);
      }

      if (filters?.groupId) {
        params = params.set('group_id', filters.groupId);
      }
    }

    return this.http.get<ServiceRequest[]>(this.apiUrl, { params });
  }

  create(payload: CreateServiceRequestPayload): Observable<ServiceRequest> {
    return this.http.post<ServiceRequest>(this.apiUrl, payload);
  }
}
