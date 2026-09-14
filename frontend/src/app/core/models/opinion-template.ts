import { TemplateExecutionMode, TemplateField } from './form-template';

export interface OpinionTemplate {
  id: number;
  name: string;
  slug: string;
  description: string;
  execution_mode: TemplateExecutionMode;
  default_responsible_group_id: number | null;
  default_responsible_group_name: string;
  decision_options: string[];
  fields_schema: TemplateField[];
  requires_justification: boolean;
  requires_signature: boolean;
  allow_attachments: boolean;
  active: boolean;
}

export type OpinionTemplatePayload = Omit<OpinionTemplate, 'id' | 'default_responsible_group_name'>;
