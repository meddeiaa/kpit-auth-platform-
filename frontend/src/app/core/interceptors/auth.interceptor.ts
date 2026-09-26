import {
  HttpInterceptorFn,
  HttpErrorResponse
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

/**
 * Interceptor Auth — Layer 1
 *
 * REQUEST  : ajoute Authorization: Bearer <access_token>
 * RESPONSE : si JWT invalide/expiré (401/422) → logout + redirect /login
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const snackBar = inject(MatSnackBar);

  const token = authService.getToken();

  // --- REQUEST : attacher le Bearer ---
  let authReq = req;
  if (token) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  // --- RESPONSE : surveiller 401 / 422 ---
  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      const url = req.url || '';

      // Ne pas déconnecter sur échec de login/register (mauvais mdp = 401 aussi)
      const isAuthEntryPoint =
        url.includes('/auth/login') || url.includes('/auth/register');

      // Flask-JWT-Extended : 401 classique ; parfois 422 si token mal formé
      const isUnauthorized =
        error.status === 401 || error.status === 422;

      if (isUnauthorized && !isAuthEntryPoint) {
        // Évite boucle si déjà sur login
        const alreadyOnLogin = router.url.startsWith('/login');

        authService.logout();

        if (!alreadyOnLogin) {
          snackBar.open(
            'Session expired or invalid. Please sign in again.',
            'Close',
            {
              duration: 4500,
              horizontalPosition: 'right',
              verticalPosition: 'top',
              panelClass: ['snackbar-warning']
            }
          );
          router.navigate(['/login']);
        }
      }

      return throwError(() => error);
    })
  );
};