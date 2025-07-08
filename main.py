from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from chatbot.retrieval import FAQRetriever

app = FastAPI()
retriever = FAQRetriever("data/vcb_credit_faq.json")

@app.post("/chat")
async def chat(request: Request):
    form = await request.form()
    message = form.get("Body", "")
    answer = retriever.get_answer(message)
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{answer}</Message>
</Response>"""
    return PlainTextResponse(xml_response, media_type="application/xml")
