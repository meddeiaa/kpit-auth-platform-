import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

// Angular Material imports
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

// Services et modèles
import { AuthService } from '../../../core/services/auth.service';
import { LoginRequest } from '../../../core/models/auth.model';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginForm: FormGroup;
  hidePassword = true;
  errorMessage = '';
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService  // ← NOUVEAU : Injection du service
  ) {
    this.loginForm = this.fb.group({
      login: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.errorMessage = 'Please fill in all fields correctly';
      this.markFormFieldsAsTouched();
      return;
    }

    // Réinitialiser l'état
    this.isLoading = true;
    this.errorMessage = '';

    // Préparer les credentials
    const credentials: LoginRequest = {
      login: this.loginForm.value.login,
      password: this.loginForm.value.password
    };

    console.log('🔐 Attempting login for:', credentials.login);

    // Appeler le service (vraie requête HTTP à Flask !)
    this.authService.login(credentials).subscribe({
      next: (response) => {
        // ✅ SUCCÈS
        console.log('✅ Login successful:', response);
        this.isLoading = false;
        this.router.navigate(['/welcome']);
      },
      error: (error) => {
        // ❌ ERREUR
        console.error('❌ Login failed:', error);
        this.isLoading = false;
        this.errorMessage = error.message || 'Login failed. Please try again.';
      }
    });
  }

  private markFormFieldsAsTouched(): void {
    Object.keys(this.loginForm.controls).forEach(key => {
      this.loginForm.get(key)?.markAsTouched();
    });
  }

  get loginField() {
    return this.loginForm.get('login');
  }

  get passwordField() {
    return this.loginForm.get('password');
  }
}