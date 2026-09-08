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

export interface CreateServiceRequestPayload {
  service_id?: number;
  service_slug?: string;
  requester_user_id?: number;
}
