import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';

import { User } from '../models/user';

interface LoginResponse {
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = 'http://localhost:5000/api/auth';
  private readonly storageKey = 'sgp.currentUser';
  private readonly currentUserSubject = new BehaviorSubject<User | null>(this.readStoredUser());

  readonly currentUser$ = this.currentUserSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  get isAuthenticated(): boolean {
    return this.currentUser !== null;
  }

  get isSystemAdmin(): boolean {
    return this.isSystemAdminUser(this.currentUser);
  }

  isSystemAdminUser(user: User | null): boolean {
    return user?.id === 1 || user?.email === 'admin@unipampa.edu.br';
  }

  login(email: string, password: string, remember: boolean): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, { email, password }).pipe(
      tap(({ user }) => {
        this.currentUserSubject.next(user);

        if (remember) {
          localStorage.setItem(this.storageKey, JSON.stringify(user));
          sessionStorage.removeItem(this.storageKey);
        } else {
          sessionStorage.setItem(this.storageKey, JSON.stringify(user));
          localStorage.removeItem(this.storageKey);
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.storageKey);
    sessionStorage.removeItem(this.storageKey);
    this.currentUserSubject.next(null);
  }

  private readStoredUser(): User | null {
    const storedUser = sessionStorage.getItem(this.storageKey) || localStorage.getItem(this.storageKey);

    if (!storedUser) {
      return null;
    }

    try {
      return JSON.parse(storedUser) as User;
    } catch {
      localStorage.removeItem(this.storageKey);
      sessionStorage.removeItem(this.storageKey);
      return null;
    }
  }
}
