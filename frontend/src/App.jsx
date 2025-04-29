import React, { useState, useRef, useEffect } from 'react';
import { sendMessageToBackend } from './services/api';
import MathRenderer from './components/MathRenderer';
import { v4 as uuidv4 } from 'uuid'
import { MathJaxContext } from 'better-react-mathjax';
import './App.css';
import logo from '/logo.png'; // or '/logo.svg'

// Optional: Configure MathJax 
const mathJaxConfig = {

};

function App() {
  // Initial disclaimer message
  const initialDisclaimer = {
    type: 'ai',
    text: "Hi! I'm an AI STEM tutor based on open-source models. I can help with problem-solving strategies in subjects like Algebra. Remember, I'm still learning, so please double-check my answers and use critical thinking! Let's focus on STEM topics."
  };
  const [inputMessage, setInputMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([initialDisclaimer]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [threadId, setThreadId] = useState(null);
  const [agentThoughts, setAgentThoughts] = useState('');
  const [showThoughts, setShowThoughts] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    
    let currentThreadId = localStorage.getItem('chatThreadId');
    if (!currentThreadId) {
      currentThreadId = `web-session-${uuidv4()}`; 
      localStorage.setItem('chatThreadId', currentThreadId);
    }
    setThreadId(currentThreadId);
    console.log("Using Thread ID:", currentThreadId); // For debugging

    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleInputChange = (event) => {
    setInputMessage(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!inputMessage.trim() || isLoading || !threadId) return;

    const userMessage = inputMessage;
    console.log("Sending message:", userMessage);
    setInputMessage('');
    setError(null);
    setChatHistory(prev => [...prev, { type: 'user', text: userMessage, timestamp: Date.now() }]);
    setIsLoading(true);

    try {
      const { answer, thoughts } = await sendMessageToBackend(userMessage, threadId);
      console.log("Received reply:", answer);
      setChatHistory(prev => [...prev, { type: 'ai', text: answer, timestamp: Date.now() }]);
      setAgentThoughts(thoughts); // Save thoughts for display
    } catch (err) {
      console.error("Failed to get reply:", err);
      const errorMessage = err.message || "Failed to connect to the AI. Please try again.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  function formatAgentThoughts(thoughts) {
    if (!thoughts) return <em>No reasoning steps available for this answer.</em>;
    // Split by double newlines or single newlines for each step
    const lines = thoughts.split('\n').filter(Boolean);
    return (
      <div className="reasoning-steps">
        {lines.map((line, idx) => {
          let className = '';
          if (line.startsWith('Thought:')) className = 'reasoning-thought';
          else if (line.startsWith('Action:')) className = 'reasoning-action';
          else if (line.startsWith('Action Input:')) className = 'reasoning-action-input';
          else if (line.startsWith('Observation:')) className = 'reasoning-observation';
          return (
            <div key={idx} className={className}>
              {line}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    // Wrap the app with MathJaxProvider
    <MathJaxContext config={mathJaxConfig} /* Optional: Pass config */ >
      <div className="App">
        <header className="app-header">
          <img src={logo} alt="STEMnity AI Logo" className="app-logo" />
          <h1>STEMnity AI</h1>
        </header>
        <p className="disclaimer-header"> Please verify answers.</p>
        <div className="chat-window">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              {msg.type === 'user' && (
                <p>
                  <strong>You:</strong> {msg.text}
                  <span
                    className="timestamp"
                    title={msg.timestamp ? new Date(msg.timestamp).toLocaleString() : ''}
                  >
                    {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </p>
              )}
              {msg.type === 'ai' && (
                <div>
                  <strong>Tutor:</strong>
                  <MathRenderer text={msg.text} />
                  <span
                    className="timestamp"
                    title={msg.timestamp ? new Date(msg.timestamp).toLocaleString() : ''}
                  >
                    {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </div>
              )}
            </div>
          ))}
           {/* Improved Loading Indicator */}
          {isLoading && <div className="message ai typing-indicator"><span></span><span></span><span></span></div>}
          {error && (
            <div className="message error">
              <p>
                <strong>Error:</strong> {error}
                <button onClick={() => setError(null)} style={{marginLeft: 10}}>✕</button>
              </p>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={inputMessage}
            onChange={handleInputChange}
            placeholder="Ask a STEM question..."
            disabled={isLoading}
            autoFocus
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
        <div className="agent-thoughts-window">
          <button
            className="toggle-thoughts-btn"
            onClick={() => setShowThoughts((prev) => !prev)}
          >
            {showThoughts ? "Hide" : "Show"} Agent's Reasoning
          </button>
          {showThoughts && (
            <div className="thoughts-content">
              <h3>Agent's Reasoning</h3>
              {formatAgentThoughts(agentThoughts)}
            </div>
          )}
        </div>
        <p className="disclaimer-footer">
        AI generated content may contain errors. Focus on STEM topics.
      </p>
      </div>
    </MathJaxContext> 
  );
}

export default App;