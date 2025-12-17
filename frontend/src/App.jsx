import { useState, useEffect } from 'react';
import { Sparkles, Send, ArrowLeft } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showChat, setShowChat] = useState(false);

  // Add right after: const [showChat, setShowChat] = useState(false);

useEffect(() => {
  const handlePopState = (event) => {
    if (event.state?.showChat === false || !event.state) {
      setShowChat(false);
      setMessages([]);
      setInput('');
    }
  };

  window.addEventListener('popstate', handlePopState);

  if (!window.history.state) {
    window.history.replaceState({ showChat: false }, '', '/');
  }

  return () => window.removeEventListener('popstate', handlePopState);
}, []);


  const suggestedQuestions = [
    "What are the core courses for MS DS?",
    "How many classes do I need to take to graduate?",
    "Create a plan for MS in CS"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Find where you set setShowChat(true) in handleSubmit
// Add these 3 lines BEFORE it:

    if (!showChat) {
      window.history.pushState({ showChat: true }, '', '/chat');
    }
    setShowChat(true);

    const userMessage = input.trim();
    setInput('');
    setShowChat(true);
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer || 'Sorry, I couldn\'t process that request.' 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error connecting to the server.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (question) => {
    setInput(question);
    // Add this line after setInput(question):
    window.history.pushState({ showChat: true }, '', '/chat');
    setShowChat(true);
  };

  return (
    <div className="app">
      <div className="container">
        {!showChat ? (
          <div className="landing">
            <div className="sparkle-icon">
              <Sparkles size={48} strokeWidth={1.5} />
            </div>
            
            <h1 className="title">Welcome to ColumbiaCourse AI!</h1>
            <p className="subtitle">Your AI-powered degree planner</p>

            <div className="suggestions">
              <p className="try-asking">Try asking:</p>
              <div className="suggestion-grid">
                {suggestedQuestions.map((question, idx) => (
                  <button
                    key={idx}
                    className="suggestion-card"
                    onClick={() => handleSuggestionClick(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="input-form">
              <div className="input-wrapper">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything about your degree plans/requirements"
                  className="chat-input"
                />
                <button 
                  type="submit" 
                  className="send-button"
                  disabled={!input.trim()}
                >
                  <Send size={20} />
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="chat-view">
            <div className="chat-header">
              <div className="header-content">
                <Sparkles size={24} strokeWidth={1.5} />
                <h2>ColumbiaCourse AI</h2>
              </div>
            </div>

            <div className="messages-container">
              {messages.map((message, idx) => (
                <div key={idx} className={`message ${message.role}`}>
                  <div className="message-content">
                    {message.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <div className="message-content loading">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleSubmit} className="chat-input-form">
              <div className="input-wrapper">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything about your degree plans/requirements"
                  className="chat-input"
                />
                <button 
                  type="submit" 
                  className="send-button"
                  disabled={!input.trim() || isLoading}
                >
                  <Send size={20} />
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
