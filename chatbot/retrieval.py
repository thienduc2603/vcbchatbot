from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re
import random

class FAQRetriever:
    def __init__(self, faq_path):
        with open(faq_path, "r", encoding="utf-8") as f:
            self.faq_data = json.load(f)
        self.questions = [item["question"] for item in self.faq_data]
        self.answers = [item["answer"] for item in self.faq_data]

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Sử dụng unigram và bigram
            max_features=5000,
            stop_words=None  # Giữ stop words vì tiếng Việt
        )
        self.question_vectors = self.vectorizer.fit_transform(self.questions)
        
        # Templates for natural responses
        self.greeting_templates = [
            "Chào bạn! ",
            "Xin chào! ",
            "Cảm ơn bạn đã liên hệ. ",
            ""
        ]
        
        self.closing_templates = [
            " Bạn có cần hỗ trợ thêm gì khác không?",
            " Nếu có thắc mắc gì thêm, hãy hỏi tôi nhé!",
            " Tôi có thể giúp gì thêm cho bạn?",
            ""
        ]
        
        # Response templates by category
        self.response_templates = {
            "fee": {
                "intro": ["Về vấn đề phí mà bạn hỏi", "Liên quan đến phí", "Đối với khoản phí này"],
                "outro": ["Hy vọng thông tin này hữu ích cho bạn", "Bạn có thể tham khảo thêm với hotline nếu cần"]
            },
            "payment": {
                "intro": ["Về cách thanh toán", "Đối với thanh toán", "Liên quan đến việc thanh toán"],
                "outro": ["Chúc bạn thực hiện giao dịch thành công", "Nếu gặp khó khăn, hãy liên hệ hotline nhé"]
            },
            "card": {
                "intro": ["Về thẻ của bạn", "Đối với thẻ tín dụng", "Liên quan đến thẻ"],
                "outro": ["Bạn có thể quản lý thẻ qua app VCB Mobile Banking", "Nếu cần hỗ trợ, vui lòng gọi hotline"]
            },
            "technical": {
                "intro": ["Về vấn đề kỹ thuật này", "Đối với sự cố bạn gặp phải", "Liên quan đến vấn đề này"],
                "outro": ["Nếu vẫn chưa được, hãy liên hệ hotline 1900 54 54 13", "Bạn có thể thử lại hoặc liên hệ hỗ trợ"]
            }
        }
    
    def categorize_question(self, question):
        """Phân loại câu hỏi dựa trên từ khóa"""
        question_lower = question.lower()
        
        fee_keywords = ["phí", "lệ phí", "chi phí", "tốn", "mất tiền"]
        payment_keywords = ["thanh toán", "trả", "nợ", "sao kê", "đóng tiền"]
        card_keywords = ["thẻ", "card", "mất thẻ", "khóa thẻ", "thẻ phụ"]
        technical_keywords = ["otp", "không nhận được", "lỗi", "sự cố", "không hoạt động"]
        
        if any(keyword in question_lower for keyword in fee_keywords):
            return "fee"
        elif any(keyword in question_lower for keyword in payment_keywords):
            return "payment"
        elif any(keyword in question_lower for keyword in card_keywords):
            return "card"
        elif any(keyword in question_lower for keyword in technical_keywords):
            return "technical"
        else:
            return "general"
    
    def format_natural_response(self, answer, question, category="general"):
        """Tạo câu trả lời tự nhiên"""
        # Thêm greeting
        greeting = random.choice(self.greeting_templates)
        
        # Thêm intro phù hợp với category
        if category in self.response_templates:
            intro = random.choice(self.response_templates[category]["intro"])
            outro = random.choice(self.response_templates[category]["outro"])
        else:
            intro = ""
            outro = ""
        
        # Thêm closing
        closing = random.choice(self.closing_templates)
        
        # Xử lý format answer
        formatted_answer = self.format_answer_content(answer)
        
        # Ghép lại
        if intro:
            response = f"{greeting}{intro}, {formatted_answer.lower()}"
        else:
            response = f"{greeting}{formatted_answer}"
        
        if outro:
            response += f" {outro}."
        
        response += closing
        
        return response
    
    def format_answer_content(self, answer):
        """Format nội dung câu trả lời"""
        # Loại bỏ các ký tự đặc biệt không cần thiết
        answer = re.sub(r'\n+', ' ', answer)
        answer = re.sub(r'\s+', ' ', answer)
        
        # Thay thế một số từ ngữ cứng nhắc
        replacements = {
            "Quý khách": "Bạn",
            "quý khách": "bạn",
            "Vietcombank": "VCB",
            "đề nghị": "bạn nên",
            "cần thực hiện": "cần làm",
            "vui lòng": "hãy"
        }
        
        for old, new in replacements.items():
            answer = answer.replace(old, new)
        
        return answer.strip()
    
    def get_top_k_answers(self, question, k=3):
        """Lấy top k câu trả lời phù hợp nhất"""
        question_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(question_vec, self.question_vectors)
        
        # Lấy top k indices
        top_indices = scores[0].argsort()[-k:][::-1]
        results = []
        
        for idx in top_indices:
            results.append({
                "question": self.questions[idx],
                "answer": self.answers[idx],
                "score": scores[0][idx],
                "data": self.faq_data[idx]
            })
        
        return results
    
    def get_answer(self, question, use_natural_response=True):
        """Lấy câu trả lời với tùy chọn tự nhiên hóa"""
        results = self.get_top_k_answers(question, k=3)
        
        if not results or results[0]["score"] < 0.2:
            return self.get_fallback_response(question)
        
        best_result = results[0]
        
        if use_natural_response:
            category = self.categorize_question(question)
            return self.format_natural_response(
                best_result["answer"], 
                question, 
                category
            )
        else:
            return best_result["answer"]
    
    def get_fallback_response(self, question):
        """Trả lời khi không tìm thấy câu trả lời phù hợp"""
        fallback_responses = [
            f"Xin lỗi, tôi chưa có thông tin cụ thể về '{question}'. Bạn có thể liên hệ hotline 1900 54 54 13 để được hỗ trợ trực tiếp nhé!",
            f"Tôi hiểu bạn đang quan tâm về '{question}', tuy nhiên tôi cần thêm thông tin để trả lời chính xác. Bạn có thể hỏi cụ thể hơn hoặc liên hệ chi nhánh gần nhất.",
            f"Câu hỏi về '{question}' khá cụ thể. Để được tư vấn chính xác nhất, bạn nên liên hệ trực tiếp với VCB qua hotline 1900 54 54 13 hoặc ghé thăm chi nhánh nhé!"
        ]
        
        return random.choice(fallback_responses)
    
    def get_contextual_answer(self, question):
        """Lấy nhiều câu trả lời liên quan để tạo context"""
        results = self.get_top_k_answers(question, k=3)
        
        if not results or results[0]["score"] < 0.15:
            return self.get_fallback_response(question)
        
        # Nếu có nhiều câu trả lời liên quan
        if len(results) > 1 and results[1]["score"] > 0.15:
            category = self.categorize_question(question)
            
            main_answer = results[0]["answer"]
            additional_info = []
            
            for result in results[1:]:
                if result["score"] > 0.15:
                    additional_info.append(result["answer"])
            
            # Tạo câu trả lời tổng hợp
            response = self.format_natural_response(main_answer, question, category)
            
            if additional_info:
                response += f"\n\nThông tin bổ sung: {' '.join(additional_info[:1])}"
            
            return response
        else:
            return self.get_answer(question, use_natural_response=True)