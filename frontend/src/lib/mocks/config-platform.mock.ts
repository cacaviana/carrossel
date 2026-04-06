export const platformRulesMock = [
  {
    plataforma: 'linkedin',
    max_caracteres_titulo: 150,
    max_caracteres_corpo: 3000,
    max_hashtags: 5,
    formatos_suportados: ['carrossel', 'post_unico'],
    specs: { aspect_ratio: '4:5', formato_imagem: 'PNG/JPG', tamanho_max: '10MB' }
  },
  {
    plataforma: 'instagram',
    max_caracteres_titulo: 125,
    max_caracteres_corpo: 2200,
    max_hashtags: 30,
    formatos_suportados: ['carrossel', 'post_unico', 'capa_reels'],
    specs: { aspect_ratio: '1:1 ou 4:5', formato_imagem: 'PNG/JPG', tamanho_max: '30MB' }
  },
  {
    plataforma: 'youtube',
    max_caracteres_titulo: 100,
    max_caracteres_corpo: 5000,
    max_hashtags: 15,
    formatos_suportados: ['thumbnail_youtube'],
    specs: { resolucao: '1280x720', formato_imagem: 'PNG/JPG', tamanho_max: '2MB' }
  }
];
