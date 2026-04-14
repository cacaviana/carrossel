// src/lib/dtos/AuthDTO.ts

export type UserRole = 'admin' | 'copywriter' | 'designer' | 'reviewer' | 'viewer';

export class AuthDTO {
  readonly token: string;
  readonly user_id: string;
  readonly tenant_id: string;
  readonly email: string;
  readonly name: string;
  readonly avatar_url: string;
  readonly role: UserRole;

  constructor(data: Record<string, any>) {
    this.token = data.token ?? '';
    this.user_id = data.user_id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.email = data.email ?? '';
    this.name = data.name ?? '';
    this.avatar_url = data.avatar_url ?? '';
    this.role = data.role ?? 'viewer';
  }

  get iniciais(): string {
    return this.name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  get isAdmin(): boolean {
    return this.role === 'admin';
  }

  get canEdit(): boolean {
    return this.role !== 'viewer';
  }

  get canComment(): boolean {
    return this.role !== 'viewer';
  }

  get canCreateCard(): boolean {
    return this.role === 'admin' || this.role === 'copywriter';
  }

  get canManageUsers(): boolean {
    return this.role === 'admin';
  }

  get roleLabel(): string {
    const labels: Record<UserRole, string> = {
      admin: 'Admin',
      copywriter: 'Copywriter',
      designer: 'Designer',
      reviewer: 'Reviewer',
      viewer: 'Viewer'
    };
    return labels[this.role];
  }

  isValid(): boolean {
    return this.token.length > 0 && this.user_id.length > 0 && this.email.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      token: this.token,
      user_id: this.user_id,
      tenant_id: this.tenant_id,
      email: this.email,
      name: this.name,
      role: this.role
    };
  }
}
