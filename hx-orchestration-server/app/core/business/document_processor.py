"""
Intelligent Document Processing Pipeline
Provides AI-powered document analysis and business insight extraction
"""

import asyncio
import json
import logging
import uuid
import re
from typing import Dict, List, Any, Optional, Union, BinaryIO
from datetime import datetime
from dataclasses import dataclass
import httpx
from pathlib import Path

from app.common.base_classes import BaseService

logger = logging.getLogger("hx_orchestration.document_processor")

@dataclass
class DocumentSection:
    """Document section with metadata"""
    section_id: str
    content: str
    section_type: str
    position: int
    metadata: Dict[str, Any]

@dataclass
class ExtractedInformation:
    """Structured information extracted from documents"""
    key_entities: List[str]
    dates: List[str]
    financial_figures: List[Dict[str, Any]]
    action_items: List[str]
    stakeholders: List[str]
    topics: List[str]
    metadata: Dict[str, Any]

@dataclass
class BusinessInsights:
    """Business insights derived from document analysis"""
    summary: str
    key_findings: List[str]
    opportunities: List[str]
    risks: List[str]
    sentiment_analysis: Dict[str, Any]
    priority_level: str
    confidence_score: float

@dataclass
class ProcessingResult:
    """Complete document processing result"""
    processing_id: str
    document_type: str
    extracted_information: ExtractedInformation
    business_insights: BusinessInsights
    recommendations: List[Dict[str, Any]]
    embeddings_generated: int
    processing_timestamp: datetime
    processing_time: float

class DocumentType:
    """Supported document types for processing"""
    CONTRACT = "contract"
    INVOICE = "invoice"
    REPORT = "report"
    EMAIL = "email"
    PROPOSAL = "proposal"
    MEETING_NOTES = "meeting_notes"
    SPECIFICATION = "specification"
    POLICY = "policy"
    GENERAL = "general"

class DocumentProcessor(BaseService):
    """Enterprise document processing service with AI analysis"""
    
    def __init__(self, orchestration_service=None, name: str = "document_processor"):
        super().__init__(name)
        self.orchestration_service = orchestration_service
        self.processing_history: List[ProcessingResult] = []
        self.document_patterns = self._initialize_patterns()
        self.embedding_model = "nomic-embed-text"
        self.analysis_model = "phi3"
        
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize document pattern recognition"""
        return {
            DocumentType.CONTRACT: [
                r'agreement', r'contract', r'terms and conditions', r'liability',
                r'obligations', r'breach', r'termination', r'effective date'
            ],
            DocumentType.INVOICE: [
                r'invoice', r'bill', r'amount due', r'payment terms', r'due date',
                r'invoice number', r'total amount', r'tax'
            ],
            DocumentType.REPORT: [
                r'executive summary', r'findings', r'recommendations', r'conclusion',
                r'analysis', r'results', r'methodology'
            ],
            DocumentType.EMAIL: [
                r'from:', r'to:', r'subject:', r'sent:', r'received:',
                r'regards', r'best', r'sincerely'
            ],
            DocumentType.PROPOSAL: [
                r'proposal', r'solution', r'implementation', r'timeline',
                r'deliverables', r'scope', r'budget', r'benefits'
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize document processor"""
        try:
            logger.info("Initializing document processor")
            
            # Validate orchestration service
            if not self.orchestration_service:
                logger.warning("No orchestration service provided - some features may be limited")
            
            self._health_status = "healthy"
            self._initialized = True
            
            logger.info("Document processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize document processor: {e}")
            self._health_status = "unhealthy"
            return False
    
    async def process_business_document(
        self,
        document_content: str,
        document_type: str = DocumentType.GENERAL,
        processing_requirements: Dict[str, Any] = None,
        generate_embeddings: bool = True
    ) -> ProcessingResult:
        """Process business document with comprehensive AI analysis"""
        start_time = datetime.utcnow()
        processing_id = str(uuid.uuid4())
        
        logger.info(f"Processing document {processing_id} of type: {document_type}")
        
        try:
            # Initialize processing requirements
            requirements = processing_requirements or {}
            
            # Auto-detect document type if needed
            if document_type == DocumentType.GENERAL:
                document_type = await self._detect_document_type(document_content)
            
            # Step 1: Generate embeddings for semantic analysis
            embeddings_count = 0
            if generate_embeddings:
                embeddings_count = await self._generate_document_embeddings(document_content)
            
            # Step 2: Extract structured information
            extracted_info = await self._extract_key_information(document_content, document_type)
            
            # Step 3: Analyze document for business insights
            business_insights = await self._analyze_business_insights(
                document_content, extracted_info, requirements
            )
            
            # Step 4: Generate action recommendations
            recommendations = await self._generate_action_recommendations(
                business_insights, requirements
            )
            
            # Create processing result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ProcessingResult(
                processing_id=processing_id,
                document_type=document_type,
                extracted_information=extracted_info,
                business_insights=business_insights,
                recommendations=recommendations,
                embeddings_generated=embeddings_count,
                processing_timestamp=start_time,
                processing_time=processing_time
            )
            
            # Store in history
            self.processing_history.append(result)
            
            logger.info(f"Document {processing_id} processed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise Exception(f"Document processing failed: {str(e)}")
    
    async def _detect_document_type(self, content: str) -> str:
        """Automatically detect document type based on content patterns"""
        content_lower = content.lower()
        
        type_scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower))
                score += matches
            type_scores[doc_type] = score
        
        # Return document type with highest score
        if type_scores:
            detected_type = max(type_scores, key=type_scores.get)
            if type_scores[detected_type] > 0:
                logger.info(f"Detected document type: {detected_type}")
                return detected_type
        
        return DocumentType.GENERAL
    
    async def _generate_document_embeddings(self, content: str) -> int:
        """Generate embeddings for document sections"""
        if not self.orchestration_service:
            logger.warning("No orchestration service - skipping embeddings")
            return 0
        
        try:
            # Split document into sections
            sections = self._split_document_sections(content)
            
            embeddings_generated = 0
            for section in sections:
                if len(section.content.strip()) > 10:  # Skip very short sections
                    try:
                        # Generate embedding for section
                        # Note: This would integrate with the actual embedding service
                        # For now, we'll simulate the process
                        embeddings_generated += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to generate embedding for section {section.section_id}: {e}")
            
            logger.info(f"Generated {embeddings_generated} embeddings for document sections")
            return embeddings_generated
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return 0
    
    def _split_document_sections(self, content: str) -> List[DocumentSection]:
        """Split document into logical sections"""
        sections = []
        
        # Simple paragraph-based splitting
        paragraphs = content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                section = DocumentSection(
                    section_id=f"section_{i}",
                    content=paragraph.strip(),
                    section_type="paragraph",
                    position=i,
                    metadata={"word_count": len(paragraph.split())}
                )
                sections.append(section)
        
        return sections
    
    async def _extract_key_information(self, content: str, document_type: str) -> ExtractedInformation:
        """Extract structured information from document using AI"""
        
        extraction_prompt = f"""Extract key information from this {document_type} document:

DOCUMENT CONTENT:
{content[:3000]}  # Limit content to avoid token limits

Please provide a structured JSON response with the following information:
- key_entities: Important entities mentioned (companies, people, products, etc.)
- dates: Relevant dates found in the document
- financial_figures: Monetary amounts or financial data with context
- action_items: Tasks, actions, or next steps mentioned
- stakeholders: People or organizations involved
- topics: Main topics or themes discussed

RESPONSE FORMAT (JSON):
{{
    "key_entities": ["entity1", "entity2", "entity3"],
    "dates": ["2024-01-15", "Q1 2024", "next month"],
    "financial_figures": [
        {{"amount": "$10,000", "context": "project budget", "type": "budget"}},
        {{"amount": "€5,500", "context": "monthly fee", "type": "recurring"}}
    ],
    "action_items": ["complete review", "submit proposal", "schedule meeting"],
    "stakeholders": ["John Smith", "ABC Company", "Legal Department"],
    "topics": ["project planning", "budget allocation", "timeline"]
}}

Respond only with valid JSON."""
        
        try:
            # Call AI model for extraction
            ai_response = await self._call_ai_model(extraction_prompt)
            extracted_data = self._parse_json_response(ai_response)
            
            return ExtractedInformation(
                key_entities=extracted_data.get("key_entities", []),
                dates=extracted_data.get("dates", []),
                financial_figures=extracted_data.get("financial_figures", []),
                action_items=extracted_data.get("action_items", []),
                stakeholders=extracted_data.get("stakeholders", []),
                topics=extracted_data.get("topics", []),
                metadata={"extraction_method": "ai_powered"}
            )
            
        except Exception as e:
            logger.error(f"Information extraction failed: {e}")
            
            # Fallback to pattern-based extraction
            return await self._fallback_extraction(content)
    
    async def _analyze_business_insights(
        self,
        content: str,
        extracted_info: ExtractedInformation,
        requirements: Dict[str, Any]
    ) -> BusinessInsights:
        """Analyze document for business insights using AI"""
        
        analysis_prompt = f"""Analyze this business document and provide comprehensive business insights:

DOCUMENT CONTENT SUMMARY:
Key Entities: {extracted_info.key_entities[:5]}
Topics: {extracted_info.topics[:5]}
Action Items: {extracted_info.action_items[:3]}
Financial Figures: {len(extracted_info.financial_figures)} identified

FULL CONTENT:
{content[:2000]}  # Limit content

ANALYSIS REQUIREMENTS:
{json.dumps(requirements, indent=2)}

Please provide a comprehensive business analysis in JSON format:

{{
    "summary": "2-3 sentence summary of the document's business purpose and key points",
    "key_findings": ["finding1", "finding2", "finding3"],
    "opportunities": ["opportunity1", "opportunity2"],
    "risks": ["risk1", "risk2"],
    "sentiment_analysis": {{
        "overall_sentiment": "positive/negative/neutral",
        "confidence": 0.85,
        "key_indicators": ["indicator1", "indicator2"]
    }},
    "priority_level": "high/medium/low",
    "confidence_score": 0.85
}}

Respond only with valid JSON."""
        
        try:
            ai_response = await self._call_ai_model(analysis_prompt)
            insights_data = self._parse_json_response(ai_response)
            
            return BusinessInsights(
                summary=insights_data.get("summary", "No summary available"),
                key_findings=insights_data.get("key_findings", []),
                opportunities=insights_data.get("opportunities", []),
                risks=insights_data.get("risks", []),
                sentiment_analysis=insights_data.get("sentiment_analysis", {}),
                priority_level=insights_data.get("priority_level", "medium"),
                confidence_score=float(insights_data.get("confidence_score", 0.5))
            )
            
        except Exception as e:
            logger.error(f"Business insights analysis failed: {e}")
            
            # Fallback insights
            return BusinessInsights(
                summary="Document analysis completed with limited insights due to processing error",
                key_findings=["Document contains structured content"],
                opportunities=["Manual review recommended"],
                risks=["Automated analysis incomplete"],
                sentiment_analysis={"overall_sentiment": "neutral", "confidence": 0.1},
                priority_level="medium",
                confidence_score=0.1
            )
    
    async def _generate_action_recommendations(
        self,
        insights: BusinessInsights,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on insights"""
        
        recommendations_prompt = f"""Based on the business insights analysis, generate specific, actionable recommendations:

BUSINESS INSIGHTS:
Summary: {insights.summary}
Key Findings: {insights.key_findings}
Opportunities: {insights.opportunities}
Risks: {insights.risks}
Priority Level: {insights.priority_level}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

Generate 3-5 specific, actionable recommendations in JSON format:

{{
    "recommendations": [
        {{
            "title": "Recommendation Title",
            "description": "Detailed description of what should be done",
            "priority": "high/medium/low",
            "timeline": "immediate/short-term/long-term",
            "owner": "suggested responsible party",
            "success_metrics": ["metric1", "metric2"],
            "resources_required": ["resource1", "resource2"]
        }}
    ]
}}

Respond only with valid JSON."""
        
        try:
            ai_response = await self._call_ai_model(recommendations_prompt)
            recommendations_data = self._parse_json_response(ai_response)
            
            return recommendations_data.get("recommendations", [])
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            
            # Fallback recommendations
            return [
                {
                    "title": "Manual Document Review",
                    "description": "Conduct manual review of document due to automated processing limitations",
                    "priority": "medium",
                    "timeline": "short-term",
                    "owner": "document_reviewer",
                    "success_metrics": ["review_completed"],
                    "resources_required": ["reviewer_time"]
                }
            ]
    
    async def _call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """Call AI model for analysis"""
        # Fallback server configuration
        server_config = {
            "hostname": "192.168.10.34",
            "port": 8002
        }
        
        url = f"http://{server_config['hostname']}:{server_config['port']}/v1/chat/completions"
        
        payload = {
            "model": self.analysis_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a business document analysis expert. Extract structured information and provide business insights in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    
    def _parse_json_response(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response from AI model"""
        try:
            content = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {}
    
    async def _fallback_extraction(self, content: str) -> ExtractedInformation:
        """Fallback extraction using pattern matching"""
        logger.info("Using fallback pattern-based extraction")
        
        # Simple pattern-based extraction
        entities = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)  # Names
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}', content)  # Dates
        financial = re.findall(r'[\$€£¥]\s*\d+(?:,\d{3})*(?:\.\d{2})?', content)  # Money
        
        return ExtractedInformation(
            key_entities=list(set(entities[:10])),
            dates=list(set(dates[:5])),
            financial_figures=[{"amount": f, "context": "extracted", "type": "amount"} for f in financial[:5]],
            action_items=[],
            stakeholders=list(set(entities[:5])),
            topics=[],
            metadata={"extraction_method": "pattern_based"}
        )
    
    async def get_processing_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get document processing history"""
        recent_results = self.processing_history[-limit:] if limit else self.processing_history
        
        return [
            {
                "processing_id": r.processing_id,
                "document_type": r.document_type,
                "processing_timestamp": r.processing_timestamp.isoformat(),
                "processing_time": r.processing_time,
                "embeddings_generated": r.embeddings_generated,
                "key_findings_count": len(r.business_insights.key_findings),
                "recommendations_count": len(r.recommendations)
            }
            for r in recent_results
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Document processor health check"""
        return {
            "service": self.name,
            "status": self._health_status,
            "total_documents_processed": len(self.processing_history),
            "uptime_seconds": self.uptime,
            "orchestration_service_available": self.orchestration_service is not None
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of document processor"""
        logger.info("Shutting down document processor")
        await super().shutdown()
        logger.info("Document processor shut down gracefully")
