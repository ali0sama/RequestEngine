import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { AccessRequest } from '../../core/models';
import { statusLabel, statusClass } from '../../core/workflow';

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

  statusLabel = statusLabel;
  statusClass = statusClass;
}
