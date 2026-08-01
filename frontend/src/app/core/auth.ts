import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

interface LoginResponse {
  access: string;
  refresh: string;
}

interface RefreshResponse {
  access: string;
}

interface CurrentUser {
  id: number;
  username: string;
  email: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login/`, { username, password }).pipe(
      tap((response) => {
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
      })
    );
  }

  logout(): Observable<any> {
    const refresh = localStorage.getItem('refresh_token');
    return this.http.post(`${this.apiUrl}/auth/logout/`, { refresh }).pipe(
      tap(() => this.clearTokens())
    );
  }

  getCurrentUser(): Observable<CurrentUser> {
    return this.http.get<CurrentUser>(`${this.apiUrl}/auth/me/`);
  }

  changePassword(oldPassword: string, newPassword: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/change-password/`, {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }

  refreshAccessToken(): Observable<RefreshResponse> {
    const refresh = this.getRefreshToken();
    return this.http.post<RefreshResponse>(`${this.apiUrl}/auth/token/refresh/`, { refresh }).pipe(
      tap((response) => this.setAccessToken(response.access))
    );
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  setAccessToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isLoggedIn(): boolean {
    return this.getAccessToken() !== null;
  }
}