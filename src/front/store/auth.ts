import { User } from '@models/user';
import { AuthRepository } from '@repositories/authRepository';

export class AuthStore {
  private token: string | null = null;
  private user: User | null = null;
  private isLoading: boolean = false;
  private error: string | null = null;
  private listeners: (() => void)[] = [];

  constructor() {
    // Load token from localStorage on init
    this.token = localStorage.getItem('auth_token');
    if (this.token) {
      this.loadCurrentUser();
    }
  }

  subscribe(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify() {
    this.listeners.forEach(listener => listener());
  }

  private async loadCurrentUser() {
    if (!this.token) return;

    try {
      this.user = await AuthRepository.getCurrentUser(this.token);
      this.notify();
    } catch (error) {
      // Token invalid, clear it
      this.logout();
    }
  }

  async signup(email: string, password: string, username: string) {
    this.isLoading = true;
    this.error = null;
    this.notify();

    try {
      const response = await AuthRepository.signup(email, password, username);
      this.setToken(response.token);
      this.setUser(response.user);
      return response;
    } catch (error: any) {
      this.error = error.message;
      this.notify();
      throw error;
    } finally {
      this.isLoading = false;
      this.notify();
    }
  }

  async login(email: string, password: string) {
    this.isLoading = true;
    this.error = null;
    this.notify();

    try {
      const response = await AuthRepository.login(email, password);
      this.setToken(response.token);
      this.setUser(response.user);
      return response;
    } catch (error: any) {
      this.error = error.message;
      this.notify();
      throw error;
    } finally {
      this.isLoading = false;
      this.notify();
    }
  }

  logout() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('auth_token');
    this.notify();
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
    this.notify();
  }

  setUser(user: User) {
    this.user = user;
    this.notify();
  }

  getToken(): string | null {
    return this.token;
  }

  getUser(): User | null {
    return this.user;
  }

  isAuthenticated(): boolean {
    return this.token !== null && this.user !== null;
  }

  getError(): string | null {
    return this.error;
  }

  getIsLoading(): boolean {
    return this.isLoading;
  }
}
