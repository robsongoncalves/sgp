import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import {
  CreateServiceRequestPayload,
  ServiceRequest,
  ServiceRequestAttachment,
  ServiceRequestDocument
} from '../models/service-request';

export interface ServiceRequestListFilters {
  requesterUserId?: number;
  groupId?: number;
  serviceSlug?: string;
  status?: string;
}

export interface ServiceRequestAttachmentFilters {
  contextType?: string;
  requirementCode?: string;
  itemIndex?: number;
  serviceRequestDocumentId?: number;
}

export interface ServiceRequestAttachmentPayload {
  uploadedByUserId: number;
  contextType: string;
  requirementCode: string;
  itemIndex: number;
  serviceRequestDocumentId?: number;
  file: File;
}

export interface ServiceRequestDocumentPayload {
  service_situation_id: number;
  document_type_id: number;
  created_by_user_id?: number;
  updated_by_user_id?: number;
  status?: string;
  content_data?: Record<string, unknown>;
  assigned_to_user_id?: number | null;
  assigned_to_group_id?: number | null;
  linked_service_request_id?: number | null;
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

      if (filters?.serviceSlug) {
        params = params.set('service_slug', filters.serviceSlug);
      }

      if (filters?.status) {
        params = params.set('status', filters.status);
      }
    }

    return this.http.get<ServiceRequest[]>(this.apiUrl, { params });
  }

  create(payload: CreateServiceRequestPayload): Observable<ServiceRequest> {
    return this.http.post<ServiceRequest>(this.apiUrl, payload);
  }

  get(serviceRequestId: number): Observable<ServiceRequest> {
    return this.http.get<ServiceRequest>(`${this.apiUrl}/${serviceRequestId}`);
  }

  updateFormData(serviceRequestId: number, formData: Record<string, unknown>): Observable<ServiceRequest> {
    return this.http.patch<ServiceRequest>(
      `${this.apiUrl}/${serviceRequestId}/form-data`,
      { form_data: formData }
    );
  }

  updateSituation(serviceRequestId: number, situation: number | string): Observable<ServiceRequest> {
    const payload = typeof situation === 'number'
      ? { situation_id: situation }
      : { situation_name: situation };

    return this.http.patch<ServiceRequest>(
      `${this.apiUrl}/${serviceRequestId}/situation`,
      payload
    );
  }

  listDocuments(serviceRequestId: number): Observable<ServiceRequestDocument[]> {
    return this.http.get<ServiceRequestDocument[]>(`${this.apiUrl}/${serviceRequestId}/documents`);
  }

  listAssignedDocuments(userId: number): Observable<ServiceRequestDocument[]> {
    const params = new HttpParams().set('assigned_to_user_id', userId);

    return this.http.get<ServiceRequestDocument[]>(
      'http://localhost:5000/api/service-request-documents',
      { params }
    );
  }

  createDocument(
    serviceRequestId: number,
    payload: ServiceRequestDocumentPayload
  ): Observable<ServiceRequestDocument> {
    return this.http.post<ServiceRequestDocument>(`${this.apiUrl}/${serviceRequestId}/documents`, payload);
  }

  updateDocument(
    serviceRequestId: number,
    documentId: number,
    payload: Partial<ServiceRequestDocumentPayload>
  ): Observable<ServiceRequestDocument> {
    return this.http.put<ServiceRequestDocument>(
      `${this.apiUrl}/${serviceRequestId}/documents/${documentId}`,
      payload
    );
  }

  deleteDocument(serviceRequestId: number, documentId: number, userId: number): Observable<void> {
    const params = new HttpParams().set('user_id', userId);

    return this.http.delete<void>(`${this.apiUrl}/${serviceRequestId}/documents/${documentId}`, { params });
  }

  submitDocument(
    serviceRequestId: number,
    documentId: number,
    submittedByUserId: number,
    assignedToUserId?: number | null
  ): Observable<ServiceRequestDocument> {
    return this.http.post<ServiceRequestDocument>(
      `${this.apiUrl}/${serviceRequestId}/documents/${documentId}/submit`,
      {
        submitted_by_user_id: submittedByUserId,
        assigned_to_user_id: assignedToUserId
      }
    );
  }

  decideDocument(
    serviceRequestId: number,
    documentId: number,
    decidedByUserId: number,
    decision: 'approved' | 'rejected' | 'returned',
    decisionText = ''
  ): Observable<ServiceRequestDocument> {
    return this.http.post<ServiceRequestDocument>(
      `${this.apiUrl}/${serviceRequestId}/documents/${documentId}/decision`,
      {
        decided_by_user_id: decidedByUserId,
        decision,
        decision_text: decisionText
      }
    );
  }

  listAttachments(
    serviceRequestId: number,
    filters?: ServiceRequestAttachmentFilters
  ): Observable<ServiceRequestAttachment[]> {
    let params = new HttpParams();

    if (filters?.contextType) {
      params = params.set('context_type', filters.contextType);
    }

    if (filters?.requirementCode) {
      params = params.set('requirement_code', filters.requirementCode);
    }

    if (filters?.itemIndex !== undefined) {
      params = params.set('item_index', filters.itemIndex);
    }

    if (filters?.serviceRequestDocumentId !== undefined) {
      params = params.set('service_request_document_id', filters.serviceRequestDocumentId);
    }

    return this.http.get<ServiceRequestAttachment[]>(
      `${this.apiUrl}/${serviceRequestId}/attachments`,
      { params }
    );
  }

  uploadAttachment(
    serviceRequestId: number,
    payload: ServiceRequestAttachmentPayload
  ): Observable<ServiceRequestAttachment> {
    const formData = new FormData();
    formData.append('file', payload.file);
    formData.append('uploaded_by_user_id', String(payload.uploadedByUserId));
    formData.append('context_type', payload.contextType);
    formData.append('requirement_code', payload.requirementCode);
    formData.append('item_index', String(payload.itemIndex));

    if (payload.serviceRequestDocumentId) {
      formData.append('service_request_document_id', String(payload.serviceRequestDocumentId));
    }

    return this.http.post<ServiceRequestAttachment>(
      `${this.apiUrl}/${serviceRequestId}/attachments`,
      formData
    );
  }

  uploadDocumentAttachment(
    serviceRequestId: number,
    documentId: number,
    payload: ServiceRequestAttachmentPayload
  ): Observable<ServiceRequestAttachment> {
    const formData = new FormData();
    formData.append('file', payload.file);
    formData.append('uploaded_by_user_id', String(payload.uploadedByUserId));
    formData.append('context_type', payload.contextType);
    formData.append('requirement_code', payload.requirementCode);
    formData.append('item_index', String(payload.itemIndex));

    return this.http.post<ServiceRequestAttachment>(
      `${this.apiUrl}/${serviceRequestId}/documents/${documentId}/attachments`,
      formData
    );
  }

  deleteAttachment(serviceRequestId: number, attachmentId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${serviceRequestId}/attachments/${attachmentId}`);
  }

  getAttachmentDownloadUrl(serviceRequestId: number, attachmentId: number): string {
    return `${this.apiUrl}/${serviceRequestId}/attachments/${attachmentId}/download`;
  }
}
