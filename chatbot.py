# # chatbot.py

# import os
# import logging
# from datetime import datetime

# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.chains import create_retrieval_chain, create_history_aware_retriever
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.messages import HumanMessage, AIMessage
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from dotenv import load_dotenv

# load_dotenv()

# # Optional: disable Chroma telemetry
# os.environ["CHROMA_TELEMETRY_ENABLED"] = "FALSE"

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # --- 1. Initialize Embeddings and Vectorstore ---
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={"device": "cpu"},
#     encode_kwargs={"normalize_embeddings": True}
# )

# vectorstore_path = "./jupiter_vectordb_enhanced"
# vectorstore = Chroma(
#     persist_directory=vectorstore_path,
#     embedding_function=embeddings
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 5})


# # --- 2. Initialize the LLM ---
# llm = ChatGroq(
#     groq_api_key= os.environ.get("GROQ_API_KEY", ""),
#     model_name="llama3-8b-8192",
#     temperature=0.3,
#     max_tokens=300
# )

# # --- 3. Prompt Templates ---
# # Contextualize Follow-Up Questions
# contextualize_q_prompt = ChatPromptTemplate.from_messages([
#     ("system", (
#         "As JupiterBot, rewrite the user's follow-up message into a clear, standalone question. "
#         "Include relevant chat history, domain-specific terms (e.g., 'Jupiter card', 'Jewels'), "
#         "and clarify any ambiguity to make it fully self-contained."
#     )),
#     MessagesPlaceholder("chat_history"),
#     ("human", "{input}")
# ])

# # Main Answering Prompt
# qa_prompt = ChatPromptTemplate.from_messages([
#     ("system", (
#         "You are Jupiter’s Tier‑1 Support Bot. Provide friendly, professional responses (2–3 sentences) "
#         "using the provided context.\n"
#         "If relevant, include clear actionable steps like app navigation (e.g., 'Go to Settings > Card > Block Card') "
#         "or links to the Help Center.\n"
#         "If unsure, reply: 'I'm not certain—let me escalate this or check with our team.'\n"
#         "Avoid using internal system terms. Always prioritize clarity and customer understanding.\n\n"
#         "{context}"
#     )),
#     MessagesPlaceholder("chat_history"),
#     ("human", "{input}")
# ])

# # --- 4. Build RAG Chain with Memory ---
# history_aware_retriever = create_history_aware_retriever(
#     llm=llm,
#     retriever=retriever,
#     prompt=contextualize_q_prompt
# )

# question_answer_chain = create_stuff_documents_chain(
#     llm=llm,
#     prompt=qa_prompt
# )

# rag_chain = create_retrieval_chain(
#     retriever=history_aware_retriever,
#     combine_docs_chain=question_answer_chain
# )

# # --- 5. In-memory Chat History per Session ---
# store = {}

# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# # Wrap the chain with session-aware message memory
# conversational_rag_chain = RunnableWithMessageHistory(
#     rag_chain,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="chat_history",
#     output_messages_key="answer"
# )

# # --- 6. Exposed Function for UI or CLI Integration ---
# def query_jupiter(question: str, session_id: str = "default") -> dict:
#     try:
#         logger.info(f"💬 Query: {question} (Session: {session_id})")
#         start = datetime.now()

#         result = conversational_rag_chain.invoke(
#             {"input": question},
#             config={"configurable": {"session_id": session_id}}
#         )

#         return {
#             "question": question,
#             "answer": result["answer"],
#             "session_id": session_id,
#             "processing_time": (datetime.now() - start).total_seconds()
#         }

#     except Exception as e:
#         logger.error(f"❌ Error: {e}")
#         return {
#             "error": str(e),
#             "session_id": session_id
#         }

# # --- 7. Test Runner (Optional for Local Testing) ---
# def main():
#     if "GROQ_API_KEY" not in os.environ:
#         print("❌ GROQ_API_KEY environment variable is not set")
#         return

#     print("✅ Jupiter RAG chatbot initialized\n")

