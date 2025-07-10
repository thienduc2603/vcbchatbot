import json
import os
from typing import List, Dict, Any

class DataProcessor:
    """Utility class để xử lý và format dữ liệu FAQ"""
    
    def __init__(self):
        self.processed_data = []
    
    def load_all_faq_data(self, folder="data"):
        """Load tất cả file JSON FAQ từ folder"""
        faq_all = []
        for fname in os.listdir(folder):
            if fname.endswith(".json"):
                with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        item["source"] = fname
                        faq_all.append(item)
        return faq_all
    
    def process_faq_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý một item FAQ để format tốt hơn"""
        processed = {
            "question": item["question"],
            "answer": item["answer"],
            "source": item.get("source", "unknown")
        }
        
        # Xử lý table nếu có
        if "table" in item:
            table_text = self.format_table(item["table"])
            processed["answer"] += f"\n\n{table_text}"
        
        # Xử lý bullet points nếu có
        if "bullet_points" in item:
            bullet_text = self.format_bullet_points(item["bullet_points"])
            processed["answer"] += f"\n\n{bullet_text}"
        
        # Xử lý note nếu có
        if "note" in item:
            processed["answer"] += f"\n\nLưu ý: {item['note']}"
        
        return processed
    
    def format_table(self, table_data: Dict[str, Any]) -> str:
        """Format table thành text dễ đọc"""
        if not table_data or "columns" not in table_data or "rows" not in table_data:
            return ""
        
        columns = table_data["columns"]
        rows = table_data["rows"]
        
        # Tạo header
        formatted_table = " | ".join(columns) + "\n"
        formatted_table += "-" * len(formatted_table) + "\n"
        
        # Tạo rows
        for row in rows:
            formatted_table += " | ".join(str(cell) for cell in row) + "\n"
        
        return formatted_table
    
    def format_bullet_points(self, bullet_points: List[str]) -> str:
        """Format bullet points thành text dễ đọc"""
        if not bullet_points:
            return ""
        
        formatted = ""
        for i, point in enumerate(bullet_points, 1):
            formatted += f"{i}. {point}\n"
        
        return formatted.strip()
    
    def enhance_data_with_keywords(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Thêm keywords cho mỗi FAQ item để tìm kiếm tốt hơn"""
        keyword_mapping = {
            "phí": ["fee", "cost", "charge", "lệ phí", "chi phí"],
            "thanh toán": ["payment", "pay", "trả", "nợ", "sao kê"],
            "thẻ": ["card", "credit card", "thẻ tín dụng", "thẻ phụ"],
            "otp": ["mã xác thực", "verification", "xác nhận"],
            "khóa thẻ": ["block card", "lock card", "mất thẻ", "thất lạc"],
            "hotline": ["support", "hỗ trợ", "liên hệ", "gọi"]
        }
        
        enhanced_data = []
        for item in data:
            enhanced_item = item.copy()
            keywords = []
            
            # Tìm keywords dựa trên nội dung
            content = (item["question"] + " " + item["answer"]).lower()
            for keyword, synonyms in keyword_mapping.items():
                if keyword in content or any(syn in content for syn in synonyms):
                    keywords.extend([keyword] + synonyms)
            
            enhanced_item["keywords"] = list(set(keywords))
            enhanced_data.append(enhanced_item)
        
        return enhanced_data
    
    def save_processed_data(self, data: List[Dict[str, Any]], output_file: str):
        """Lưu dữ liệu đã xử lý"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def process_all_data(self, input_folder: str, output_file: str):
        """Process tất cả dữ liệu từ folder và lưu ra file"""
        # Load all data
        raw_data = self.load_all_faq_data(input_folder)
        
        # Process each item
        processed_data = []
        for item in raw_data:
            processed_item = self.process_faq_item(item)
            processed_data.append(processed_item)
        
        # Enhance with keywords
        enhanced_data = self.enhance_data_with_keywords(processed_data)
        
        # Save
        self.save_processed_data(enhanced_data, output_file)
        
        print(f"Processed {len(enhanced_data)} FAQ items and saved to {output_file}")
        return enhanced_data

# Usage example
if __name__ == "__main__":
    processor = DataProcessor()
    
    # Process all data
    processed_data = processor.process_all_data("data", "data/processed_faq.json")
    
    # Print some examples
    for i, item in enumerate(processed_data[:3]):
        print(f"\n=== FAQ {i+1} ===")
        print(f"Question: {item['question']}")
        print(f"Answer: {item['answer'][:100]}...")
        print(f"Keywords: {item['keywords']}")
        print(f"Source: {item['source']}")