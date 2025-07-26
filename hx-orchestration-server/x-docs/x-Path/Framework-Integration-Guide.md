# Framework Integration Guide

**Document Version:** 1.0  
**Date:** 2025-07-25  
**Author:** Manus AI  
**Project:** Citadel AI Operating System - Orchestration Server Implementation  
**Server:** hx-orchestration-server (192.168.10.31)  
**Purpose:** Comprehensive framework integration and implementation guide  
**Classification:** Technical Implementation Guide  

---

## Framework Overview

### Core AI Frameworks

#### **1. Pydantic - Data Validation & Serialization**
**Purpose**: Type-safe data validation, serialization, and settings management
```python
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
from datetime import datetime

class EmbeddingRequest(BaseModel):
    """Pydantic model for embedding requests"""
    text: str = Field(..., min_length=1, max_length=8192)
    model: str = Field(default="nomic-embed-text")
    options: Optional[Dict[str, Any]] = None
    cache_enabled: bool = Field(default=True)
    
    @validator('model')
    def validate_model(cls, v):
        allowed_models = ["nomic-embed-text", "mxbai-embed-large", "bge-m3", "all-minilm"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of {allowed_models}")
        return v

class OrchestrationWorkflow(BaseModel):
    """Pydantic model for workflow definitions"""
    workflow_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$')
    description: str = Field(..., max_length=500)
    steps: List[Dict[str, Any]] = Field(..., min_items=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    
    class Config:
        schema_extra = {
            "example": {
                "workflow_id": "text_analysis_pipeline",
                "description": "Analyze text with embeddings and LLM processing",
                "steps": [
                    {"type": "embedding", "model": "nomic-embed-text"},
                    {"type": "vector_search", "collection": "documents"},
                    {"type": "llm_query", "prompt": "Analyze the content"}
                ]
            }
        }

class Settings(BaseSettings):
    """Application settings with Pydantic"""
    app_name: str = "Citadel AI Operating System - Gateway"
    app_version: str = "2.0.0"
    service_name: str = "citadel-gateway"
    
    # Production Gateway Configuration
    listening_port: int = 8002  # Production port
    workers: int = 8           # High-performance uvicorn workers
    host: str = "0.0.0.0"      # Accept all interfaces
    
    # HANA-X Lab Database settings
    postgres_host: str = "192.168.10.35"  # hx-sql-database-server
    postgres_port: int = 5432
    postgres_db: str = "citadel_llm_db"
    postgres_user: str = "citadel_llm_user"
    postgres_password: str = "CitadelLLM#2025$SecurePass!"
    
    # Redis settings (local orchestration cache)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # HANA-X Lab Vector Database settings
    qdrant_host: str = "192.168.10.30"  # hx-vector-database-server
    qdrant_port: int = 6333
    
    # HANA-X Lab LLM servers (dual setup)
    llm_server_01: str = "192.168.10.29"  # hx-llm-server-01
    llm_server_02: str = "192.168.10.28"  # hx-llm-server-02
    llm_port: int = 8080
    llm_load_balance: bool = True
    
    # LangChain settings
    openai_api_key: Optional[str] = None
    langchain_tracing_v2: bool = True
    langsmith_api_key: Optional[str] = None
    
    # LiveKit settings
    livekit_url: Optional[str] = None
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    
    # HANA-X Lab Infrastructure
    metrics_server: str = "192.168.10.37"  # hx-metric-server
    web_server: str = "192.168.10.38"      # hx-web-server
    dev_server: str = "192.168.10.33"      # hx-development-server
    test_server: str = "192.168.10.34"     # hx-test-server
    devops_server: str = "192.168.10.36"   # hx-devops-server
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

#### **2. LangChain - LLM Application Framework**
**Purpose**: Building sophisticated LLM applications with chains, agents, and tools
```python
"""
LangChain Integration for AI Orchestration
"""
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import AsyncCallbackHandler
from langchain.schema import Document

import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient

