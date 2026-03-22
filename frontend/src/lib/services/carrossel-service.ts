import { CarrosselRepository } from '$lib/repositories/carrossel-repository';
import { HistoricoRepository } from '$lib/repositories/historico-repository';

export class CarrosselService {
	static async gerarConteudo(
		backendUrl: string,
		body: Record<string, unknown>,
		useCli: boolean
	): Promise<Record<string, unknown>> {
		const result = await CarrosselRepository.gerarConteudo(backendUrl, body, useCli);
		const withDate = { ...result, createdAt: new Date().toISOString() };
		HistoricoRepository.add(result);
		return withDate;
	}

	static async gerarImagens(
		backendUrl: string,
		slides: Record<string, unknown>[],
		fotoCriador?: string
	): Promise<(string | null)[]> {
		const result = await CarrosselRepository.gerarImagens(backendUrl, slides, fotoCriador);
		return result.images;
	}

	static async gerarImagemSlide(
		backendUrl: string,
		slide: Record<string, unknown>,
		slideIndex: number,
		totalSlides: number,
		fotoCriador?: string
	): Promise<string | null> {
		const result = await CarrosselRepository.gerarImagemSlide(
			backendUrl, slide, slideIndex, totalSlides, fotoCriador
		);
		return result.image;
	}

	static async salvarNoDrive(
		backendUrl: string,
		title: string,
		pdfBase64: string,
		imagesBase64: (string | null)[]
	): Promise<string> {
		const result = await CarrosselRepository.salvarNoDrive(
			backendUrl, title, pdfBase64, imagesBase64
		);
		return result.web_view_link;
	}

	static async exportarPdf(
		slides: { imageBase64?: string }[],
		title: string
	): Promise<void> {
		const imagesWithData = slides.filter((s) => s.imageBase64);
		if (imagesWithData.length === 0) throw new Error('Gere as imagens primeiro.');

		const { jsPDF } = await import('jspdf');
		const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [1080, 1350] });
		let first = true;
		for (const slide of slides) {
			if (!slide.imageBase64) continue;
			if (!first) pdf.addPage([1080, 1350]);
			pdf.addImage(slide.imageBase64, 'PNG', 0, 0, 1080, 1350);
			first = false;
		}
		pdf.save(`${title || 'carrossel'}.pdf`);
	}
}
