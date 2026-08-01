import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';

import { Auth } from '../../core/auth';

function passwordsMatchValidator(control: AbstractControl): ValidationErrors | null {
  const newPassword = control.get('newPassword')?.value;
  const confirmPassword = control.get('confirmPassword')?.value;
  return newPassword === confirmPassword ? null : { passwordMismatch: true };
}

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './change-password.html',
  styleUrl: './change-password.css'
})
export class ChangePassword {

  form: FormGroup;

  loading = signal(false);

  errorMessage = signal('');

  successMessage = signal('');

  showOldPassword = signal(false);

  showNewPassword = signal(false);

  constructor(
    private fb: FormBuilder,
    private auth: Auth,
    private router: Router
  ) {

    this.form = this.fb.group({
      username: ['', Validators.required],
      oldPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    }, { validators: passwordsMatchValidator });

  }

  toggleOldPassword(): void {
    this.showOldPassword.update(v => !v);
  }

  toggleNewPassword(): void {
    this.showNewPassword.update(v => !v);
  }

  onSubmit(): void {

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    const { username, oldPassword, newPassword } = this.form.value;

    this.auth.login(username, oldPassword).pipe(
      switchMap(() => this.auth.changePassword(oldPassword, newPassword))
    ).subscribe({

      next: () => {

        this.loading.set(false);
        this.successMessage.set('Password updated. Redirecting to your dashboard…');

        setTimeout(() => this.router.navigate(['/dashboard']), 1200);

      },

      error: (err) => {

        this.loading.set(false);
        this.auth.clearTokens();

        if (err.status === 401) {

          this.errorMessage.set('Incorrect username or current password.');

        } else if (err.status === 400) {

          const detail = err.error?.detail;
          this.errorMessage.set(Array.isArray(detail) ? detail.join(' ') : (detail || 'Could not update password.'));

        } else if (err.status === 0) {

          this.errorMessage.set('Cannot connect to the server.');

        } else {

          this.errorMessage.set('Something went wrong. Please try again.');

        }

      }

    });

  }

}
