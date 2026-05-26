/** Dimensoes por formato — fonte unica de verdade (mirror do backend utils/dimensions.py). */

export interface FormatDims {
  w: number;
  h: number;
  ratio: string;
  cssRatio: string;
  label: string;
}

export const FORMAT_DIMS: Record<string, FormatDims> = {
  carrossel:         { w: 1080, h: 1350, ratio: '4:5',  cssRatio: '4/5',  label: 'portrait' },
  post_unico:        { w: 1080, h: 1080, ratio: '1:1',  cssRatio: '1/1',  label: 'square' },
  thumbnail_youtube: { w: 1280, h: 720,  ratio: '16:9', cssRatio: '16/9', label: 'landscape' },
  capa_reels:        { w: 1080, h: 1920, ratio: '9:16', cssRatio: '9/16', label: 'tall portrait' },
};

export function getDims(formato: string): FormatDims {
  return FORMAT_DIMS[formato] ?? FORMAT_DIMS.carrossel;
}
