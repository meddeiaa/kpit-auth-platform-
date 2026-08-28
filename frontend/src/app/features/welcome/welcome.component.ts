import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AuthService } from '../../core/services/auth.service';
import { TestManagementService } from '../../core/services/test-management.service';
import { User } from '../../core/models/auth.model';
import { forkJoin, Subscription } from 'rxjs';

@Component({
  selector: 'app-welcome',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './welcome.component.html',
  styleUrl: './welcome.component.scss'
})
export class WelcomeComponent implements OnInit, OnDestroy {
  user: User | null = null;
  loginTime = new Date();

  // Vraies données dynamiques du backend
  totalTests = 0;
  totalSuites = 0;
  totalTags = 0;
  isLoadingStats = true;
  
  private dataSub!: Subscription;

  constructor(
    private authService: AuthService,
    private testService: TestManagementService, // Injection du service
    private router: Router
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    if (!this.user) {
      this.router.navigate(['/login']);
      return;
    }

    this.loadRealDashboardData();
  }

  loadRealDashboardData(): void {
    // forkJoin permet de lancer plusieurs requêtes HTTP en parallèle 
    // et d'attendre que TOUTES soient terminées avant de continuer.
    this.dataSub = forkJoin({
      casesData: this.testService.getAllTestCases(),
      suitesData: this.testService.getSuites()
    }).subscribe({
      next: (results) => {
        this.totalTests = results.casesData.count;
        this.totalTags = results.casesData.available_tags.length;
        this.totalSuites = results.suitesData.count;
        this.isLoadingStats = false;
      },
      error: (err) => {
        console.error('Failed to load dashboard data', err);
        this.isLoadingStats = false;
      }
    });
  }

  goToTestManagement(): void {
    this.router.navigate(['/tests']);
  }

  onLogout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  ngOnDestroy(): void {
    if (this.dataSub) {
      this.dataSub.unsubscribe(); // Éviter les fuites de mémoire
    }
  }
}