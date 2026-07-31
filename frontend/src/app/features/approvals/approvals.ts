import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { Auth } from '../../core/auth';
import { AccessRequest } from '../../core/models';

const APPROVER_ROLES = ['MANAGER', 'APP_OWNER', 'SECURITY'];

@Component({
  selector: 'app-approvals',
  standalone: true,
  imports: [CommonModule, RouterModule, Sidebar, Header, LoadingSpinner],
  templateUrl: './approvals.html',
  styleUrl: './approvals.css'
})
export class Approvals implements OnInit {

  approvals   = signal<AccessRequest[]>([]);
  loading     = signal(true);
  error       = signal(false);
  restricted  = signal(false);

  constructor(private requestService: RequestService, private auth: Auth) {}

  ngOnInit(): void {
    this.auth.getCurrentUser().subscribe({
      next: (user) => {
        if (!APPROVER_ROLES.includes(user.role)) {
          this.restricted.set(true);
          this.loading.set(false);
          return;
        }
        this.requestService.getPendingApprovals().subscribe({
          next:  (data) => { this.approvals.set(data); this.loading.set(false); },
          error: ()     => { this.error.set(true);      this.loading.set(false); }
        });
      },
      error: () => { this.error.set(true); this.loading.set(false); }
    });
  }

  stageLabel(state: string): string {
    const map: Record<string, string> = {
      PENDING_MANAGER:   'Manager Review',
      PENDING_APP_OWNER: 'App Owner Review',
      PENDING_SECURITY:  'Security Review',
    };
    return map[state] ?? state;
  }

  stageIcon(state: string): string {
    const map: Record<string, string> = {
      PENDING_MANAGER:   'fa-user-tie',
      PENDING_APP_OWNER: 'fa-layer-group',
      PENDING_SECURITY:  'fa-shield-halved',
    };
    return map[state] ?? 'fa-clock';
  }

  stageColor(state: string): string {
    const map: Record<string, string> = {
      PENDING_MANAGER:   '#f59e0b',
      PENDING_APP_OWNER: '#6366f1',
      PENDING_SECURITY:  '#E60000',
    };
    return map[state] ?? '#8a8a9a';
  }
}
