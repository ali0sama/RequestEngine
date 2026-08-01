import { Routes } from '@angular/router';
import { authGuard } from './core/auth-guard';

export const routes: Routes = [

  {
    path: 'login',
    loadComponent: () =>
      import('./features/login/login').then(m => m.Login)
  },

  {
    path: 'change-password',
    loadComponent: () =>
      import('./features/change-password/change-password').then(m => m.ChangePassword)
  },

  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard').then(m => m.Dashboard),
    canActivate: [authGuard]
  },

  {
    path: 'requests',
    loadComponent: () =>
      import('./features/requests/requests').then(m => m.Requests),
    canActivate: [authGuard]
  },

  {
    path: 'requests/:id',
    loadComponent: () =>
      import('./features/request-detail/request-detail').then(m => m.RequestDetail),
    canActivate: [authGuard]
  },

  {
    path: 'create-request',
    loadComponent: () =>
      import('./features/create-request/create-request').then(m => m.CreateRequest),
    canActivate: [authGuard]
  },

  {
    path: 'approvals',
    loadComponent: () =>
      import('./features/approvals/approvals').then(m => m.Approvals),
    canActivate: [authGuard]
  },

  {
    path: 'applications',
    loadComponent: () =>
      import('./features/applications/applications').then(m => m.Applications),
    canActivate: [authGuard]
  },

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  {
    path: '**',
    redirectTo: 'login'
  }

];
