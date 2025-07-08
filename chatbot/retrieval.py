from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class FAQRetriever:
    def __init__(self, faq_path):
        with open(faq_path, "r", encoding="utf-8") as f:
            self.faq_data = json.load(f)
        self.questions = [item["question"] for item in self.faq_data]
        self.answers = [item["answer"] for item in self.faq_data]

        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.questions)

    def get_answer(self, question):
        question_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(question_vec, self.question_vectors)
        best_idx = scores.argmax()
        best_score = scores[0][best_idx]
        if best_score > 0.2:  # threshold có thể chỉnh
            return self.answers[best_idx]
        return "Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. Vui lòng hỏi lại rõ hơn."
