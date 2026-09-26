import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { WelcomeComponent } from './features/welcome/welcome.component';
import { TestManagementComponent } from './features/test-management/test-management.component';
import { MainLayoutComponent } from './core/layouts/main-layout/main-layout.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: LoginComponent,
    title: 'Login - KPIT Auth Platform'
  },
 {
    path: '',
    component: MainLayoutComponent,
    children: [
      {
        path: 'welcome',
        component: WelcomeComponent,
        title: 'Dashboard - KPIT Test Manager'
      },
      {
        path: 'tests',
        component: TestManagementComponent,
        title: 'Test Cases - KPIT Test Manager'
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'login'
  }


];