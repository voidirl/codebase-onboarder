import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  // Which "screen" are we on?
  const [phase, setPhase] = useState('input') // 'input' | 'loading' | 'result'
  
  // Form state
  const [githubUrl, setGithubUrl] = useState('')
  
  // After /analyze responds
  const [repoId, setRepoId] = useState(null)
  const [onboardingDoc, setOnboardingDoc] = useState('')
  
  // Chat state
  const [chatHistory, setChatHistory] = useState([])
  const [question, setQuestion] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [error, setError] = useState(null)

  // Handler: analyze repo
  const handleAnalyze = async () => {
    if (!githubUrl.trim()) return
    setError(null)
    setPhase('loading')
    try {
      const res = await axios.post(`${API_BASE}/analyze`, { github_url: githubUrl })
      setRepoId(res.data.repo_id)
      setOnboardingDoc(res.data.onboarding_doc)
      setChatHistory([])
      setPhase('result')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
      setPhase('input')
    }
  }

  // Handler: send chat message
  const handleChat = async () => {
    if (!question.trim() || chatLoading) return
    const newHistory = [...chatHistory, { role: 'user', content: question }]
    setChatHistory(newHistory)
    setQuestion('')
    setChatLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        repo_id: repoId,
        question: question,
        chat_history: chatHistory,
      })
      setChatHistory([...newHistory, { role: 'assistant', content: res.data.answer }])
    } catch (err) {
      setChatHistory([...newHistory, { role: 'assistant', content: '⚠️ Error: ' + (err.response?.data?.detail || 'Failed to get answer') }])
    } finally {
      setChatLoading(false)
    }
  }

  // Render 
  if (phase === 'input' || phase === 'loading') {
    return (
      <div className="container">
        <h1>Codebase Onboarder</h1>
        <p className="subtitle">Paste a GitHub repo URL and get an onboarding guide instantly</p>
        <div className="input-row">
          <input
            className="url-input"
            type="text"
            placeholder="https://github.com/owner/repo"
            value={githubUrl}
            onChange={e => setGithubUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
            disabled={phase === 'loading'}
          />
          <button className="analyze-btn" onClick={handleAnalyze} disabled={phase === 'loading'}>
            {phase === 'loading' ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>
    )
  }

  return (
    <div className="container result-layout">
      {/* Left: Onboarding Doc */}
      <div className="doc-panel">
        <div className="panel-header">
          <span className="repo-id">{repoId}</span>
          <button className="back-btn" onClick={() => setPhase('input')}>← New Repo</button>
        </div>
        <pre className="onboarding-doc">{onboardingDoc}</pre>
      </div>

      {/* Right: Chat */}
      <div className="chat-panel">
        <div className="chat-header">Ask about this codebase</div>
        <div className="chat-messages">
          {chatHistory.length === 0 && (
            <p className="chat-empty">Ask anything about the repo...</p>
          )}
          {chatHistory.map((msg, i) => (
            <div key={i} className={`chat-msg ${msg.role}`}>
              <span className="msg-label">{msg.role === 'user' ? 'You' : 'AI'}</span>
              <p>{msg.content}</p>
            </div>
          ))}
          {chatLoading && <div className="chat-msg assistant"><span className="msg-label">AI</span><p>Thinking...</p></div>}
        </div>
        <div className="chat-input-row">
          <input
            className="chat-input"
            type="text"
            placeholder="Ask a question..."
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleChat()}
            disabled={chatLoading}
          />
          <button className="send-btn" onClick={handleChat} disabled={chatLoading}>Send</button>
        </div>
      </div>
    </div>
  )
}

export default App