class CitadelLangChainOrchestrator:
    """
    LangChain-based orchestration for complex AI workflows
    """
    
    def __init__(
        self,
        openai_api_key: str,
        qdrant_client: QdrantClient,
        collection_name: str = "citadel_documents"
    ):
        """Initialize LangChain orchestrator"""
        self.llm = OpenAI(
            openai_api_key=openai_api_key,
            temperature=0.3,
            max_tokens=1000
        )
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key
        )
        
        self.vectorstore = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=self.embeddings
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self._setup_chains()
        self._setup_agents()
    
    def _setup_chains(self):
        """Setup LangChain chains for different tasks"""
        
        # Document analysis chain
        analysis_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            Based on the following context, answer the question comprehensively:
            
            Context: {context}
            
            Question: {question}
            
            Provide a detailed analysis including:
            1. Key insights from the context
            2. Relevant connections and patterns
            3. Actionable recommendations
            
            Answer:
            """
        )
        
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=analysis_prompt,
            verbose=True
        )
        
        # Retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            ),
            return_source_documents=True
        )
    
    def _setup_agents(self):
        """Setup LangChain agents with tools"""
        
        tools = [
            Tool(
                name="Document Search",
                func=self._document_search,
                description="Search through document collection for relevant information"
            ),
            Tool(
                name="Embedding Analysis",
                func=self._embedding_analysis,
                description="Analyze text embeddings for similarity and clustering"
            ),
            Tool(
                name="Content Summarization",
                func=self._content_summarization,
                description="Summarize long-form content into key points"
            )
        ]
        
        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    async def process_workflow(
        self,
        workflow_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process complex workflow using LangChain"""
        
        workflow_id = workflow_definition["workflow_id"]
        steps = workflow_definition["steps"]
        context = workflow_definition.get("context", {})
        
        results = []
        
        for step in steps:
            step_type = step.get("type")
            
            if step_type == "document_qa":
                result = await self._execute_qa_step(step, context)
            elif step_type == "content_analysis":
                result = await self._execute_analysis_step(step, context)
            elif step_type == "agent_task":
                result = await self._execute_agent_step(step, context)
            else:
                result = {"error": f"Unknown step type: {step_type}"}
            
            results.append(result)
            context.update(result.get("output", {}))
        
        return {
            "workflow_id": workflow_id,
            "results": results,
            "final_context": context
        }
    
    async def _execute_qa_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute QA step using retrieval chain"""
        
        query = step.get("query", "")
        
        # Run QA chain
        result = await asyncio.to_thread(
            self.qa_chain,
            {"query": query}
        )
        
        return {
            "step_type": "document_qa",
            "query": query,
            "answer": result["result"],
            "source_documents": [
                doc.page_content for doc in result["source_documents"]
            ],
            "output": {"qa_result": result["result"]}
        }
    
    async def _execute_analysis_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute content analysis step"""
        
        content = step.get("content", context.get("content", ""))
        question = step.get("question", "Analyze this content")
        
        # Run analysis chain
        result = await asyncio.to_thread(
            self.analysis_chain.run,
            context=content,
            question=question
        )
        
        return {
            "step_type": "content_analysis",
            "analysis": result,
            "output": {"analysis_result": result}
        }
    
    async def _execute_agent_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent-based step"""
        
        task = step.get("task", "")
        
        # Run agent
        result = await asyncio.to_thread(
            self.agent.run,
            task
        )
        
        return {
            "step_type": "agent_task",
            "task": task,
            "result": result,
            "output": {"agent_result": result}
        }
    
    def _document_search(self, query: str) -> str:
        """Tool function for document search"""
        docs = self.vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in docs])
    
    def _embedding_analysis(self, text: str) -> str:
        """Tool function for embedding analysis"""
        # This would integrate with your Ollama embedding service
        return f"Embedding analysis for: {text[:100]}..."
    
    def _content_summarization(self, content: str) -> str:
        """Tool function for content summarization"""
        summary_prompt = f"Summarize the following content in 3-5 key points:\n\n{content}"
        return self.llm(summary_prompt)
```

#### **3. LangGraph - Stateful AI Workflows**
**Purpose**: Building complex, stateful, multi-actor applications
```python
"""
LangGraph Integration for Complex AI Workflows
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, List, TypedDict, Annotated
import operator
from langchain.schema import HumanMessage, AIMessage

class WorkflowState(TypedDict):
    """State structure for LangGraph workflows"""
    messages: Annotated[List[HumanMessage | AIMessage], operator.add]
    current_step: str
    workflow_id: str
    context: Dict[str, Any]
    embeddings: List[List[float]]
    search_results: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    final_output: str

