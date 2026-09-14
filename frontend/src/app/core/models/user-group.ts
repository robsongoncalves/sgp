export interface UserGroup {
  id: number;
  name: string;
  description: string;
  parent_group_id: number | null;
  parent_group_name: string;
  manager_user_id: number | null;
  manager_name: string;
  manager_email: string;
  active: boolean;
}

export type UserGroupPayload = Omit<UserGroup, 'id' | 'parent_group_name' | 'manager_name' | 'manager_email'>;
