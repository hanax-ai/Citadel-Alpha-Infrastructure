#!/usr/bin/env python3
"""
Open WebUI Agent Streaming Test Interface
Simple web interface to test the new agent streaming endpoints
"""

import asyncio
import aiohttp
import json
from aiohttp import web, web_request
from aiohttp_cors import setup as cors_setup, ResourceOptions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server-02 Gateway configuration
GATEWAY_BASE_URL = "http://localhost:8000"
TEST_MODEL = "qwen"

class StreamingTestServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
    
    def setup_cors(self):
        """Setup CORS for web interface"""
        cors = cors_setup(self.app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_post('/api/test/voice', self.test_voice_streaming)
        self.app.router.add_post('/api/test/copilot', self.test_copilot_streaming)
        self.app.router.add_post('/api/test/gui', self.test_gui_streaming)
        self.app.router.add_post('/api/test/generic', self.test_generic_streaming)
        self.app.router.add_get('/api/health', self.health_check)
    
    async def index(self, request):
        """Serve the main test interface"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Citadel Agent Streaming Test Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .agent-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .agent-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .agent-desc { color: #666; margin-bottom: 15px; }
        .test-controls { display: flex; gap: 10px; margin-bottom: 15px; }
        input[type="text"] { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .output { 
            background: #f8f9fa; 
            border: 1px solid #e9ecef; 
            border-radius: 4px; 
            padding: 15px; 
            min-height: 100px; 
            font-family: monospace; 
            font-size: 14px;
            white-space: pre-wrap;
            overflow-y: auto;
            max-height: 300px;
        }
        .stats { margin-top: 10px; font-size: 12px; color: #666; }
        .voice { border-left: 4px solid #ff6b6b; }
        .copilot { border-left: 4px solid #4ecdc4; }
        .gui { border-left: 4px solid #45b7d1; }
        .generic { border-left: 4px solid #96ceb4; }
        .status { padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; }
        .status.connected { background: #d4edda; color: #155724; }
        .status.streaming { background: #fff3cd; color: #856404; }
        .status.completed { background: #d1ecf1; color: #0c5460; }
        .status.error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Citadel Server-02 Agent Streaming Test Interface</h1>
        <p>Test the new agent-specific streaming endpoints with real-time response visualization.</p>
        
        <!-- Voice Agent Section -->
        <div class="agent-section voice">
            <div class="agent-title">🎤 Voice Agent - Real-time Speech Synthesis</div>
            <div class="agent-desc">Single token streaming optimized for TTS systems (10ms delays)</div>
            <div class="test-controls">
                <input type="text" id="voice-input" placeholder="Enter your message for voice agent..." value="Tell me a quick joke">
                <button onclick="testVoiceAgent()" id="voice-btn">Test Voice Streaming</button>
            </div>
            <div class="output" id="voice-output">Ready to test voice agent streaming...</div>
            <div class="stats" id="voice-stats"></div>
        </div>

        <!-- Copilot Agent Section -->
        <div class="agent-section copilot">
            <div class="agent-title">💻 Copilot Agent - Code Completion</div>
            <div class="agent-desc">5-token chunks optimized for IDE integration (100ms delays)</div>
            <div class="test-controls">
                <input type="text" id="copilot-input" placeholder="Enter your code completion request..." value="Write a Python function to calculate fibonacci">
                <button onclick="testCopilotAgent()" id="copilot-btn">Test Copilot Streaming</button>
            </div>
            <div class="output" id="copilot-output">Ready to test copilot agent streaming...</div>
            <div class="stats" id="copilot-stats"></div>
        </div>

        <!-- GUI Agent Section -->
        <div class="agent-section gui">
            <div class="agent-title">🖥️ GUI Agent - Chat Interface</div>
            <div class="agent-desc">10-token chunks optimized for chat UIs (200ms delays)</div>
            <div class="test-controls">
                <input type="text" id="gui-input" placeholder="Enter your chat message..." value="Explain machine learning in simple terms">
                <button onclick="testGUIAgent()" id="gui-btn">Test GUI Streaming</button>
            </div>
            <div class="output" id="gui-output">Ready to test GUI agent streaming...</div>
            <div class="stats" id="gui-stats"></div>
        </div>

        <!-- Generic Agent Section -->
        <div class="agent-section generic">
            <div class="agent-title">🔧 Generic Agent - Configurable</div>
            <div class="agent-desc">Configurable agent type via dropdown selection</div>
            <div class="test-controls">
                <input type="text" id="generic-input" placeholder="Enter your message..." value="Hello from generic agent">
                <select id="generic-type" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                    <option value="voice">Voice (1-token chunks)</option>
                    <option value="copilot">Copilot (5-token chunks)</option>
                    <option value="gui" selected>GUI (10-token chunks)</option>
                </select>
                <button onclick="testGenericAgent()" id="generic-btn">Test Generic Streaming</button>
            </div>
            <div class="output" id="generic-output">Ready to test generic agent streaming...</div>
            <div class="stats" id="generic-stats"></div>
        </div>
    </div>

    <script>
        async function streamTest(endpoint, message, outputId, statsId, btnId) {
            const output = document.getElementById(outputId);
            const stats = document.getElementById(statsId);
            const btn = document.getElementById(btnId);
            
            // Reset UI
            output.innerHTML = 'Connecting to streaming endpoint...\\n';
            output.innerHTML += `<span class="status connected">CONNECTED</span> Starting stream...\\n\\n`;
            stats.innerHTML = '';
            btn.disabled = true;
            
            const startTime = Date.now();
            let chunkCount = 0;
            let totalContent = '';
            let firstChunkTime = null;
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        model: "${TEST_MODEL}",
                        messages: [{"role": "user", "content": message}],
                        max_tokens: 100
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                output.innerHTML += `<span class="status streaming">STREAMING</span> Receiving chunks...\\n\\n`;
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            if (firstChunkTime === null) {
                                firstChunkTime = Date.now();
                                const ttft = (firstChunkTime - startTime) / 1000;
                                output.innerHTML += `⚡ Time to first token: ${ttft.toFixed(3)}s\\n\\n`;
                            }
                            
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                output.innerHTML += `\\n<span class="status completed">COMPLETED</span> Stream finished\\n`;
                                break;
                            }
                            
                            try {
                                const parsed = JSON.parse(data);
                                if (parsed.choices && parsed.choices[0] && parsed.choices[0].delta && parsed.choices[0].delta.content) {
                                    const content = parsed.choices[0].delta.content;
                                    totalContent += content;
                                    chunkCount++;
                                    output.innerHTML += `📦 Chunk ${chunkCount}: "${content}"\\n`;
                                    output.scrollTop = output.scrollHeight;
                                }
                            } catch (e) {
                                // Skip malformed JSON
                            }
                        }
                    }
                }
                
                const totalTime = (Date.now() - startTime) / 1000;
                const avgChunkTime = totalTime / Math.max(chunkCount, 1);
                
                stats.innerHTML = `
                    ✅ Chunks: ${chunkCount} | 
                    ✅ Content: ${totalContent.length} chars | 
                    ✅ Total time: ${totalTime.toFixed(3)}s | 
                    ✅ Avg chunk time: ${avgChunkTime.toFixed(3)}s
                `;
                
                output.innerHTML += `\\n📊 Final content: "${totalContent}"\\n`;
                
            } catch (error) {
                output.innerHTML += `\\n<span class="status error">ERROR</span> ${error.message}\\n`;
                stats.innerHTML = `❌ Test failed: ${error.message}`;
            } finally {
                btn.disabled = false;
            }
        }
        
        async function testVoiceAgent() {
            const message = document.getElementById('voice-input').value;
            await streamTest('${GATEWAY_BASE_URL}/v1/voice/chat/completions', message, 'voice-output', 'voice-stats', 'voice-btn');
        }
        
        async function testCopilotAgent() {
            const message = document.getElementById('copilot-input').value;
            await streamTest('${GATEWAY_BASE_URL}/v1/copilot/completions', message, 'copilot-output', 'copilot-stats', 'copilot-btn');
        }
        
        async function testGUIAgent() {
            const message = document.getElementById('gui-input').value;
            await streamTest('${GATEWAY_BASE_URL}/v1/gui/chat/completions', message, 'gui-output', 'gui-stats', 'gui-btn');
        }
        
        async function testGenericAgent() {
            const message = document.getElementById('generic-input').value;
            const agentType = document.getElementById('generic-type').value;
            await streamTest(`${GATEWAY_BASE_URL}/v1/agents/stream?agent_type=${agentType}`, message, 'generic-output', 'generic-stats', 'generic-btn');
        }
        
        // Auto-test on page load
        window.addEventListener('load', function() {
            console.log('Citadel Agent Streaming Test Interface loaded');
            console.log('Gateway URL:', '${GATEWAY_BASE_URL}');
        });
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def health_check(self, request):
        """Health check endpoint"""
        try:
            # Check gateway health
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{GATEWAY_BASE_URL}/health") as resp:
                    gateway_health = await resp.json() if resp.status == 200 else {"status": "unhealthy"}
            
            return web.json_response({
                "status": "ok",
                "test_server": "running",
                "gateway_health": gateway_health
            })
        except Exception as e:
            return web.json_response({
                "status": "error",
                "error": str(e)
            }, status=500)
    
    async def test_voice_streaming(self, request):
        """Test voice streaming endpoint"""
        return await self._proxy_to_gateway(request, "/v1/voice/chat/completions")
    
    async def test_copilot_streaming(self, request):
        """Test copilot streaming endpoint"""
        return await self._proxy_to_gateway(request, "/v1/copilot/completions")
    
    async def test_gui_streaming(self, request):
        """Test GUI streaming endpoint"""
        return await self._proxy_to_gateway(request, "/v1/gui/chat/completions")
    
    async def test_generic_streaming(self, request):
        """Test generic streaming endpoint"""
        agent_type = request.query.get('agent_type', 'gui')
        return await self._proxy_to_gateway(request, f"/v1/agents/stream?agent_type={agent_type}")
    
    async def _proxy_to_gateway(self, request, endpoint):
        """Proxy streaming request to gateway"""
        try:
            data = await request.json()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{GATEWAY_BASE_URL}{endpoint}", json=data) as resp:
                    if resp.status != 200:
                        return web.json_response({
                            "error": f"Gateway error: {resp.status}"
                        }, status=resp.status)
                    
                    # Stream the response
                    response = web.StreamResponse()
                    response.headers['Content-Type'] = 'text/event-stream'
                    response.headers['Cache-Control'] = 'no-cache'
                    response.headers['Connection'] = 'keep-alive'
                    await response.prepare(request)
                    
                    async for chunk in resp.content.iter_chunked(1024):
                        await response.write(chunk)
                    
                    await response.write_eof()
                    return response
                    
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            return web.json_response({"error": str(e)}, status=500)

def main():
    """Run the test server"""
    server = StreamingTestServer()
    
    print("🚀 Starting Citadel Agent Streaming Test Server")
    print("=" * 60)
    print(f"📡 Gateway URL: {GATEWAY_BASE_URL}")
    print(f"🌐 Test Interface: http://localhost:8080")
    print(f"🤖 Test Model: {TEST_MODEL}")
    print("=" * 60)
    print("🎤 Voice Agent: /v1/voice/chat/completions")
    print("💻 Copilot Agent: /v1/copilot/completions") 
    print("🖥️ GUI Agent: /v1/gui/chat/completions")
    print("🔧 Generic Agent: /v1/agents/stream")
    print("=" * 60)
    
    web.run_app(server.app, host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
