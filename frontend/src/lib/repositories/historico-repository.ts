import { browser } from '$app/environment';

const STORAGE_KEY = 'carrossel-historico';
const MAX_ITEMS = 50;

export class HistoricoRepository {
	static load(): Record<string, unknown>[] {
		if (!browser) return [];
		const saved = localStorage.getItem(STORAGE_KEY);
		if (!saved) return [];
		try {
			return JSON.parse(saved);
		} catch {
			return [];
		}
	}

	static save(items: Record<string, unknown>[]): void {
		if (!browser) return;
		localStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, MAX_ITEMS)));
	}

	static add(item: Record<string, unknown>): void {
		const items = HistoricoRepository.load();
		items.unshift({ ...item, createdAt: new Date().toISOString() });
		HistoricoRepository.save(items);
	}

	static remove(index: number): void {
		const items = HistoricoRepository.load();
		items.splice(index, 1);
		HistoricoRepository.save(items);
	}
}
