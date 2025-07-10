from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from chatbot.retrieval import FAQRetriever
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
retriever = FAQRetriever("data/vcb_credit_faq.json")

@app.post("/chat")
async def chat(request: Request):
    try:
        form = await request.form()
        message = form.get("Body", "").strip()
        
        # Log incoming message
        logger.info(f"Received message: {message}")
        
        if not message:
            answer = "Xin chào! Tôi là trợ lý ảo của VCB. Bạn có cần hỗ trợ gì không?"
        else:
            # Sử dụng contextual answer cho câu trả lời tự nhiên hơn
            answer = retriever.get_contextual_answer(message)
        
        # Log response
        logger.info(f"Response: {answer}")
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{answer}</Message>
</Response>"""
        
        return PlainTextResponse(xml_response, media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Xin lỗi, hệ thống đang gặp sự cố. Bạn vui lòng thử lại sau hoặc liên hệ hotline 1900 54 54 13 để được hỗ trợ.</Message>
</Response>"""
        return PlainTextResponse(error_response, media_type="application/xml")

@app.get("/")
async def root():
    return {"message": "VCB FAQ Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running normally"}

# Endpoint để test chatbot
@app.post("/test-chat")
async def test_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    
    if not message:
        return {"error": "Message is required"}
    
    try:
        answer = retriever.get_contextual_answer(message)
        return {
            "question": message,
            "answer": answer,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }