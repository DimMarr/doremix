export interface User {
  idUser: number;
  email: string;
  username: string;
  role: 'USER' | 'MODERATOR' | 'ADMIN';
  banned: boolean;
}

export interface AuthResponse {
  token: string;
  user: User;
}
