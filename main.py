import openai
from pinecone import Pinecone
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
from chat_db import log_to_mysql,get_chat_history

# Init OpenAI & Pinecone
openai.api_key = OPENAI_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

def get_embedding(text: str):
    response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
    return response["data"][0]["embedding"]

def query_pinecone(query: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    result = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    matches = result.matches if hasattr(result, 'matches') else result['matches']
    texts = [match['metadata']['text'] for match in matches]
    sources = [match['metadata'].get('doc_name', 'web') for match in matches]
    return texts, sources

def answer_question(question: str, user_id: str):
    context_chunks, _ = query_pinecone(question)
    context_text = "\n\n".join(context_chunks)

    # Load chat history from DB
    chat_history = get_chat_history(user_id)

    # Add current question with context
    messages = chat_history.copy()
    messages.append({
        "role": "user",
        "content": f"Context:\n{context_text}\n\nQuestion: {question}"
    })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=500,
    )
    answer = response.choices[0].message.content.strip()

    # Log new messages
    log_to_mysql(role="user", message=question, sources=["web"], user_id=user_id)
    log_to_mysql(role="assistant", message=answer, sources=["web"], user_id=user_id)

    return answer, ["web"]