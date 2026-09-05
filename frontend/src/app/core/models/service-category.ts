export interface ServiceCategory {
  id: number;
  name: string;
  description: string;
  display_order: number;
  active: boolean;
}

export type ServiceCategoryPayload = Omit<ServiceCategory, 'id'>;
