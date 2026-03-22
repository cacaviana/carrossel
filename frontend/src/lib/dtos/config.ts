export class AppConfigDTO {
	readonly fotoCriadorBase64: string;
	readonly backendUrl: string;

	constructor(data: Record<string, unknown>) {
		this.fotoCriadorBase64 = (data.fotoCriadorBase64 as string) ?? '';
		this.backendUrl = (data.backendUrl as string) ?? 'http://localhost:8000';
	}

	isValid(): boolean {
		return this.backendUrl.startsWith('http');
	}

	toPayload(): Record<string, unknown> {
		return {
			fotoCriadorBase64: this.fotoCriadorBase64,
			backendUrl: this.backendUrl
		};
	}
}
