export interface AutomationLog {
  id: number;
  created_at: string;
  event_name: string;
  status: string;
  duration_ms: number;
  messages: string[];
  warnings: string[];
  error_message: string;
  service_id: number | null;
  service_name: string;
  service_slug: string;
  function_id: number | null;
  function_name: string;
  handler_key: string;
  service_request_id: number | null;
  service_request_number: string;
  user_id: number | null;
  user_name: string;
  user_email: string;
}
