import { HttpErrorResponse, HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, catchError, filter, switchMap, take, throwError } from 'rxjs';
import { Auth } from './auth';

let isRefreshing = false;
const refreshedToken$ = new BehaviorSubject<string | null>(null);

function withAuth(req: HttpRequest<unknown>, token: string) {
  return req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
}

function handle401(req: HttpRequest<unknown>, next: HttpHandlerFn, authService: Auth, router: Router) {
  if (!authService.getRefreshToken()) {
    authService.clearTokens();
    router.navigate(['/login']);
    return throwError(() => new Error('Session expired'));
  }

  if (!isRefreshing) {
    isRefreshing = true;
    refreshedToken$.next(null);

    return authService.refreshAccessToken().pipe(
      switchMap((response) => {
        isRefreshing = false;
        refreshedToken$.next(response.access);
        return next(withAuth(req, response.access));
      }),
      catchError((refreshError) => {
        isRefreshing = false;
        authService.clearTokens();
        router.navigate(['/login']);
        return throwError(() => refreshError);
      })
    );
  }

  return refreshedToken$.pipe(
    filter((token): token is string => token !== null),
    take(1),
    switchMap((token) => next(withAuth(req, token)))
  );
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(Auth);
  const router = inject(Router);
  const token = authService.getAccessToken();

  const authReq = token ? withAuth(req, token) : req;

  return next(authReq).pipe(
    catchError((error) => {
      const isAuthEndpoint = req.url.includes('/auth/login/') || req.url.includes('/auth/token/refresh/');

      if (error instanceof HttpErrorResponse && error.status === 401 && !isAuthEndpoint) {
        return handle401(req, next, authService, router);
      }

      return throwError(() => error);
    })
  );
};
