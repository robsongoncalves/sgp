export interface ServiceCategory {
  id: number;
  name: string;
  description: string;
  parent_category_id: number | null;
  parent_category_name: string;
  display_order: number;
  show_on_main_menu: boolean;
  active: boolean;
}

export type ServiceCategoryPayload = Omit<ServiceCategory, 'id' | 'parent_category_name'>;
