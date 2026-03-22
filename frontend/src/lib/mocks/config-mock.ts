export function configStatusMock() {
	return {
		claude_api_key_set: true,
		gemini_api_key_set: true,
		google_drive_credentials_set: true,
		google_drive_folder_id: 'mock-folder-id'
	};
}

export function pastasMock() {
	return [
		{ id: 'mock-1', name: 'Posts LinkedIn' },
		{ id: 'mock-2', name: 'Carrosséis IT Valley' }
	];
}
