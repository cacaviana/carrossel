// src/lib/dtos/EditarUsuarioDTO.ts

import type { UserRole } from '$lib/dtos/AuthDTO';

export class EditarUsuarioDTO {
  readonly user_id: string;
  readonly name: string;
  readonly role: UserRole;
  readonly avatar_url: string;

  constructor(data: Record<string, any>) {
    this.user_id = data.user_id ?? '';
    this.name = data.name ?? '';
    this.role = data.role ?? 'viewer';
    this.avatar_url = data.avatar_url ?? '';
  }

  get nomeValido(): boolean {
    return this.name.trim().length >= 2;
  }

  getUserId(): string {
    return this.user_id;
  }

  isValid(): boolean {
    return this.user_id.length > 0 && this.nomeValido;
  }

  toPayload(): Record<string, any> {
    return {
      name: this.name,
      role: this.role,
      avatar_url: this.avatar_url
    };
  }
}
