// src/lib/services/AuthService.ts

import { AuthRepository } from '$lib/repositories/AuthRepository';
import type { AuthDTO } from '$lib/dtos/AuthDTO';

export class AuthService {
  static async login(email: string, password: string): Promise<{ success: boolean; data?: AuthDTO; error?: string }> {
    return AuthRepository.login(email, password);
  }
}
