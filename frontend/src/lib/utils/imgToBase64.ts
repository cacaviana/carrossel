import { API_BASE } from '$lib/api';

/** Converte URL de imagem para data URI base64. Fallback via backend para CORS. */
export async function imgToBase64(src: string): Promise<string> {
  if (!src || src.startsWith('data:')) return src;
  try {
    const res = await fetch(src, { credentials: 'include' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve((reader.result as string) || src);
      reader.onerror = () => resolve(src);
      reader.readAsDataURL(blob);
    });
  } catch {
    try {
      const res = await fetch(`${API_BASE}/api/image-to-base64`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: src }),
      });
      if (res.ok) {
        const data = await res.json();
        return data.data_uri || src;
      }
    } catch {}
    return src;
  }
}
