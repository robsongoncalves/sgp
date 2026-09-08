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
  created_at: string;
  updated_at: string;
  canceled_at: string | null;
}

export interface CreateServiceRequestPayload {
  service_id?: number;
  service_slug?: string;
  requester_user_id?: number;
}
