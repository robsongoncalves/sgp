export type TemplateExecutionMode = 'dynamic' | 'custom';

export interface TemplateField {
  name: string;
  label: string;
  type: string;
  required: boolean;
  order: number;
  options?: string[];
  data_source?: string;
  value_field?: string;
  label_field?: string;
  maps_to?: string;
  filters?: Record<string, unknown>;
}

export interface FormTemplate {
  id: number;
  name: string;
  slug: string;
  description: string;
  execution_mode: TemplateExecutionMode;
  fields_schema: TemplateField[];
  active: boolean;
}

export type FormTemplatePayload = Omit<FormTemplate, 'id'>;
