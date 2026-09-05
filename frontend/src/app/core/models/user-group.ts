export interface UserGroup {
  id: number;
  name: string;
  description: string;
  active: boolean;
}

export type UserGroupPayload = Omit<UserGroup, 'id'>;
