export type ServiceImplementationMode = 'custom_module' | 'standard';

export interface ServiceSituation {
  id: number;
  name: string;
  previous_situation_id: number | null;
  responsible_group_id: number | null;
  is_initial: boolean;
  is_final: boolean;
  requires_opinion: boolean;
  requires_attachment: boolean;
  document_type_ids: number[];
  display_order: number;
}

export interface ServiceHook {
  id: number;
  function_id: number | null;
  function_name: string;
  event_name: string;
  handler_key: string;
  config: Record<string, unknown>;
  execution_order: number;
  active: boolean;
}

export interface Service {
  id: number;
  name: string;
  slug: string;
  description: string;
  description_html?: string;
  description_text?: string;
  documentation_id?: number | null;
  documentation_url: string;
  documentation_headings?: string[];
  implementation_mode: ServiceImplementationMode;
  module_key: string;
  active: boolean;
  featured: boolean;
  updated_at: string;
  category_ids: number[];
  group_ids: number[];
  situations: ServiceSituation[];
  hooks: ServiceHook[];
}

export type ServicePayload = Omit<Service, 'id'>;

export type ServiceSituationDraft = Omit<ServiceSituation, 'id'> & {
  id?: number;
};

export type ServiceHookDraft = Omit<ServiceHook, 'id' | 'function_name' | 'config'> & {
  id?: number;
  config: Record<string, unknown>;
  config_text: string;
};
