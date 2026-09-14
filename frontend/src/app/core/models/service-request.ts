export interface ServiceRequest {
  id: number;
  number: string;
  service_id: number;
  service_name: string;
  service_slug: string;
  module_key: string;
  requester_user_id: number;
  requester_name: string;
  requester_email: string;
  current_situation_id: number | null;
  current_situation_name: string;
  status: string;
  form_data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  canceled_at: string | null;
}

export interface ServiceRequestAttachment {
  id: number;
  service_request_id: number;
  service_request_document_id: number | null;
  uploaded_by_user_id: number;
  uploaded_by_name: string;
  original_name: string;
  mime_type: string;
  size_bytes: number;
  bucket: string;
  object_key: string;
  sha256: string;
  context_type: string;
  requirement_code: string;
  item_index: number | null;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ServiceRequestDocument {
  id: number;
  service_request_id: number;
  service_situation_id: number;
  service_situation_name: string;
  document_type_id: number;
  document_type_name: string;
  linked_service_request_id: number | null;
  linked_service_request_number: string;
  linked_service_request_status: string;
  linked_service_request_service_slug: string;
  linked_service_request_module_key: string;
  created_by_user_id: number;
  created_by_name: string;
  updated_by_user_id: number | null;
  updated_by_name: string;
  assigned_to_user_id: number | null;
  assigned_to_user_name: string;
  assigned_to_user_email: string;
  assigned_to_group_id: number | null;
  assigned_to_group_name: string;
  decided_by_user_id: number | null;
  decided_by_name: string;
  decided_at: string | null;
  decision: string;
  decision_text: string;
  status: string;
  content_data: Record<string, unknown>;
  attachments_count: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface CreateServiceRequestPayload {
  service_id?: number;
  service_slug?: string;
  requester_user_id?: number;
}
