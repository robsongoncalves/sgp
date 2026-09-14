export type DocumentOrigin = 'requester' | 'responsible_group' | 'system' | 'external';
export type DocumentPurpose = 'attachment' | 'form' | 'opinion' | 'evaluation' | 'generated' | 'linked_service';

export interface DocumentType {
  id: number;
  name: string;
  code: string;
  description: string;
  origin: DocumentOrigin;
  purpose: DocumentPurpose;
  module_slug: string;
  form_template_id: number | null;
  form_template_name: string;
  opinion_template_id: number | null;
  opinion_template_name: string;
  linked_service_id: number | null;
  linked_service_name: string;
  linked_service_slug: string;
  linked_service_module_key: string;
  linked_service_required_status: string;
  allowed_formats: string;
  required_by_default: boolean;
  allow_multiple_files: boolean;
  active: boolean;
}

export type DocumentTypePayload = Omit<
  DocumentType,
  | 'id'
  | 'form_template_name'
  | 'opinion_template_name'
  | 'linked_service_name'
  | 'linked_service_slug'
  | 'linked_service_module_key'
>;