#     test_queries = [
#         "Im sai krishna ,How do I activate my Jupiter card?",
#         "Bill payment failed",
#         "What are Jewels?",
#         "KYC verification process",
#         "What my name ?",
#         "what services you providing for me ?",
#         "How can I activate my Jupiter card, and what are the common issues users face during activation?",
#         "What steps should I follow if my bill payment fails? Are there alternative payment methods outside the app?",
#         "What exactly are “Jewels” in Jupiter, and how can I earn, redeem, or track them effectively?",
#         "What is the detailed KYC (Know Your Customer) verification process, and how long does it usually take to complete?",
#         "What types of financial services and products does Jupiter currently offer (e.g., debit cards, credit cards, savings accounts, investments)?",
#         "Can Jupiter be used internationally? If yes, what are the restrictions or fees for using the card abroad?",
#         "What triggers automatic fund deductions from savings or “Pots” to pay dues, and how can users control or disable this feature?",
#         "What is the process and expected timeline for resolving account freezes or blocks due to KYC or suspicious activities?",
#         "How does Jupiter handle customer support escalations? What are the official channels, response times, and escalation paths?",
#         "What security measures are in place to protect user data and transactions, and how does Jupiter comply with financial regulations like RBI guidelines?"
#     ]

#     # for i, q in enumerate(test_queries, 1):
#     #     print(f"\n{'='*60}")
#     #     print(f"🧪 Test {i}: {q}")
#     #     result = query_jupiter(q, session_id=f"test_session_{i}")
#     #     print(f"✅ Answer: {result.get('answer')}")
#     #     print(f"⏱ Time: {result.get('processing_time'):.2f}s")

# if __name__ == "__main__":
#     main()
# enhanced_chatbot.py

import os
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jupiter_chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    ERROR = "error"

