import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { StatisticCard } from '../../shared/statistic-card/statistic-card';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, Sidebar, Header, StatisticCard, LoadingSpinner],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {

  loading          = signal(true);
  error            = signal(false);
  totalRequests    = signal(0);
  pendingCount     = signal(0);
  infoNeededCount  = signal(0);
  approvedCount    = signal(0);
  rejectedCount    = signal(0);

  constructor(private requestService: RequestService) {}

  ngOnInit(): void {
    this.requestService.getMyRequests().subscribe({
      next: (requests) => {
        this.totalRequests.set(requests.length);
        this.pendingCount.set(
          requests.filter(r =>
            ['PENDING_MANAGER', 'PENDING_APP_OWNER', 'PENDING_SECURITY'].includes(r.current_state)
          ).length
        );
        this.infoNeededCount.set(
          requests.filter(r => r.current_state === 'INFO_REQUESTED').length
        );
        this.approvedCount.set(requests.filter(r => r.current_state === 'APPROVED').length);
        this.rejectedCount.set(requests.filter(r => r.current_state === 'REJECTED').length);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Dashboard API error:', err);
        this.error.set(true);
        this.loading.set(false);
      }
    });
  }
}
