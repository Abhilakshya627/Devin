"""
Web-based Devin AI Assistant using FastAPI
No LiveKit required - works through web browser
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import asyncio
import json
import logging
from typing import Dict, List
import uvicorn

# Import your existing modules
from gemini_client import get_gemini_client
from devin_system import system_status_report
from voice_interaction import speak_text

app = FastAPI(title="Devin AI Assistant", description="Web-based AI Assistant")
logger = logging.getLogger(__name__)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

class WebDevin:
    """Web-based Devin AI Assistant."""
    
    def __init__(self):
        self.gemini_client = get_gemini_client()
    
    async def process_message(self, message: str) -> Dict:
        """Process user message and return response."""
        try:
            # Use Gemini to process the request
            prompt = f"""
            As Devin, a helpful AI assistant, respond to this message:
            
            User: {message}
            
            Provide a helpful, intelligent response as Devin would.
            Be concise but thorough.
            """
            
            response = await self.gemini_client.generate_content(prompt)
            
            return {
                "type": "response",
                "message": response,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "type": "error", 
                "message": f"Sorry, I encountered an error: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }

web_devin = WebDevin()

@app.get("/")
async def get_homepage():
    """Serve the main web interface."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Devin AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .chat-container { border: 1px solid #333; border-radius: 10px; height: 400px; overflow-y: auto; padding: 15px; background: #2a2a2a; margin-bottom: 20px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #0066cc; text-align: right; }
            .devin-message { background: #006600; }
            .input-container { display: flex; gap: 10px; }
            #messageInput { flex: 1; padding: 10px; border: 1px solid #333; border-radius: 5px; background: #2a2a2a; color: #fff; }
            #sendButton { padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 5px; cursor: pointer; }
            #sendButton:hover { background: #0052a3; }
            .status { text-align: center; color: #666; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Devin AI Assistant</h1>
                <p>Your intelligent desktop companion</p>
            </div>
            
            <div id="status" class="status">Connecting...</div>
            
            <div id="chatContainer" class="chat-container">
                <div class="message devin-message">
                    Hello! I'm Devin, your AI assistant. How can I help you today?
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Type your message here..." />
                <button id="sendButton">Send</button>
            </div>
        </div>

        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const chatContainer = document.getElementById("chatContainer");
            const messageInput = document.getElementById("messageInput");
            const sendButton = document.getElementById("sendButton");
            const status = document.getElementById("status");

            ws.onopen = function(event) {
                status.textContent = "Connected to Devin";
                status.style.color = "#00cc00";
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.message, "devin-message");
            };

            ws.onclose = function(event) {
                status.textContent = "Disconnected from Devin";
                status.style.color = "#cc0000";
            };

            function addMessage(message, className) {
                const messageDiv = document.createElement("div");
                messageDiv.className = "message " + className;
                messageDiv.textContent = message;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                if (message) {
                    addMessage(message, "user-message");
                    ws.send(JSON.stringify({type: "message", content: message}));
                    messageInput.value = "";
                }
            }

            sendButton.addEventListener("click", sendMessage);
            messageInput.addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time chat."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                # Process the message
                response = await web_devin.process_message(message_data["content"])
                
                # Send response back to client
                await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/api/status")
async def get_status():
    """Get system status."""
    try:
        status = await system_status_report(context=None)
        return {"status": "online", "details": status}
    except Exception as e:
        return {"status": "error", "details": str(e)}

def run_web_server():
    """Run the web server."""
    print("🌐 Starting Devin Web Interface...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🔴 Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_web_server()