class JupiterChatbot:
    def __init__(self):
        """Initialize the enhanced Jupiter chatbot with improved prompting"""
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.validator_llm = None
        self.contextualizer_llm = None
        self.qa_llm = None
        self.session_store = {}

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "out_of_scope_queries": 0,
            "successful_queries": 0,
            "error_queries": 0,
            "greeting_queries": 0,
            "escalated_queries": 0
        }

        self._initialize_components()
        self._setup_enhanced_chains()

    def _initialize_components(self):
        """Initialize embeddings, vectorstore, and LLMs"""
        try:
            logger.info("🔧 Initializing enhanced chatbot components...")

            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )

            # Initialize vectorstore
            vectorstore_path = "./jupiter_vectordb_enhanced"
            self.vectorstore = Chroma(
                persist_directory=vectorstore_path,
                embedding_function=self.embeddings
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="mmr",  # Maximum Marginal Relevance for diverse results
                search_kwargs={"k": 6, "fetch_k": 20}
            )

            # Initialize LLMs with optimized configurations
            groq_api_key = os.environ.get("GROQ_API_KEY", "")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set")

            # Validator LLM - Fast and efficient
            self.validator_llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name="llama3-8b-8192",
                temperature=0.0,
                max_tokens=50
            )

            # Contextualizer LLM - Moderate creativity
            self.contextualizer_llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name="llama3-8b-8192",
                temperature=0.2,
                max_tokens=200
            )

            # QA LLM - Balanced for comprehensive answers
            self.qa_llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name="llama3-8b-8192",
                temperature=0.3,
                max_tokens=500
            )

            logger.info("✅ All components initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise

    def _setup_enhanced_chains(self):
        """Setup enhanced processing chains with improved prompts"""
        try:
            # 1. Enhanced Validator Chain
            self.validator_prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a scope validator for JupiterBot. Determine if a user question is about Jupiter.money services.\n\n"

                    "✅ ALWAYS ALLOW (Jupiter.money related):\n"
                    "- App features: Pots, Jewels, Cards, UPI, bill payments, transfers\n"
                    "- Account help: KYC, linking, profiles, statements, troubleshooting\n"
                    "- Card services: activation, PIN, blocking, limits, transactions\n"
                    "- General Jupiter inquiries, onboarding, how-to questions\n"
                    "- Friendly greetings, small talk, 'What can you do?' questions\n\n"

                    "🚫 BLOCK (Not Jupiter.money related):\n"
                    "- Other banks/financial services (HDFC, SBI, PayTM, etc.)\n"
                    "- Investment advice, tax planning, personal finance guidance\n"
                    "- Unrelated topics: cooking, movies, politics, general knowledge\n\n"

                    "Respond with exactly ONE word:\n"
                    "- 'ALLOWED' if question is Jupiter.money related OR friendly interaction\n"
                    "- 'BLOCKED' if question is completely unrelated to Jupiter.money"
                )),
                ("human", "{input}")
            ])

            self.validator_chain = self.validator_prompt | self.validator_llm | StrOutputParser()

            # 2. Enhanced Contextualizer Chain
            self.contextualizer_prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are JupiterBot's conversation contextualizer. Your job is to rewrite follow-up questions "
                    "into clear, standalone queries that incorporate relevant chat history.\n\n"

                    "GUIDELINES:\n"
                    "- Make questions self-contained and specific\n"
                    "- Include Jupiter-specific terms when relevant (Jewels, Pots, Jupiter card, etc.)\n"
                    "- Resolve pronouns and references using chat history\n"
                    "- If question is already clear, return it unchanged\n"
                    "- Maintain the user's intent and tone\n\n"

                    "EXAMPLES:\n"
                    "User: 'How do I activate it?' (after asking about Jupiter card)\n"
                    "Output: 'How do I activate my Jupiter debit card?'\n\n"

                    "User: 'What about the rewards?' (after asking about Jupiter features)\n"
                    "Output: 'What are Jupiter Jewels rewards and how do they work?'"
                )),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])

            self.contextualizer_chain = self.contextualizer_prompt | self.contextualizer_llm | StrOutputParser()

            # 3. Enhanced History-aware retriever
            self.history_aware_retriever = create_history_aware_retriever(
                llm=self.contextualizer_llm,
                retriever=self.retriever,
                prompt=self.contextualizer_prompt
            )

            # 4. Enhanced QA Chain with improved prompt
            self.qa_prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are JupiterBot, Jupiter.money's AI Assistant — your friendly guide to India's most delightful money app.\n\n"

                    "🎯 PRIMARY ROLE:\n"
                    "You provide instant, helpful support for Jupiter.money users with a warm, professional tone that reflects our brand values of simplicity, delight, and customer-first service.\n\n"

                    "✅ IN-SCOPE TOPICS (Always Help With):\n"
                    "• Jupiter App Features: Pots, Jewels, Cards, UPI payments, bill payments, money transfers\n"
                    "• Account Management: KYC verification, account linking, profile updates, statements\n"
                    "• Card Services: Debit card activation, PIN reset, card blocking/unblocking, transaction limits\n"
                    "• Troubleshooting: Login issues, payment failures, app crashes, transaction disputes\n"
                    "• Onboarding: Account opening, document upload, verification status\n"
                    "• General Inquiries: Features explanation, benefits, how-to guides\n"
                    "• Friendly Interactions: Greetings, small talk, 'What can you do?', casual questions\n\n"

                    "📋 RESPONSE GUIDELINES:\n"
                    "1. TONE: Warm, friendly, professional but conversational\n"
                    "2. LENGTH: 2-3 sentences for simple queries, up to 4-5 for complex ones\n"
                    "3. STRUCTURE: Clear, actionable steps when relevant (e.g., 'Go to App → Settings → Cards')\n"
                    "4. LANGUAGE: Simple, jargon-free, easy to understand\n"
                    "5. BRAND VOICE: Helpful buddy who knows Jupiter inside-out\n\n"

                    "🔄 INTERACTION PATTERNS:\n"
                    "• Greetings: Respond warmly and ask how you can help\n"
                    "• Vague Questions: Gently guide users to be more specific\n"
                    "• Complex Issues: Break down into simple steps or offer escalation\n\n"

                    "⚠️ WHEN UNCERTAIN:\n"
                    "Say: 'I want to make sure I give you the right information. Let me connect you with our support team who can help with the specifics, or you can check the Help section in your Jupiter app.'\n\n"

                    "🎨 BRAND PERSONALITY:\n"
                    "• Curious and genuinely helpful\n"
                    "• Optimistic and solution-focused\n"
                    "• Knowledgeable but humble\n"
                    "• Professional yet approachable\n\n"

                    "Use the provided context to answer accurately. If context doesn't contain the answer, be honest about limitations and offer to escalate.\n\n"

                    "CONTEXT:\n{context}"
                )),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])

            self.question_answer_chain = create_stuff_documents_chain(
                llm=self.qa_llm,
                prompt=self.qa_prompt
            )

            # 5. Complete RAG Chain
            self.rag_chain = create_retrieval_chain(
                retriever=self.history_aware_retriever,
                combine_docs_chain=self.question_answer_chain
            )

            # 6. Conversational RAG Chain with memory
            self.conversational_rag_chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )

            logger.info("✅ Enhanced chains setup successfully")

        except Exception as e:
            logger.error(f"❌ Failed to setup enhanced chains: {e}")
            raise

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for a session"""
        if session_id not in self.session_store:
            self.session_store[session_id] = ChatMessageHistory()
        return self.session_store[session_id]

    def _sanitize_input(self, text: str) -> str:
        """Enhanced input sanitization"""
        if not text or not isinstance(text, str):
            return ""

        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove potentially harmful patterns
        text = re.sub(r'[<>{}]', '', text)  # Remove HTML-like tags

        # Limit length
        max_length = 500
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.warning(f"Input truncated to {max_length} characters")

        return text

    def _is_greeting_or_casual(self, question: str) -> bool:
        """Check if question is a greeting or casual interaction"""
        greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\bwhat can you do\b',
            r'\bwho are you\b',
            r'\bhelp me\b',
            r'\bhow are you\b',
            r'\bthanks?\b',
            r'\bthank you\b'
        ]

        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in greeting_patterns)

    def _validate_question(self, question: str) -> ValidationResult:
        """Enhanced validation with greeting detection"""
        try:
            logger.info(f"🛡️ Validating question scope...")

            # Always allow greetings and casual interactions
            if self._is_greeting_or_casual(question):
                logger.info("👋 Detected greeting/casual interaction - allowing")
                self.metrics["greeting_queries"] += 1
                return ValidationResult.IN_SCOPE

            result = self.validator_chain.invoke({"input": question})
            result = result.strip().upper()

            if "ALLOWED" in result:
                logger.info("✅ Question is in scope")
                return ValidationResult.IN_SCOPE
            elif "BLOCKED" in result:
                logger.info("🚫 Question is out of scope")
                return ValidationResult.OUT_OF_SCOPE
            else:
                logger.warning(f"⚠️ Ambiguous validation result: {result}")
                return ValidationResult.IN_SCOPE  # Default to allowing

        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return ValidationResult.ERROR

    def _contextualize_question(self, question: str, session_id: str) -> str:
        """Enhanced question contextualization"""
        try:
            logger.info("🔄 Contextualizing question...")

            chat_history = self._get_session_history(session_id).messages
            if not chat_history or len(chat_history) < 2:
                return question  # No meaningful history to contextualize with

            result = self.contextualizer_chain.invoke({
                "input": question,
                "chat_history": chat_history[-10:]  # Use last 10 messages for context
            })

            logger.info(f"📝 Contextualized: {result}")
            return result.strip()

        except Exception as e:
            logger.error(f"❌ Contextualization error: {e}")
            return question  # Fallback to original question

    def _generate_answer(self, question: str, session_id: str) -> Dict[str, Any]:
        """Enhanced answer generation with better error handling"""
        try:
            logger.info("🧠 Generating answer...")

            result = self.conversational_rag_chain.invoke(
                {"input": question},
                config={"configurable": {"session_id": session_id}}
            )

            # Extract and process source documents
            source_docs = result.get("context", [])
            sources = []
            for doc in source_docs:
                source = doc.metadata.get("source", "Unknown")
                if source != "Unknown":
                    sources.append(source)

            # Determine if escalation is needed
            answer_text = result["answer"].lower()
            needs_escalation = any(keyword in answer_text for keyword in [
                "not sure", "uncertain", "don't know", "can't help",
                "contact support", "escalate", "technical team"
            ])

            if needs_escalation:
                self.metrics["escalated_queries"] += 1

            return {
                "answer": result["answer"],
                "sources": list(set(sources)),  # Remove duplicates
                "confidence": len(source_docs),
                "needs_escalation": needs_escalation
            }

        except Exception as e:
            logger.error(f"❌ Answer generation error: {e}")
            return {
                "answer": "I'm experiencing technical difficulties right now. Please try again in a moment, or you can reach out to our support team through the Jupiter app for immediate assistance! 😊",
                "sources": [],
                "confidence": 0,
                "needs_escalation": True
            }

    def query(self, question: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Enhanced main query method with improved processing pipeline
        """
        start_time = datetime.now()
        self.metrics["total_queries"] += 1

        try:
            logger.info(f"💬 New query: '{question}' (Session: {session_id})")

            # Stage 1: Input sanitization
            sanitized_question = self._sanitize_input(question)
            if not sanitized_question:
                return {
                    "answer": "I'd love to help! Could you please ask me a question about Jupiter.money? 😊",
                    "session_id": session_id,
                    "processing_time": 0,
                    "stage": "input_validation",
                    "status": "error"
                }

            # Stage 2: Enhanced scope validation
            validation_result = self._validate_question(sanitized_question)

            if validation_result == ValidationResult.OUT_OF_SCOPE:
                self.metrics["out_of_scope_queries"] += 1
                return {
                    "answer": "Hi there! 👋 I can only help with questions about Jupiter.money services, features, and your account. What would you like to know about Jupiter today?",
                    "session_id": session_id,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "stage": "validation",
                    "status": "out_of_scope"
                }

            elif validation_result == ValidationResult.ERROR:
                self.metrics["error_queries"] += 1
                return {
                    "answer": "I'm having a small technical hiccup. Could you try rephrasing your question? I'm here to help with anything Jupiter.money related! 😊",
                    "session_id": session_id,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "stage": "validation",
                    "status": "error"
                }

            # Stage 3: Question contextualization
            contextualized_question = self._contextualize_question(sanitized_question, session_id)

            # Stage 4: Enhanced RAG-based answer generation
            answer_result = self._generate_answer(contextualized_question, session_id)

            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics["successful_queries"] += 1

            result = {
                "question": sanitized_question,
                "contextualized_question": contextualized_question,
                "answer": answer_result["answer"],
                "sources": answer_result["sources"],
                "confidence": answer_result["confidence"],
                "needs_escalation": answer_result.get("needs_escalation", False),
                "session_id": session_id,
                "processing_time": processing_time,
                "stage": "complete",
                "status": "success"
            }

            logger.info(f"✅ Query completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            self.metrics["error_queries"] += 1
            logger.error(f"❌ Unexpected error in query processing: {e}")

            return {
                "answer": "Oops! I'm experiencing some technical difficulties. Please try again in a moment, or reach out to our support team through the Jupiter app for immediate help! 🛠️",
                "session_id": session_id,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "stage": "error",
                "status": "error",
                "error": str(e)
            }

    def get_enhanced_metrics(self) -> Dict[str, Any]:
        """Get enhanced chatbot performance metrics"""
        total = max(self.metrics["total_queries"], 1)
        return {
            **self.metrics,
            "success_rate": (self.metrics["successful_queries"] / total) * 100,
            "out_of_scope_rate": (self.metrics["out_of_scope_queries"] / total) * 100,
            "greeting_rate": (self.metrics["greeting_queries"] / total) * 100,
            "escalation_rate": (self.metrics["escalated_queries"] / total) * 100,
            "error_rate": (self.metrics["error_queries"] / total) * 100
        }

    def clear_session(self, session_id: str) -> bool:
        """Clear chat history for a specific session"""
        try:
            if session_id in self.session_store:
                del self.session_store[session_id]
                logger.info(f"🗑️ Cleared session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error clearing session {session_id}: {e}")
            return False

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.session_store.keys())

