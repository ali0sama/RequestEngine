import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

import { Sidebar } from '../../shared/sidebar/sidebar';
import { Header } from '../../shared/header/header';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { RequestService } from '../../core/request.service';
import { Application } from '../../core/models';

@Component({
  selector: 'app-create-request',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, Sidebar, Header, LoadingSpinner],
  templateUrl: './create-request.html',
  styleUrl: './create-request.css'
})
export class CreateRequest implements OnInit {

  form: FormGroup;

  applications  = signal<Application[]>([]);
  loadingApps   = signal(true);
  submitting    = signal(false);
  appsError     = signal(false);
  submitError   = signal('');

  constructor(
    private fb: FormBuilder,
    private requestService: RequestService,
    private router: Router
  ) {
    this.form = this.fb.group({
      application:   [null, Validators.required],
      justification: ['',   [Validators.required, Validators.minLength(10)]]
    });
  }

  ngOnInit(): void {
    this.requestService.getApplications().subscribe({
      next:  (apps) => { this.applications.set(apps); this.loadingApps.set(false); },
      error: ()     => { this.appsError.set(true);    this.loadingApps.set(false); }
    });
  }

  get selectedApp(): Application | null {
    const id = this.form.get('application')?.value;
    return this.applications().find(a => a.id === +id) ?? null;
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting.set(true);
    this.submitError.set('');

    const { application, justification } = this.form.value;

    this.requestService.createRequest(+application, justification).subscribe({
      next: (req) => {
        this.submitting.set(false);
        this.router.navigate(['/requests', req.id]);
      },
      error: () => {
        this.submitting.set(false);
        this.submitError.set('Failed to create request. Please try again.');
      }
    });
  }
}
