// src/lib/dtos/LoginRequestDTO.ts

export class LoginRequestDTO {
  readonly email: string;
  readonly password: string;

  constructor(data: Record<string, any>) {
    this.email = data.email ?? '';
    this.password = data.password ?? '';
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

  isValid(): boolean {
    return this.emailValido && this.senhaForte;
  }

  toPayload(): Record<string, any> {
    return { email: this.email, password: this.password };
  }
}
