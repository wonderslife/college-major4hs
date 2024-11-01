from sentence_transformers.util import cos_sim  
from sentence_transformers import SentenceTransformer as SBert

#model = SBert('paraphrase-multilingual-MiniLM-L12-v2')

model = SBert("C:\\Users\\wonder\\Downloads\\paraphrase-multilingual-MiniLM-L12-v2")

# Two lists of sentences
sentences1 = ['管理科学与工程类(信息管理与信息系统;工程造价;工程管理)']

sentences2 = ['管理科学与工程类(信息管理与信息系统、工程管理、工程造价)']

# Compute embedding for both lists
embeddings1 = model.encode(sentences1)
embeddings2 = model.encode(sentences2)

# Compute cosine-similarits
cosine_scores = cos_sim(embeddings1, embeddings2)
print(f"句子嵌入余弦相似度: {cosine_scores.item():.2f}")

