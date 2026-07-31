import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Observable } from 'rxjs';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { Auth } from '../../core/auth';
import { AccessRequest } from '../../core/models';

const PENDING_STATES = ['PENDING_MANAGER', 'PENDING_APP_OWNER', 'PENDING_SECURITY'];

@Component({
  selector: 'app-request-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, Sidebar, Header, LoadingSpinner],
  templateUrl: './request-detail.html',
  styleUrl: './request-detail.css'
})
export class RequestDetail implements OnInit {

  request     = signal<AccessRequest | null>(null);
  currentUser = signal<{ id: number; username: string; role: string } | null>(null);
  loading     = signal(true);
  error       = signal(false);
  actioning   = signal(false);
  actionError = signal('');
  comment     = signal('');

  // ── Derived permissions ───────────────────────────────────────────────────

  canSubmit = computed(() => {
    const req = this.request(); const user = this.currentUser();
    return req?.current_state === 'DRAFT' && req?.requester === user?.id;
  });

  canResubmit = computed(() => {
    const req = this.request(); const user = this.currentUser();
    return req?.current_state === 'INFO_REQUESTED' && req?.requester === user?.id;
  });

  isCurrentOwner = computed(() => {
    const req = this.request(); const user = this.currentUser();
    if (!req || !user) return false;
    return req.current_owner === user.id && PENDING_STATES.includes(req.current_state);
  });

  hasActions = computed(() =>
    this.canSubmit() || this.canResubmit() || this.isCurrentOwner()
  );

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rs: RequestService,
    private auth: Auth
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.auth.getCurrentUser().subscribe({
      next: (user) => this.currentUser.set(user)
    });

    this.rs.getRequest(id).subscribe({
      next:  (req) => { this.request.set(req); this.loading.set(false); },
      error: ()    => { this.error.set(true);   this.loading.set(false); }
    });
  }

  // ── Workflow actions ──────────────────────────────────────────────────────

  submit():        void { this._act((id, c) => this.rs.submitRequest(id, c)); }
  approve():       void { this._act((id, c) => this.rs.approveRequest(id, c)); }
  reject():        void { this._act((id, c) => this.rs.rejectRequest(id, c)); }
  returnForInfo(): void { this._act((id, c) => this.rs.returnForInfo(id, c)); }
  resubmit():      void { this._act((id, c) => this.rs.resubmitRequest(id, c)); }

  private _act(fn: (id: number, comment: string) => Observable<AccessRequest>): void {
    const req = this.request();
    if (!req) return;
    this.actioning.set(true);
    this.actionError.set('');
    fn(req.id, this.comment()).subscribe({
      next: (updated) => {
        this.request.set(updated);
        this.comment.set('');
        this.actioning.set(false);
      },
      error: (err) => {
        this.actionError.set(err?.error?.detail ?? 'Action failed. Please try again.');
        this.actioning.set(false);
      }
    });
  }

  // ── Display helpers ───────────────────────────────────────────────────────

  statusLabel(state: string): string {
    const map: Record<string, string> = {
      DRAFT: 'Draft', PENDING_MANAGER: 'Pending Manager',
      PENDING_APP_OWNER: 'Pending App Owner', PENDING_SECURITY: 'Pending Security',
      INFO_REQUESTED: 'Info Requested', APPROVED: 'Approved', REJECTED: 'Rejected',
    };
    return map[state] ?? state;
  }

  statusClass(state: string): string {
    const map: Record<string, string> = {
      DRAFT: 'badge-draft', PENDING_MANAGER: 'badge-pending',
      PENDING_APP_OWNER: 'badge-pending', PENDING_SECURITY: 'badge-pending',
      INFO_REQUESTED: 'badge-info', APPROVED: 'badge-approved', REJECTED: 'badge-rejected',
    };
    return map[state] ?? 'badge-draft';
  }

  historyIcon(action: string): string {
    const map: Record<string, string> = {
      SUBMIT: 'fa-paper-plane', APPROVE: 'fa-check',
      REJECT: 'fa-xmark', RETURN: 'fa-rotate-left', RESUBMIT: 'fa-rotate-right',
    };
    return `fa-solid ${map[action] ?? 'fa-circle'}`;
  }

  historyColor(action: string): string {
    const map: Record<string, string> = {
      SUBMIT: '#8a8a9a', APPROVE: '#10b981',
      REJECT: '#dc2626', RETURN: '#2563eb', RESUBMIT: '#7c3aed',
    };
    return map[action] ?? '#8a8a9a';
  }

  actionLabel(action: string): string {
    const map: Record<string, string> = {
      SUBMIT: 'Submitted', APPROVE: 'Approved',
      REJECT: 'Rejected', RETURN: 'Returned for Info', RESUBMIT: 'Resubmitted',
    };
    return map[action] ?? action;
  }
}
