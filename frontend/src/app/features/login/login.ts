import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { Auth } from '../../core/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {

  loginForm: FormGroup;

  loading = false;

  errorMessage = '';

  showPassword = false;

  constructor(
    private fb: FormBuilder,
    private auth: Auth,
    private router: Router
  ) {

    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });

  }

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {

  if (this.loginForm.invalid) {
    this.loginForm.markAllAsTouched();
    return;
  }

  this.loading = true;
  this.errorMessage = '';

  const { username, password } = this.loginForm.value;

  this.auth.login(username, password).subscribe({

    next: () => {

      this.loading = false;

      this.router.navigate(['/dashboard']);

    },

    error: (err) => {

      this.loading = false;

      if (err.status === 401) {

        this.errorMessage = 'Incorrect username or password.';

      } else if (err.status === 0) {

        this.errorMessage = 'Cannot connect to the server.';

      } else {

        this.errorMessage = 'Something went wrong. Please try again.';

      }

      // Optional: clear only the password field
      this.loginForm.patchValue({
        password: ''
      });

    }

  });

}

}