import { Component, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { SidebarComponent } from '../sidebar/sidebar.component';
import { HeaderComponent } from '../header/header.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, SidebarComponent, HeaderComponent],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss'
})
export class MainLayoutComponent {
  sidebarCollapsed = false;
  isMobileMenuOpen = false;

  /** Largeur max = mode "tiroir mobile" */
  private readonly mobileBreakpoint = 992;

  toggleMenu(): void {
    if (window.innerWidth <= this.mobileBreakpoint) {
      this.isMobileMenuOpen = !this.isMobileMenuOpen;
    } else {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    }
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen = false;
  }

  @HostListener('window:resize')
  onResize(): void {
    if (window.innerWidth > this.mobileBreakpoint && this.isMobileMenuOpen) {
      this.isMobileMenuOpen = false;
    }
  }
}