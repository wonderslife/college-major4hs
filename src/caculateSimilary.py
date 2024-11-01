from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from sentence_transformers import  util  
from sentence_transformers import SentenceTransformer as SBert
import Levenshtein


def calculate_similarity_bag_of_words(sentence1, sentence2):
    vectorizer = CountVectorizer().fit([sentence1, sentence2])
    vectors = vectorizer.transform([sentence1, sentence2])
    similarity = cosine_similarity(vectors)
    return similarity[0][1]

def cosine_similarity_score(str1, str2):
    vectorizer = CountVectorizer().fit_transform([str1, str2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0][1]

def jaccard_similarity(str1, str2):
    set1 = set(str1.replace("(", "").replace(")", "").replace("；", ";").replace("，", ",").split(";"))
    set2 = set(str2.replace("(", "").replace(")", "").replace("；", ";").replace("，", ",").split("、"))
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union != 0 else 0

str1_orginal = "管理科学与工程类(120102-信息管理与信息系统;120105-工程造价;120103-工程管理)"
str1 = re.sub(r'\d+-', '', str1_orginal)# 使用正则表达式去掉数字和横线
str2_original = "管理科学与工程类(信息管理与信息系统、工程管理、工程造价)"
str2 = re.sub(r'\d+-', '', str2_original)
similarity = jaccard_similarity(str1, str2)
print(f"Jaccard 相似度: {similarity:.2f}")

similarity3 = jaccard_similarity(str1, str2)
print(f"词袋 相似度: {similarity3:.2f}")

similarity1 = cosine_similarity_score(str1, str2)
print(f"余弦相似度: {similarity1:.2f}")

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([str1, str2])
similarity2 = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
print(f"TF-IDF 余弦相似度: {similarity2[0][0]:.2f}")


model = SBert("C:\\Users\\wonder\\Downloads\\paraphrase-multilingual-MiniLM-L12-v2")
embeddings = model.encode([str1, str2])
similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
print(f"句子嵌入余弦相似度: {similarity.item():.2f}")

distance = Levenshtein.distance(str1, str2)
similarity = 1 - distance / max(len(str1), len(str2))
print(f"Levenshtein 相似度: {similarity:.2f}")
