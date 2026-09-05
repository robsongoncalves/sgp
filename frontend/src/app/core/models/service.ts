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
  display_order: number;
}

export interface Service {
  id: number;
  name: string;
  slug: string;
  description: string;
  documentation_url: string;
  implementation_mode: ServiceImplementationMode;
  module_key: string;
  active: boolean;
  featured: boolean;
  updated_at: string;
  category_ids: number[];
  group_ids: number[];
  situations: ServiceSituation[];
}

export type ServicePayload = Omit<Service, 'id'>;

export type ServiceSituationDraft = Omit<ServiceSituation, 'id'> & {
  id?: number;
};
