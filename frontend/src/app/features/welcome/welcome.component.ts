import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';

import { AuthService } from '../../core/services/auth.service';
import { User } from '../../core/models/auth.model';

@Component({
  selector: 'app-welcome',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule
  ],
  templateUrl: './welcome.component.html',
  styleUrl: './welcome.component.scss'
})
export class WelcomeComponent implements OnInit {
  user: User | null = null;
  loginTime = new Date();

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Récupérer l'utilisateur courant depuis le service
    this.user = this.authService.getCurrentUser();

    // Si pas connecté, rediriger vers login
    if (!this.user) {
      console.warn('⚠️ No user found, redirecting to login');
      this.router.navigate(['/login']);
    } else {
      console.log('👋 Welcome:', this.user);
    }
  }

  onLogout(): void {
    console.log('👋 Logging out...');
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getRoleColor(role: string): string {
    switch (role) {
      case 'admin': return 'warn';
      case 'tester': return 'accent';
      case 'viewer': return 'primary';
      default: return '';
    }
  }

  getRoleIcon(role: string): string {
    switch (role) {
      case 'admin': return 'admin_panel_settings';
      case 'tester': return 'science';
      case 'viewer': return 'visibility';
      default: return 'person';
    }
  }
}