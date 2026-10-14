/**
 * Modèles TypeScript pour l'authentification.
 * Ces interfaces définissent la structure des données
 * échangées avec le backend Flask.
 */

// Données envoyées lors du login
export interface LoginRequest {
  login: string;
  password: string;
}

// Données envoyées lors du register
export interface RegisterRequest {
  first_name: string;
  last_name: string;
  email: string;
  login: string;
  password: string;
  role?: string;  // Optionnel (défaut : viewer)
}

// Utilisateur retourné par le backend
export interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  login: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Réponse du backend pour login (succès)
export interface LoginSuccessResponse {
  success: boolean;
  message: string;
  user?: User;
  access_token?: string;
  
  // --- LAYER 2 & 3 : AI & 2FA EMAIL ---
  require_2fa?: boolean;
  login?: string;
  masked_email?: string;       // ← AJOUT ICI : Corrige l'erreur TypeScript !
  anomaly_score?: number;
  is_anomaly?: boolean;
}

export interface Verify2FARequest {
  login: string;
  otp_code: string;
}


export interface MeResponse {
  success: boolean;
  user: User;
}

// Réponse du backend pour register (succès)
export interface RegisterSuccessResponse {
  success: true;
  message: string;
  user: User;
}

// Réponse d'erreur du backend
export interface ErrorResponse {
  success: false;
  error: string;
}