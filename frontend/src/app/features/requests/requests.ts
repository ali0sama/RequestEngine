import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { AccessRequest } from '../../core/models';
import { statusLabel, statusClass } from '../../core/workflow';

const PENDING_STATES = ['PENDING_MANAGER', 'PENDING_APP_OWNER', 'PENDING_SECURITY'];

export interface FilterOption {
  value: string | null;
  label: string;
}

const FILTER_OPTIONS: FilterOption[] = [
  { value: null, label: 'All' },
  { value: 'pending', label: 'Pending Approval' },
  { value: 'info', label: 'Needs My Response' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
];

@Component({
  selector: 'app-requests',
  standalone: true,
  imports: [CommonModule, RouterModule, Sidebar, Header, LoadingSpinner],
  templateUrl: './requests.html',
  styleUrl: './requests.css'
})
export class Requests implements OnInit {

  requests     = signal<AccessRequest[]>([]);
  loading      = signal(true);
  error        = signal(false);
  statusFilter = signal<string | null>(null);
  filterOptions = FILTER_OPTIONS;

  filteredRequests = computed(() => {
    const filter = this.statusFilter();
    const all = this.requests();
    switch (filter) {
      case 'pending':  return all.filter(r => PENDING_STATES.includes(r.current_state));
      case 'info':     return all.filter(r => r.current_state === 'INFO_REQUESTED');
      case 'approved': return all.filter(r => r.current_state === 'APPROVED');
      case 'rejected': return all.filter(r => r.current_state === 'REJECTED');
      default:         return all;
    }
  });

  constructor(private requestService: RequestService, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.statusFilter.set(params.get('status'));
    });

    this.requestService.getMyRequests().subscribe({
      next:  (data) => { this.requests.set(data); this.loading.set(false); },
      error: ()     => { this.error.set(true);     this.loading.set(false); }
    });
  }

  isActive(value: string | null): boolean {
    return this.statusFilter() === value;
  }

  statusLabel = statusLabel;
  statusClass = statusClass;
}
