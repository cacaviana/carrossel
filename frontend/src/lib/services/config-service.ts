import { ConfigRepository } from '$lib/repositories/config-repository';
import type { KeysStatus, Pasta } from '$lib/repositories/config-repository';

export class ConfigService {
	static async carregarStatus(backendUrl: string): Promise<KeysStatus> {
		return ConfigRepository.getStatus(backendUrl);
	}

	static async salvarConfig(
		backendUrl: string,
		payload: Record<string, string>
	): Promise<KeysStatus> {
		if (Object.keys(payload).length > 0) {
			await ConfigRepository.save(backendUrl, payload);
		}
		return ConfigRepository.getStatus(backendUrl);
	}

	static async listarPastas(backendUrl: string): Promise<Pasta[]> {
		return ConfigRepository.listarPastas(backendUrl);
	}

	static async salvarPasta(backendUrl: string, folderId: string): Promise<KeysStatus> {
		await ConfigRepository.save(backendUrl, { google_drive_folder_id: folderId });
		return ConfigRepository.getStatus(backendUrl);
	}
}
