import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

import { environment } from '../../../environments/environment';
import {
  LoginRequest,
  RegisterRequest,
  LoginSuccessResponse,
  RegisterSuccessResponse,
  User
} from '../models/auth.model';

/**
 * Service d'authentification.
 * Gère toutes les opérations liées à l'auth :
 * - Login
 * - Register
 * - Logout
 * - Récupération de l'utilisateur courant
 */
@Injectable({
  providedIn: 'root'  // Ce service est disponible partout dans l'app
})
export class AuthService {
  
  // URL de base de l'API (vient de environment.ts)
  private apiUrl = environment.apiUrl;
  
  // Stockage de l'utilisateur courant
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Au démarrage, essayer de récupérer l'utilisateur depuis localStorage
    this.loadUserFromStorage();
  }

  /**
   * Se connecter avec un login et un mot de passe.
   * 
   * @param credentials - Les identifiants (login + password)
   * @returns Observable de la réponse
   */
  login(credentials: LoginRequest): Observable<LoginSuccessResponse> {
    const url = `${this.apiUrl}/auth/login`;
    
    return this.http.post<LoginSuccessResponse>(url, credentials).pipe(
      tap(response => {
        // Si succès, sauvegarder l'utilisateur
        if (response.success && response.user) {
          this.saveUser(response.user);
        }
      }),
      catchError(this.handleError)
    );
  }

  /**
   * Créer un nouveau compte utilisateur.
   * 
   * @param userData - Les données du nouvel utilisateur
   * @returns Observable de la réponse
   */
  register(userData: RegisterRequest): Observable<RegisterSuccessResponse> {
    const url = `${this.apiUrl}/auth/register`;
    
    return this.http.post<RegisterSuccessResponse>(url, userData).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Se déconnecter (efface les données locales).
   */
  logout(): void {
    // Supprimer l'utilisateur du localStorage
    localStorage.removeItem('currentUser');
    // Notifier tous les composants
    this.currentUserSubject.next(null);
  }

  /**
   * Récupérer l'utilisateur courant (synchrone).
   */
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Vérifier si l'utilisateur est connecté.
   */
  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null;
  }

  /**
   * Sauvegarder l'utilisateur dans localStorage + BehaviorSubject.
   */
  private saveUser(user: User): void {
    localStorage.setItem('currentUser', JSON.stringify(user));
    this.currentUserSubject.next(user);
  }

  /**
   * Charger l'utilisateur depuis localStorage (au démarrage).
   */
  private loadUserFromStorage(): void {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      try {
        const user: User = JSON.parse(userStr);
        this.currentUserSubject.next(user);
      } catch (e) {
        console.error('Error parsing user from storage:', e);
        localStorage.removeItem('currentUser');
      }
    }
  }

  /**
   * Gérer les erreurs HTTP de manière centralisée.
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Erreur côté client (réseau, etc.)
      errorMessage = `Client error: ${error.error.message}`;
    } else {
      // Erreur côté serveur
      if (error.error && error.error.error) {
        // Le backend a renvoyé un message d'erreur
        errorMessage = error.error.error;
      } else {
        errorMessage = `Server error: ${error.status} - ${error.statusText}`;
      }
    }

    console.error('AuthService error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}