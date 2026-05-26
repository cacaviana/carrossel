// src/lib/dtos/CriarUsuarioDTO.ts

import type { UserRole } from '$lib/dtos/AuthDTO';

export class CriarUsuarioDTO {
  readonly name: string;
  readonly email: string;
  readonly password: string;
  readonly role: UserRole;

  constructor(data: Record<string, any>) {
    this.name = data.name ?? '';
    this.email = data.email ?? '';
    this.password = data.password ?? '';
    this.role = data.role ?? 'viewer';
  }

  get emailValido(): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email);
  }

  get senhaForte(): boolean {
    const s = this.password;
    return s.length >= 8
      && /[A-Z]/.test(s)
      && /[0-9]/.test(s)
      && /[^A-Za-z0-9]/.test(s);
  }

  get errosSenha(): string[] {
    const erros: string[] = [];
    if (this.password.length < 8) erros.push('Minimo 8 caracteres');
    if (!/[A-Z]/.test(this.password)) erros.push('1 letra maiuscula');
    if (!/[0-9]/.test(this.password)) erros.push('1 numero');
    if (!/[^A-Za-z0-9]/.test(this.password)) erros.push('1 caractere especial');
    return erros;
  }

  get nomeValido(): boolean {
    return this.name.trim().length >= 2;
  }

  isValid(): boolean {
    return this.nomeValido && this.emailValido && this.senhaForte;
  }

  toPayload(): Record<string, any> {
    return {
      name: this.name,
      email: this.email,
      password: this.password,
      role: this.role
    };
  }
}
