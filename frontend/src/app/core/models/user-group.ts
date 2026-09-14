export interface UserGroup {
  id: number;
  name: string;
  description: string;
  manager_user_id: number | null;
  manager_name: string;
  manager_email: string;
  active: boolean;
}

export type UserGroupPayload = Omit<UserGroup, 'id' | 'manager_name' | 'manager_email'>;
