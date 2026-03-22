import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface AppConfig {
	fotoCriadorBase64: string;
	backendUrl: string;
}

function getDefaultBackendUrl(): string {
	if (typeof window === 'undefined') return 'http://localhost:8000';
	return `${window.location.protocol}//${window.location.hostname}:8000`;
}

const defaultConfig: AppConfig = {
	fotoCriadorBase64: '',
	backendUrl: getDefaultBackendUrl()
};

function loadConfig(): AppConfig {
	if (!browser) return defaultConfig;
	const saved = localStorage.getItem('carrossel-config');
	if (saved) {
		try {
			const parsed = JSON.parse(saved);
			// Se o backendUrl salvo aponta pra localhost mas o acesso é remoto, ignora o salvo
			const isRemoteAccess = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
			const savedUrlIsLocal = parsed.backendUrl?.includes('localhost') || parsed.backendUrl?.includes('127.0.0.1');
			if (isRemoteAccess && savedUrlIsLocal) {
				parsed.backendUrl = getDefaultBackendUrl();
			}
			return { ...defaultConfig, ...parsed };
		} catch {
			return defaultConfig;
		}
	}
	return defaultConfig;
}

function createConfigStore() {
	const { subscribe, set, update } = writable<AppConfig>(loadConfig());

	return {
		subscribe,
		set(value: AppConfig) {
			if (browser) {
				localStorage.setItem('carrossel-config', JSON.stringify(value));
			}
			set(value);
		},
		update(fn: (config: AppConfig) => AppConfig) {
			update((current) => {
				const updated = fn(current);
				if (browser) {
					localStorage.setItem('carrossel-config', JSON.stringify(updated));
				}
				return updated;
			});
		},
		reset() {
			if (browser) {
				localStorage.removeItem('carrossel-config');
			}
			set(defaultConfig);
		}
	};
}

export const config = createConfigStore();
