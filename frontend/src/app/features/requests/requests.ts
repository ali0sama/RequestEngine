import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { AccessRequest } from '../../core/models';

@Component({
  selector: 'app-requests',
  standalone: true,
  imports: [CommonModule, RouterModule, Sidebar, Header, LoadingSpinner],
  templateUrl: './requests.html',
  styleUrl: './requests.css'
})
export class Requests implements OnInit {

  requests = signal<AccessRequest[]>([]);
  loading  = signal(true);
  error    = signal(false);

  constructor(private requestService: RequestService) {}

  ngOnInit(): void {
    this.requestService.getMyRequests().subscribe({
      next:  (data) => { this.requests.set(data); this.loading.set(false); },
      error: ()     => { this.error.set(true);     this.loading.set(false); }
    });
  }

  statusLabel(state: string): string {
    const labels: Record<string, string> = {
      DRAFT:             'Draft',
      PENDING_MANAGER:   'Pending Manager',
      PENDING_APP_OWNER: 'Pending App Owner',
      PENDING_SECURITY:  'Pending Security',
      INFO_REQUESTED:    'Info Requested',
      APPROVED:          'Approved',
      REJECTED:          'Rejected',
    };
    return labels[state] ?? state;
  }

  statusClass(state: string): string {
    const classes: Record<string, string> = {
      DRAFT:             'badge-draft',
      PENDING_MANAGER:   'badge-pending',
      PENDING_APP_OWNER: 'badge-pending',
      PENDING_SECURITY:  'badge-pending',
      INFO_REQUESTED:    'badge-info',
      APPROVED:          'badge-approved',
      REJECTED:          'badge-rejected',
    };
    return classes[state] ?? 'badge-draft';
  }
}