class CitadelLangGraphOrchestrator:
    """
    LangGraph-based orchestration for stateful AI workflows
    """
    
    def __init__(
        self,
        embedding_service,
        vector_store,
        llm_service
    ):
        """Initialize LangGraph orchestrator"""
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service
        
        # Create workflow graph
        self.workflow = StateGraph(WorkflowState)
        self._build_workflow()
        
        # Compile with memory
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)
    
    def _build_workflow(self):
        """Build the workflow graph"""
        
        # Add nodes
        self.workflow.add_node("input_processing", self.process_input)
        self.workflow.add_node("embedding_generation", self.generate_embeddings)
        self.workflow.add_node("vector_search", self.search_vectors)
        self.workflow.add_node("content_analysis", self.analyze_content)
        self.workflow.add_node("response_generation", self.generate_response)
        
        # Add edges
        self.workflow.set_entry_point("input_processing")
        self.workflow.add_edge("input_processing", "embedding_generation")
        self.workflow.add_edge("embedding_generation", "vector_search")
        self.workflow.add_edge("vector_search", "content_analysis")
        self.workflow.add_edge("content_analysis", "response_generation")
        self.workflow.add_edge("response_generation", END)
        
        # Add conditional edges for error handling
        self.workflow.add_conditional_edges(
            "embedding_generation",
            self.should_retry_embedding,
            {
                "retry": "embedding_generation",
                "continue": "vector_search",
                "error": END
            }
        )
    
    async def process_input(self, state: WorkflowState) -> WorkflowState:
        """Process initial input"""
        
        messages = state.get("messages", [])
        if not messages:
            return state
        
        latest_message = messages[-1]
        
        # Extract query from message
        query = latest_message.content if hasattr(latest_message, 'content') else str(latest_message)
        
        # Update context
        state["context"]["user_query"] = query
        state["current_step"] = "input_processed"
        
        return state
    
    async def generate_embeddings(self, state: WorkflowState) -> WorkflowState:
        """Generate embeddings for the query"""
        
        query = state["context"].get("user_query", "")
        
        try:
            # Generate embedding using your embedding service
            embedding = await self.embedding_service.generate_embedding(
                text=query,
                model="nomic-embed-text"
            )
            
            state["embeddings"] = [embedding]
            state["current_step"] = "embeddings_generated"
            
        except Exception as e:
            state["context"]["embedding_error"] = str(e)
            state["current_step"] = "embedding_failed"
        
        return state
    
    async def search_vectors(self, state: WorkflowState) -> WorkflowState:
        """Search vector database"""
        
        embeddings = state.get("embeddings", [])
        if not embeddings:
            return state
        
        try:
            # Search vectors
            search_results = await self.vector_store.similarity_search(
                collection_name="citadel_documents",
                query_vector=embeddings[0],
                limit=5
            )
            
            state["search_results"] = search_results["results"]
            state["current_step"] = "vectors_searched"
            
        except Exception as e:
            state["context"]["search_error"] = str(e)
            state["current_step"] = "search_failed"
        
        return state
    
    async def analyze_content(self, state: WorkflowState) -> WorkflowState:
        """Analyze retrieved content"""
        
        search_results = state.get("search_results", [])
        user_query = state["context"].get("user_query", "")
        
        if not search_results:
            return state
        
        try:
            # Prepare context from search results
            context_text = "\n\n".join([
                result.get("payload", {}).get("content", "")
                for result in search_results
            ])
            
            # Analyze content
            analysis_prompt = f"""
            Based on the following context, provide a comprehensive analysis for the query: "{user_query}"
            
            Context:
            {context_text}
            
            Analysis:
            """
            
            analysis = await self.llm_service.generate_response(
                prompt=analysis_prompt,
                max_tokens=500
            )
            
            state["analysis_results"] = {
                "analysis": analysis,
                "context_used": len(search_results),
                "confidence": self._calculate_confidence(search_results)
            }
            state["current_step"] = "content_analyzed"
            
        except Exception as e:
            state["context"]["analysis_error"] = str(e)
            state["current_step"] = "analysis_failed"
        
        return state
    
    async def generate_response(self, state: WorkflowState) -> WorkflowState:
        """Generate final response"""
        
        analysis = state.get("analysis_results", {}).get("analysis", "")
        user_query = state["context"].get("user_query", "")
        
        try:
            # Generate final response
            response_prompt = f"""
            User Query: {user_query}
            
            Analysis: {analysis}
            
            Provide a clear, actionable response that directly addresses the user's query:
            """
            
            final_response = await self.llm_service.generate_response(
                prompt=response_prompt,
                max_tokens=300
            )
            
            state["final_output"] = final_response
            state["current_step"] = "response_generated"
            
            # Add AI message to conversation
            state["messages"].append(AIMessage(content=final_response))
            
        except Exception as e:
            state["context"]["response_error"] = str(e)
            state["current_step"] = "response_failed"
        
        return state
    
    def should_retry_embedding(self, state: WorkflowState) -> str:
        """Decide whether to retry embedding generation"""
        
        if state["current_step"] == "embedding_failed":
            retry_count = state["context"].get("embedding_retry_count", 0)
            if retry_count < 3:
                state["context"]["embedding_retry_count"] = retry_count + 1
                return "retry"
            else:
                return "error"
        
        return "continue"
    
    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Calculate based on similarity scores
        scores = [result.get("score", 0.0) for result in search_results]
        return sum(scores) / len(scores) if scores else 0.0
    
    async def run_workflow(
        self,
        user_input: str,
        workflow_id: str,
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """Run the complete workflow"""
        
        initial_state = WorkflowState(
            messages=[HumanMessage(content=user_input)],
            current_step="starting",
            workflow_id=workflow_id,
            context={"user_query": user_input},
            embeddings=[],
            search_results=[],
            analysis_results={},
            final_output=""
        )
        
        # Run workflow with state persistence
        config = {"configurable": {"thread_id": thread_id}}
        
        final_state = await self.app.ainvoke(
            initial_state,
            config=config
        )
        
        return {
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "final_output": final_state["final_output"],
            "analysis_results": final_state["analysis_results"],
            "messages": [msg.content for msg in final_state["messages"]],
            "current_step": final_state["current_step"]
        }
```

#### **4. LiveKit - Real-time Communication**
**Purpose**: Real-time audio/video communication and collaboration
```python
"""
LiveKit Integration for Real-time Communication
"""
from livekit import rtc, api
import asyncio
from typing import Dict, Any, Optional, Callable
import json
import logging

class CitadelLiveKitManager:
    """
    LiveKit integration for real-time collaboration and streaming
    """
    
    def __init__(
        self,
        livekit_url: str,
        api_key: str,
        api_secret: str
    ):
        """Initialize LiveKit manager"""
        self.livekit_url = livekit_url
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Initialize API client
        self.api_client = api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret
        )
        
        self.active_rooms: Dict[str, rtc.Room] = {}
        self.event_handlers: Dict[str, Callable] = {}
        
        logger = logging.getLogger(__name__)
    
    async def create_orchestration_room(
        self,
        room_name: str,
        max_participants: int = 10
    ) -> Dict[str, Any]:
        """Create a room for AI orchestration collaboration"""
        
        try:
            # Create room
            room_info = await self.api_client.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=300,  # 5 minutes
                    max_participants=max_participants,
                    metadata=json.dumps({
                        "type": "ai_orchestration",
                        "features": ["screen_share", "ai_assistance", "real_time_analysis"]
                    })
                )
            )
            
            return {
                "room_name": room_name,
                "room_sid": room_info.sid,
                "created_at": room_info.creation_time,
                "max_participants": max_participants
            }
            
        except Exception as e:
            logger.error(f"Failed to create room {room_name}: {e}")
            raise
    
    async def generate_access_token(
        self,
        room_name: str,
        participant_identity: str,
        participant_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate access token for room participant"""
        
        # Create access token
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_identity)
        token.with_name(participant_name)
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True
            )
        )
        
        if metadata:
            token.with_metadata(json.dumps(metadata))
        
        return token.to_jwt()
    
    async def connect_to_room(
        self,
        room_name: str,
        participant_token: str
    ) -> rtc.Room:
        """Connect to a LiveKit room"""
        
        room = rtc.Room()
        
        # Set up event handlers
        @room.on("connected")
        def on_connected():
            logger.info(f"Connected to room {room_name}")
        
        @room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant {participant.identity} connected")
            # Send welcome message with AI capabilities
            asyncio.create_task(
                self.send_ai_welcome_message(room, participant)
            )
        
        @room.on("data_received")
        def on_data_received(data: rtc.DataPacket):
            asyncio.create_task(
                self.handle_real_time_data(room, data)
            )
        
        # Connect to room
        await room.connect(
            url=self.livekit_url,
            token=participant_token
        )
        
        self.active_rooms[room_name] = room
        return room
    
    async def send_ai_welcome_message(
        self,
        room: rtc.Room,
        participant: rtc.RemoteParticipant
    ):
        """Send AI-powered welcome message"""
        
        welcome_data = {
            "type": "ai_welcome",
            "message": f"Welcome {participant.name}! AI Orchestration features available:",
            "features": [
                "Real-time document analysis",
                "Live embedding generation",
                "Collaborative AI workflows",
                "Voice-to-text transcription"
            ],
            "commands": [
                "/analyze <text> - Analyze text with AI",
                "/embed <text> - Generate embeddings",
                "/workflow <name> - Start AI workflow"
            ]
        }
        
        await room.local_participant.publish_data(
            json.dumps(welcome_data).encode(),
            destination=[participant.sid]
        )
    
    async def handle_real_time_data(
        self,
        room: rtc.Room,
        data: rtc.DataPacket
    ):
        """Handle real-time data messages"""
        
        try:
            message = json.loads(data.data.decode())
            message_type = message.get("type")
            
            if message_type == "ai_command":
                await self.process_ai_command(room, data.participant, message)
            elif message_type == "embedding_request":
                await self.process_embedding_request(room, data.participant, message)
            elif message_type == "workflow_trigger":
                await self.process_workflow_trigger(room, data.participant, message)
                
        except Exception as e:
            logger.error(f"Error processing real-time data: {e}")
    
    async def process_ai_command(
        self,
        room: rtc.Room,
        participant: rtc.RemoteParticipant,
        message: Dict[str, Any]
    ):
        """Process AI command from participant"""
        
        command = message.get("command", "")
        text = message.get("text", "")
        
        if command == "analyze":
            # Perform real-time text analysis
            analysis_result = await self.perform_real_time_analysis(text)
            
            response = {
                "type": "ai_response",
                "command": "analyze",
                "result": analysis_result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Broadcast to all participants
            await room.local_participant.publish_data(
                json.dumps(response).encode()
            )
    
    async def process_embedding_request(
        self,
        room: rtc.Room,
        participant: rtc.RemoteParticipant,
        message: Dict[str, Any]
    ):
        """Process real-time embedding request"""
        
        text = message.get("text", "")
        model = message.get("model", "nomic-embed-text")
        
        # This would integrate with your embedding service
        # embedding = await self.embedding_service.generate_embedding(text, model)
        
        response = {
            "type": "embedding_response",
            "text": text,
            "model": model,
            # "embedding": embedding,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await room.local_participant.publish_data(
            json.dumps(response).encode(),
            destination=[participant.sid]
        )
    
    async def process_workflow_trigger(
        self,
        room: rtc.Room,
        participant: rtc.RemoteParticipant,
        message: Dict[str, Any]
    ):
        """Process workflow trigger from participant"""
        
        workflow_name = message.get("workflow_name", "")
        workflow_params = message.get("parameters", {})
        
        # Start collaborative workflow
        workflow_id = f"live_{room.name}_{workflow_name}_{int(asyncio.get_event_loop().time())}"
        
        # This would integrate with your workflow orchestration
        # workflow_result = await self.workflow_service.start_workflow(
        #     workflow_name, workflow_params, workflow_id
        # )
        
        response = {
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "status": "running",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Broadcast workflow start to all participants
        await room.local_participant.publish_data(
            json.dumps(response).encode()
        )
    
    async def perform_real_time_analysis(self, text: str) -> Dict[str, Any]:
        """Perform real-time text analysis"""
        
        # This is a placeholder - integrate with your AI services
        return {
            "text_length": len(text),
            "word_count": len(text.split()),
            "sentiment": "neutral",  # Would use actual sentiment analysis
            "key_topics": ["AI", "orchestration"],  # Would use actual topic extraction
            "confidence": 0.85
        }
    
    async def broadcast_ai_update(
        self,
        room_name: str,
        update_data: Dict[str, Any]
    ):
        """Broadcast AI processing updates to room"""
        
        room = self.active_rooms.get(room_name)
        if not room:
            return
        
        message = {
            "type": "ai_update",
            "data": update_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await room.local_participant.publish_data(
            json.dumps(message).encode()
        )
    
    async def disconnect_from_room(self, room_name: str):
        """Disconnect from room and cleanup"""
        
        room = self.active_rooms.get(room_name)
        if room:
            await room.disconnect()
            del self.active_rooms[room_name]
```

## Framework Integration Benefits

### **Why These Frameworks Are Essential:**

1. **Pydantic**: 
   - Type safety and validation for all API requests/responses
   - Settings management with environment variable support
   - Data serialization for complex AI model outputs

2. **LangChain**:
   - Standardized interface for multiple LLM providers
   - Chain-based workflows for complex AI operations
   - Built-in vector store integrations (including Qdrant)
   - Agent framework for autonomous AI decision-making

3. **LangGraph**:
   - Stateful workflows with checkpointing and recovery
   - Complex multi-step AI processes with branching logic
   - Memory management for long-running conversations
   - Error handling and retry mechanisms

4. **LiveKit**:
   - Real-time collaboration on AI workflows
   - Voice-to-text integration for natural interaction
   - Live streaming of AI processing results
   - Multi-user AI assistance sessions

## Implementation Priority

**Immediate (Task 1-2)**: Pydantic for all data models
**Phase 2 (Task 3-4)**: LangChain for LLM integration  
**Phase 3 (Task 5)**: LangGraph for complex workflows
**Phase 4 (Task 5-6)**: LiveKit for real-time features

These frameworks transform the orchestration server from a simple API into a comprehensive AI collaboration platform.
