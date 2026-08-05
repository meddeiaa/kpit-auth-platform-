import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { WelcomeComponent } from './features/welcome/welcome.component';

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
    path: 'welcome',
    component: WelcomeComponent,
    title: 'Welcome - KPIT Auth Platform'
  },
  {
    path: '**',
    redirectTo: 'login'
  }
];