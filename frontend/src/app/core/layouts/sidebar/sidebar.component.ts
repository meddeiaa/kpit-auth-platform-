import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatRippleModule } from '@angular/material/core';

interface NavItem {
  label: string;
  icon: string;
  route?: string;
  badge?: {
    text: string;
    color: string;
  };
}

interface NavSection {
  title: string;
  items: NavItem[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatRippleModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {
  @Input() collapsed = false;
  /** Ouverture en mode tiroir (mobile) — piloté par le layout */
  @Input() mobileOpen = false;

  navigationSections: NavSection[] = [
    {
      title: 'DASHBOARDS',
      items: [
        {
          label: 'Overview',
          icon: 'insights',
          route: '/welcome'
        }
      ]
    },
    {
      title: 'TESTING',
      items: [
        {
          label: 'Test Cases',
          icon: 'fact_check',
          route: '/tests'
        },
        {
          label: 'Test Reports',
          icon: 'analytics',
          route: '',
          badge: { text: 'SOON', color: 'slate' }
        },
        {
          label: 'Test History',
          icon: 'history',
          route: '',
          badge: { text: 'SOON', color: 'slate' }
        }
      ]
    },
    {
      title: 'MANAGEMENT',
      items: [
        {
          label: 'Users',
          icon: 'people',
          route: '',
          badge: { text: 'SOON', color: 'slate' }
        },
        {
          label: 'Settings',
          icon: 'settings',
          route: '',
          badge: { text: 'SOON', color: 'slate' }
        }
      ]
    }
  ];

  constructor(private router: Router) {}

  navigateTo(item: NavItem): void {
    if (item.route) {
      this.router.navigate([item.route]);
    }
  }

  isRouteActive(route: string | undefined): boolean {
    if (!route) return false;
    return this.router.url.startsWith(route);
  }
}