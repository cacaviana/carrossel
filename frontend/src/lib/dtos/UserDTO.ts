// src/lib/dtos/UserDTO.ts

import type { UserRole } from '$lib/dtos/AuthDTO';

export class UserDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly email: string;
  readonly name: string;
  readonly avatar_url: string;
  readonly role: UserRole;
  readonly created_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.email = data.email ?? '';
    this.name = data.name ?? '';
    this.avatar_url = data.avatar_url ?? '';
    this.role = data.role ?? 'viewer';
    this.created_at = data.created_at ?? '';
    this.deleted_at = data.deleted_at ?? '';
  }

  get iniciais(): string {
    return this.name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  get isActive(): boolean {
    return this.deleted_at.length === 0;
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

  get roleBadgeColor(): string {
    const colors: Record<UserRole, string> = {
      admin: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
      copywriter: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
      designer: 'bg-pink-500/10 text-pink-600 border-pink-500/20',
      reviewer: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
      viewer: 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    };
    return colors[this.role];
  }

  isValid(): boolean {
    return this.id.length > 0 && this.email.length > 0 && this.name.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      email: this.email,
      name: this.name,
      avatar_url: this.avatar_url,
      role: this.role
    };
  }
}
