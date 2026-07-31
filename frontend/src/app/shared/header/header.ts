import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Auth } from '../../core/auth';

const TITLE_MAP: Record<string, string> = {
  '/dashboard':       'Dashboard',
  '/requests':        'My Requests',
  '/create-request':  'New Request',
  '/approvals':       'Pending Approvals',
  '/applications':    'Applications',
};

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class Header implements OnInit {

  username  = signal('');
  role      = signal('');
  pageTitle = signal('Dashboard');

  constructor(private auth: Auth, private router: Router) {}

  ngOnInit(): void {
    const url = this.router.url.split('?')[0];
    const base = '/' + url.split('/')[1];

    if (url.match(/^\/requests\/\d+/)) {
      this.pageTitle.set('Request Detail');
    } else {
      this.pageTitle.set(TITLE_MAP[base] ?? 'Dashboard');
    }

    this.auth.getCurrentUser().subscribe({
      next:  (user) => { this.username.set(user.username); this.role.set(user.role); },
      error: ()     => { this.username.set('Unknown User'); }
    });
  }

  logout(): void {
    this.auth.logout().subscribe({
      complete: () => this.router.navigate(['/login']),
      error:    () => { localStorage.clear(); this.router.navigate(['/login']); }
    });
  }
}
