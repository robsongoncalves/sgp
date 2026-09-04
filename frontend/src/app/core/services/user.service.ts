import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { User, UserPayload } from '../models/user';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly apiUrl = 'http://localhost:5000/api/users';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  create(payload: UserPayload): Observable<User> {
    return this.http.post<User>(this.apiUrl, payload);
  }

  update(userId: number, payload: UserPayload): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${userId}`, payload);
  }

  delete(userId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${userId}`);
  }
}
