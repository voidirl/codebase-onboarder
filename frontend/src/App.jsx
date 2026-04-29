import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [phase, setPhase] = useState('input')
  const [githubUrl, setGithubUrl] = useState('')
  const [repoId, setRepoId] = useState(null)
  const [onboardingDoc, setOnboardingDoc] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [question, setQuestion] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [error, setError] = useState(null)
  const chatBottomRef = useRef(null)

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory, chatLoading])

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
      setChatHistory([...newHistory, { role: 'assistant', content: '⚠️ ' + (err.response?.data?.detail || 'Failed to get answer') }])
    } finally {
      setChatLoading(false)
    }
  }

  if (phase === 'input' || phase === 'loading') {
    return (
      <div className="container">
        <div className="hero-badge">AI-Powered</div>
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
            {phase === 'loading' ? <span className="spinner" /> : 'Analyze'}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        {phase === 'loading' && <p className="loading-text">Fetching repo and generating onboarding doc...</p>}
      </div>
    )
  }

  return (
    <div className="container result-layout">
      <div className="doc-panel">
        <div className="panel-header">
          <div className="panel-header-left">
            <span className="repo-pill">{repoId}</span>
          </div>
          <button className="back-btn" onClick={() => setPhase('input')}>← New Repo</button>
        </div>
        <div className="onboarding-doc">
          <ReactMarkdown>{onboardingDoc}</ReactMarkdown>
        </div>
      </div>

      <div className="chat-panel">
        <div className="chat-header">
          <span>💬 Ask about this codebase</span>
        </div>
        <div className="chat-messages">
          {chatHistory.length === 0 && (
            <div className="chat-empty">
              <p>🤖 Ask anything about <strong>{repoId}</strong></p>
              <p className="chat-empty-sub">Architecture, setup, key files, how things work...</p>
            </div>
          )}
          {chatHistory.map((msg, i) => (
            <div key={i} className={`chat-msg ${msg.role}`}>
              <span className="msg-label">{msg.role === 'user' ? '🧑 You' : '🤖 AI'}</span>
              <div className="msg-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          {chatLoading && (
            <div className="chat-msg assistant">
              <span className="msg-label">🤖 AI</span>
              <div className="msg-content typing">
                <span /><span /><span />
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
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
          <button className="send-btn" onClick={handleChat} disabled={chatLoading}>
            {chatLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App