import { browser } from '$app/environment';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export interface KeysStatus {
	claude_api_key_set: boolean;
	gemini_api_key_set: boolean;
	google_drive_credentials_set: boolean;
	google_drive_folder_id: string;
}

export interface Pasta {
	id: string;
	name: string;
}

export class ConfigRepository {
	static async getStatus(backendUrl: string): Promise<KeysStatus> {
		if (USE_MOCK) {
			const { configStatusMock } = await import('$lib/mocks/config-mock');
			return configStatusMock();
		}
		const res = await fetch(`${backendUrl}/api/config`);
		if (!res.ok) throw new Error('Erro ao buscar status');
		return res.json();
	}

	static async save(
		backendUrl: string,
		payload: Record<string, string>
	): Promise<void> {
		if (USE_MOCK) return;
		const res = await fetch(`${backendUrl}/api/config`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		});
		if (!res.ok) throw new Error('Erro ao salvar no servidor');
	}

	static async listarPastas(backendUrl: string): Promise<Pasta[]> {
		if (USE_MOCK) {
			const { pastasMock } = await import('$lib/mocks/config-mock');
			return pastasMock();
		}
		const res = await fetch(`${backendUrl}/api/drive/pastas`);
		if (!res.ok) {
			const d = await res.json();
			throw new Error(d.detail || 'Erro ao listar pastas');
		}
		return res.json();
	}
}
