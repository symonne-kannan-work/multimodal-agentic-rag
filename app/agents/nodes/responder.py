import logfire
from app.agents.state import AgentState
from app.config import settings
from langchain_groq import ChatGroq

# Direct Groq call 
llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL, temperature=0.1)


def generate_node(state: AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History.
    """
    query = state["current_query"]

    history = ""
    for message in state["messages"][:-1]:
        role = "User" if message["role"] == "user" else "Assistant"
        history += f"{role}: {message['content']}\n"

    user_message = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are a friendly and helpful Enterprise AI Assistant.
        Answer the user's latest message using the CONVERSATION HISTORY below.

        CONVERSATION HISTORY:
        {history}

        LATEST MESSAGE:
        "{user_message}"
        """
    else:
        logfire.info("Generating technical RAG response.")
        max_context_chars = 25000
        full_context = ""

        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
        You are a Senior Technical Architect.
        Answer the question using the TECHNICAL CONTEXT provided.

        TECHNICAL CONTEXT:
        {full_context}

        CONVERSATION HISTORY:
        {history}

        USER QUESTION:
        "{user_message}"
        """

    with logfire.span("✍️ LLM Synthesis"):
        try:
            content = llm.invoke(prompt).content
            logfire.info("✅ Response synthesised via LLM.")

            return {
                "final_answer": content,
                "status": "Response generated.",
                "plan": state["plan"],
                "messages": [{"role": "assistant", "content": content}]
            }

        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e