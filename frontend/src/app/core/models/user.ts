export interface User {
  id: number;
  name: string;
  email: string;
  active: boolean;
}

export type UserPayload = Omit<User, 'id'> & {
  password?: string;
};
