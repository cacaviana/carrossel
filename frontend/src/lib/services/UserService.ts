// src/lib/services/UserService.ts

import { UserRepository } from '$lib/repositories/UserRepository';
import type { UserDTO } from '$lib/dtos/UserDTO';

export class UserService {
  static async listarTodos(): Promise<UserDTO[]> {
    const users = await UserRepository.listar();
    return users.filter(u => u.isValid());
  }
}
