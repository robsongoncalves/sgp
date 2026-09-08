export interface User {
  id: number;
  name: string;
  email: string;
  siape: string;
  cargo: string;
  classe_nivel: string;
  local_exercicio: string;
  telefone: string;
  active: boolean;
}

export type UserPayload = Omit<User, 'id'> & {
  password?: string;
};
