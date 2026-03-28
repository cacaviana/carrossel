import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface FotoItem {
	id: string;
	name: string;
	dataUrl: string;
	createdAt: string;
}

const STORAGE_KEY = 'carrossel-fotos';

function loadFotos(): FotoItem[] {
	if (!browser) return [];
	const saved = localStorage.getItem(STORAGE_KEY);
	if (saved) {
		try { return JSON.parse(saved); } catch { return []; }
	}
	return [];
}

function saveFotos(fotos: FotoItem[]) {
	if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(fotos));
}

function createFotosStore() {
	const { subscribe, set, update } = writable<FotoItem[]>(loadFotos());

	return {
		subscribe,
		add(file: File): Promise<void> {
			return new Promise((resolve) => {
				const reader = new FileReader();
				reader.onload = () => {
					update((fotos) => {
						const novo: FotoItem = {
							id: crypto.randomUUID(),
							name: file.name,
							dataUrl: reader.result as string,
							createdAt: new Date().toISOString(),
						};
						const updated = [...fotos, novo];
						saveFotos(updated);
						return updated;
					});
					resolve();
				};
				reader.readAsDataURL(file);
			});
		},
		remove(id: string) {
			update((fotos) => {
				const updated = fotos.filter((f) => f.id !== id);
				saveFotos(updated);
				return updated;
			});
		},
		clear() {
			set([]);
			saveFotos([]);
		},
	};
}

export const fotos = createFotosStore();
