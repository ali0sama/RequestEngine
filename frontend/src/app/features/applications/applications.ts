import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { Application } from '../../core/models';

@Component({
  selector: 'app-applications',
  standalone: true,
  imports: [CommonModule, RouterModule, Sidebar, Header, LoadingSpinner],
  templateUrl: './applications.html',
  styleUrl: './applications.css'
})
export class Applications implements OnInit {

  applications = signal<Application[]>([]);
  loading      = signal(true);
  error        = signal(false);

  constructor(private requestService: RequestService) {}

  ngOnInit(): void {
    this.requestService.getApplications().subscribe({
      next:  (data) => { this.applications.set(data); this.loading.set(false); },
      error: ()     => { this.error.set(true);         this.loading.set(false); }
    });
  }
}
