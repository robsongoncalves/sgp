import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { UserGroup, UserGroupPayload } from '../models/user-group';

interface UserGroupMembersResponse {
  user_ids: number[];
}

@Injectable({
  providedIn: 'root'
})
export class UserGroupService {
  private readonly apiUrl = 'http://localhost:5000/api/user-groups';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<UserGroup[]> {
    return this.http.get<UserGroup[]>(this.apiUrl);
  }

  listByUser(userId: number): Observable<UserGroup[]> {
    const params = new HttpParams().set('user_id', userId);

    return this.http.get<UserGroup[]>(this.apiUrl, { params });
  }

  create(payload: UserGroupPayload): Observable<UserGroup> {
    return this.http.post<UserGroup>(this.apiUrl, payload);
  }

  update(groupId: number, payload: UserGroupPayload): Observable<UserGroup> {
    return this.http.put<UserGroup>(`${this.apiUrl}/${groupId}`, payload);
  }

  delete(groupId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${groupId}`);
  }

  getMemberUserIds(groupId: number): Observable<UserGroupMembersResponse> {
    return this.http.get<UserGroupMembersResponse>(`${this.apiUrl}/${groupId}/members`);
  }

  updateMemberUserIds(
    groupId: number,
    userIds: number[]
  ): Observable<UserGroupMembersResponse> {
    return this.http.put<UserGroupMembersResponse>(
      `${this.apiUrl}/${groupId}/members`,
      { user_ids: userIds }
    );
  }
}
