// src/lib/services/AuthService.ts

import { AuthRepository } from '$lib/repositories/AuthRepository';
import type { AuthDTO } from '$lib/dtos/AuthDTO';
import type { UserDTO } from '$lib/dtos/UserDTO';
import type { LoginRequestDTO } from '$lib/dtos/LoginRequestDTO';
import type { CriarUsuarioDTO } from '$lib/dtos/CriarUsuarioDTO';
import type { EditarUsuarioDTO } from '$lib/dtos/EditarUsuarioDTO';

export class AuthService {
  static async login(email: string, password: string): Promise<{ success: boolean; data?: AuthDTO; error?: string }> {
    return AuthRepository.login(email, password);
  }

  static async me(): Promise<AuthDTO> {
    return AuthRepository.me();
  }

  static async listarUsuarios(): Promise<UserDTO[]> {
    return AuthRepository.listarUsuarios();
  }

  static async criarUsuario(dto: CriarUsuarioDTO): Promise<UserDTO> {
    if (!dto.isValid()) throw new Error('Dados invalidos');
    return AuthRepository.criarUsuario(dto.toPayload());
  }

  static async editarUsuario(dto: EditarUsuarioDTO): Promise<UserDTO> {
    if (!dto.isValid()) throw new Error('Dados invalidos');
    return AuthRepository.editarUsuario(dto.getUserId(), dto.toPayload());
  }

  static async desativarUsuario(userId: string): Promise<void> {
    return AuthRepository.desativarUsuario(userId);
  }

  static async reativarUsuario(userId: string): Promise<void> {
    return AuthRepository.reativarUsuario(userId);
  }

  static async convidarUsuario(payload: Record<string, any>): Promise<{ invite_token: string; invite_url: string; expires_at: string }> {
    return AuthRepository.convidarUsuario(payload);
  }

  static async aceitarConvite(token: string, password: string): Promise<AuthDTO> {
    return AuthRepository.aceitarConvite(token, password);
  }
}
