import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface FotoItem {
	id: string;
	name: string;
	dataUrl: string;
	createdAt: string;
}

const STORAGE_KEY = 'carrossel-fotos';
const PRINCIPAL_KEY = 'carrossel-foto-principal';

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

function loadPrincipalId(): string {
	if (!browser) return '';
	return localStorage.getItem(PRINCIPAL_KEY) || '';
}

function savePrincipalId(id: string) {
	if (browser) localStorage.setItem(PRINCIPAL_KEY, id);
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
						// Se for a primeira foto, define como principal automaticamente
						if (updated.length === 1) {
							savePrincipalId(novo.id);
							fotoPrincipalId.set(novo.id);
						}
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
				// Se removeu a principal, limpa
				if (loadPrincipalId() === id) {
					const newPrincipal = updated.length > 0 ? updated[0].id : '';
					savePrincipalId(newPrincipal);
					fotoPrincipalId.set(newPrincipal);
				}
				return updated;
			});
		},
		clear() {
			set([]);
			saveFotos([]);
			savePrincipalId('');
			fotoPrincipalId.set('');
		},
	};
}

function createPrincipalStore() {
	const { subscribe, set } = writable<string>(loadPrincipalId());

	return {
		subscribe,
		set(id: string) {
			savePrincipalId(id);
			set(id);
		},
	};
}

export const fotos = createFotosStore();
export const fotoPrincipalId = createPrincipalStore();
