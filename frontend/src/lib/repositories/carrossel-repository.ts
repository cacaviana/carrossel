import { browser } from '$app/environment';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class CarrosselRepository {
	static async gerarConteudo(
		backendUrl: string,
		body: Record<string, unknown>,
		useCli: boolean
	): Promise<Record<string, unknown>> {
		if (USE_MOCK) {
			const { carrosselMock } = await import('$lib/mocks/carrossel-mock');
			return carrosselMock();
		}
		const endpoint = useCli ? '/api/gerar-conteudo-cli' : '/api/gerar-conteudo';
		const res = await fetch(`${backendUrl}${endpoint}`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body)
		});
		if (!res.ok) {
			const data = await res.json();
			throw new Error(data.detail || 'Erro ao gerar conteúdo');
		}
		return res.json();
	}

	static async gerarImagens(
		backendUrl: string,
		slides: Record<string, unknown>[],
		fotoCriador?: string
	): Promise<{ images: (string | null)[] }> {
		if (USE_MOCK) {
			const { imagensMock } = await import('$lib/mocks/carrossel-mock');
			return imagensMock(slides.length);
		}
		const res = await fetch(`${backendUrl}/api/gerar-imagem`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ slides, foto_criador: fotoCriador || undefined })
		});
		if (!res.ok) {
			const data = await res.json();
			throw new Error(data.detail || 'Erro ao gerar imagens');
		}
		return res.json();
	}

	static async gerarImagemSlide(
		backendUrl: string,
		slide: Record<string, unknown>,
		slideIndex: number,
		totalSlides: number,
		fotoCriador?: string,
		referenceImage?: string
	): Promise<{ image: string | null }> {
		if (USE_MOCK) {
			const { imagemSlideMock } = await import('$lib/mocks/carrossel-mock');
			return imagemSlideMock();
		}
		const res = await fetch(`${backendUrl}/api/gerar-imagem-slide`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				slide,
				slide_index: slideIndex,
				total_slides: totalSlides,
				foto_criador: fotoCriador || undefined,
				reference_image: referenceImage || undefined
			})
		});
		if (!res.ok) {
			const data = await res.json();
			throw new Error(data.detail || 'Erro ao gerar imagem');
		}
		return res.json();
	}

	static async salvarNoDrive(
		backendUrl: string,
		title: string,
		pdfBase64: string,
		imagesBase64: (string | null)[]
	): Promise<{ subfolder_name: string; web_view_link: string }> {
		const res = await fetch(`${backendUrl}/api/google-drive/carrossel`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				title,
				pdf_base64: pdfBase64,
				images_base64: imagesBase64
			})
		});
		if (!res.ok) {
			const data = await res.json();
			throw new Error(data.detail || 'Erro ao salvar no Drive');
		}
		return res.json();
	}
}
