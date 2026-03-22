export interface Disciplina {
	id: string;
	nome: string;
	techs: string[];
	descricao: string;
}

export const disciplinas: Disciplina[] = [
	{
		id: 'D1',
		nome: 'Linguagens',
		techs: ['YOLO', 'OpenCV', 'Face Recognition', 'TensorFlow', 'Scikit-learn', 'pandas', 'NumPy'],
		descricao: 'Computer Vision, processamento de imagem e libs fundamentais'
	},
	{
		id: 'D2',
		nome: 'ETL',
		techs: ['Pipeline de dados', 'Talend', 'Apache NiFi', 'Limpeza de dados'],
		descricao: 'Extração, transformação e carga de dados'
	},
	{
		id: 'D3',
		nome: 'Fundamentos ML',
		techs: ['Random Forest', 'XGBoost', 'SVM', 'KNN'],
		descricao: 'Algoritmos clássicos de Machine Learning'
	},
	{
		id: 'D4',
		nome: 'Modelagem Preditiva',
		techs: ['Feature Engineering', 'Feature Selection', 'Regularização', 'Hiperparâmetros'],
		descricao: 'Engenharia e seleção de features, tuning de modelos'
	},
	{
		id: 'D5',
		nome: 'Deep Learning',
		techs: ['Transfer Learning', 'Fine-tuning', 'CNNs', 'RNNs', 'LSTM', 'Keras'],
		descricao: 'Redes neurais profundas e arquiteturas avançadas'
	},
	{
		id: 'D6',
		nome: 'NLP',
		techs: ['Whisper', 'Tokenização', 'Embeddings', 'Sentiment Analysis', 'NER'],
		descricao: 'Processamento de linguagem natural'
	},
	{
		id: 'D7',
		nome: 'IA Generativa',
		techs: ['GPT', 'Claude', 'LLMs', 'RAG', 'LangChain', 'LangGraph', 'Agentes', 'LoRA'],
		descricao: 'Modelos generativos, RAG, agentes e fine-tuning'
	},
	{
		id: 'D8',
		nome: 'Cloud',
		techs: ['AWS', 'Azure', 'GCP', 'Serverless ML', 'Lambda', 'SageMaker'],
		descricao: 'Deploy e infraestrutura cloud para ML'
	},
	{
		id: 'D9',
		nome: 'ML em Produção',
		techs: ['Model Monitoring', 'Data Drift', 'MLOps', 'CI/CD', 'A/B Testing'],
		descricao: 'Monitoramento, MLOps e ciclo de vida de modelos'
	}
];