# --- Enhanced Convenience Functions ---

_chatbot_instance = None

def get_chatbot() -> JupiterChatbot:
    """Get or create global chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = JupiterChatbot()
    return _chatbot_instance

def query_jupiter(question: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Enhanced convenience function for querying Jupiter chatbot
    """
    chatbot = get_chatbot()
    return chatbot.query(question, session_id)

def clear_chat_session(session_id: str = "default") -> bool:
    """Clear chat history for a session"""
    chatbot = get_chatbot()
    return chatbot.clear_session(session_id)

def get_chatbot_metrics() -> Dict[str, Any]:
    """Get enhanced chatbot performance metrics"""
    chatbot = get_chatbot()
    return chatbot.get_enhanced_metrics()

# --- Enhanced Test Runner ---
def main():
    """Test the enhanced chatbot with comprehensive scenarios"""
    if "GROQ_API_KEY" not in os.environ:
        print("❌ GROQ_API_KEY environment variable is not set")
        return

    print("🚀 Initializing Enhanced Jupiter RAG Chatbot v2.0...\n")

    try:
        chatbot = JupiterChatbot()
        print("✅ Enhanced chatbot initialized successfully!\n")

        # Enhanced test scenarios
        test_scenarios = [
            # Greetings and casual interactions
            ("Hi there!", "user_1"),
            ("Hello, what can you do?", "user_1"),
            ("Good morning! I need help", "user_2"),

            # In-scope Jupiter questions
            ("How do I activate my Jupiter debit card?", "user_1"),
            ("What are Jewels and how do I earn them?", "user_3"),
            ("My payment failed yesterday, what should I do?", "user_1"),
            ("Tell me about KYC verification process", "user_4"),
            ("How can I block my card if it's lost?", "user_5"),
            ("What is a Pot and how do I create one?", "user_3"),

            # Follow-up questions (testing contextualization)
            ("How long does it take?", "user_4"),  # Follow-up to KYC
            ("What documents do I need?", "user_4"),  # Another follow-up

            # Edge cases and out-of-scope
            ("What's the weather today?", "user_6"),
            ("Tell me about HDFC bank services", "user_7"),
            ("How do I cook pasta?", "user_8"),

            # Complex scenarios
            ("I can't login to my app and my card is not working", "user_9"),
            ("", "user_10"),  # Empty input
            ("a" * 100, "user_10"),  # Long input
        ]

        for i, (question, session_id) in enumerate(test_scenarios, 1):
            print(f"\n{'='*80}")
            print(f"🧪 Test {i}: {question[:100]}{'...' if len(question) > 100 else ''}")
            print(f"👤 Session: {session_id}")

            result = chatbot.query(question, session_id)

            print(f"✅ Answer: {result['answer']}")
            print(f"📊 Status: {result['status']} | Stage: {result['stage']}")
            print(f"⏱️ Time: {result['processing_time']:.2f}s")

            if result.get('sources'):
                print(f"📚 Sources: {', '.join(result['sources'][:3])}...")  # Show first 3 sources

            if result.get('needs_escalation'):
                print("🚨 Escalation recommended")

        # Show enhanced metrics
        print(f"\n{'='*80}")
        print("📈 ENHANCED METRICS:")
        metrics = chatbot.get_enhanced_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}%")
            else:
                print(f"  {key}: {value}")

        print(f"\n🔄 Active Sessions: {len(chatbot.get_active_sessions())}")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    main()
