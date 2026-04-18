import { useState, useRef, useEffect, useCallback } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { bulkUpdate } from '../../store/formSlice'
import { sendChatMessage } from '../../api/chatApi'
import LoadingDots from '../shared/LoadingDots'
import './ChatPanel.css'

/**
 * ChatPanel — Right 50% of the split screen.
 * WhatsApp-style AI chat interface that drives all form updates.
 * 
 * Flow:
 *   User types → POST /chat (with current form) → LangGraph → response
 *   → dispatch bulkUpdate(updated_form) → FormPanel re-renders
 */

// Quick-action hint chips
const HINT_CHIPS = [
  { label: '📝 Log interaction', value: 'Met Dr. Mehta today, discussed oncology drug, shared brochure, positive response' },
  { label: '✏️ Edit field',     value: 'Change the sentiment to neutral' },
  { label: '💡 Get suggestions', value: 'What should I do next based on this interaction?' },
  { label: '📋 Summarize',      value: 'Summarize this interaction for my records' },
  { label: '✅ Compliance',     value: 'Check this interaction for compliance issues' },
]

const formatTime = (date) =>
  date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const ChatPanel = () => {
  const dispatch   = useDispatch()
  const formData   = useSelector((state) => state.form.formData)

  const [messages, setMessages]   = useState([])
  const [input, setInput]         = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [lastIntent, setLastIntent] = useState(null)
  const [error, setError]         = useState(null)

  const messagesEndRef = useRef(null)
  const textareaRef    = useRef(null)

  // Auto-scroll to latest message
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, isLoading, scrollToBottom])

  // Auto-resize textarea
  const handleInputChange = (e) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px'
  }

  // ── Send message ─────────────────────────────────────────────────────────
  const sendMessage = async (text) => {
    const msg = (text || input).trim()
    if (!msg || isLoading) return

    // Append user message
    const userMsg = { id: Date.now(), role: 'user', text: msg, time: new Date() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setError(null)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    setIsLoading(true)

    try {
      const response = await sendChatMessage(msg, formData)

      // Dispatch Redux update (null values filtered inside slice)
      if (response.updated_form) {
        dispatch(bulkUpdate(response.updated_form))
      }

      // Track detected intent for badge display
      if (response.intent) setLastIntent(response.intent)

      // Append AI message
      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        text: response.ai_message || 'Action completed.',
        time: new Date(),
        intent: response.intent,
      }
      setMessages((prev) => [...prev, aiMsg])

    } catch (err) {
      const errText = err?.response?.data?.detail || err.message || 'Connection error.'
      setError(errText)
      const errMsg = {
        id: Date.now() + 1,
        role: 'ai',
        text: `⚠️ Error: ${errText}\n\nPlease ensure the backend is running at http://localhost:8000`,
        time: new Date(),
        isError: true,
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle Enter key (Shift+Enter = new line)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Click a hint chip
  const handleChipClick = (value) => {
    sendMessage(value)
  }

  // Click a welcome example
  const handleExampleClick = (example) => {
    setInput(example)
    textareaRef.current?.focus()
  }

  const intentColors = {
    log: '#1E6FD9',
    edit: '#8B5CF6',
    suggest: '#F59E0B',
    summarize: '#10B981',
    compliance: '#EF4444',
  }

  return (
    <section className="chat-panel" aria-label="AI Chat Assistant">
      {/* ── Header ── */}
      <div className="chat-header">
        <div className="chat-header__avatar" aria-hidden="true">🤖</div>
        <div className="chat-header__info">
          <div className="chat-header__name">AI CRM Assistant</div>
          <div className="chat-header__status">
            <span className="chat-header__status-dot" aria-hidden="true"></span>
            LangGraph · Groq gemma2-9b-it
          </div>
        </div>
        {lastIntent && (
          <span
            className="chat-header__intent-badge"
            style={{ backgroundColor: intentColors[lastIntent] + '20', color: intentColors[lastIntent] }}
            title="Last detected intent"
          >
            {lastIntent}
          </span>
        )}
      </div>

      {/* ── Quick hint chips ── */}
      <div className="chat-hints" role="toolbar" aria-label="Quick actions">
        {HINT_CHIPS.map((chip) => (
          <button
            key={chip.label}
            className="hint-chip"
            onClick={() => handleChipClick(chip.value)}
            disabled={isLoading}
            title={chip.value}
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* ── Messages ── */}
      <div className="chat-messages" role="log" aria-live="polite" aria-label="Chat messages">

        {/* Welcome screen when no messages */}
        {messages.length === 0 && !isLoading && (
          <div className="chat-welcome">
            <span className="chat-welcome__icon">🧬</span>
            <h2 className="chat-welcome__title">AI-Powered HCP Interaction Logger</h2>
            <p className="chat-welcome__desc">
              Describe your HCP interaction in natural language. The AI will extract
              all details and fill the form automatically — no manual input needed.
            </p>
            <div className="chat-welcome__examples">
              {[
                'Met Dr. Mehta today, discussed oncology drug, shared brochure, positive response',
                'Phone call with Dr. Priya, talked about CardioMax, she wants a follow-up next week',
                'What should I do next after this interaction?',
                'Check this interaction for compliance issues',
              ].map((ex) => (
                <button
                  key={ex}
                  className="chat-welcome__example"
                  onClick={() => handleExampleClick(ex)}
                  aria-label={`Use example: ${ex}`}
                >
                  "{ex}"
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message list */}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-row message-row--${msg.role}`}
            role="article"
            aria-label={`${msg.role === 'user' ? 'You' : 'AI'}: ${msg.text}`}
          >
            <div className={`message-avatar message-avatar--${msg.role}`} aria-hidden="true">
              {msg.role === 'ai' ? '🤖' : '👤'}
            </div>
            <div>
              {msg.role === 'ai' && msg.intent && (
                <div
                  className="message-intent-tag"
                  style={{
                    backgroundColor: (intentColors[msg.intent] || '#1E6FD9') + '18',
                    color: intentColors[msg.intent] || '#1E6FD9',
                  }}
                >
                  {msg.intent}
                </div>
              )}
              <div
                className={`message-bubble message-bubble--${msg.role}${msg.isError ? ' message-bubble--error' : ''}`}
                style={msg.isError ? { borderColor: 'var(--clr-danger)', background: '#FFF5F5' } : {}}
              >
                {msg.text}
              </div>
              <div className={`message-time message-time--${msg.role}`}>
                {formatTime(msg.time)}
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="message-row message-row--ai message-row--loading" aria-live="polite" aria-label="AI is thinking">
            <div className="message-avatar message-avatar--ai" aria-hidden="true">🤖</div>
            <div>
              <div className="message-bubble message-bubble--ai" style={{ padding: '10px 16px' }}>
                <LoadingDots />
              </div>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      {/* ── Input Area ── */}
      <div className="chat-input-area">
        <form
          className="chat-input-form"
          onSubmit={(e) => { e.preventDefault(); sendMessage() }}
          aria-label="Send message to AI"
        >
          <div className="chat-input-wrapper">
            <textarea
              id="chat-input"
              ref={textareaRef}
              className="chat-textarea"
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Describe your HCP interaction… (Enter to send, Shift+Enter for new line)"
              rows={1}
              disabled={isLoading}
              aria-label="Chat message input"
              autoComplete="off"
            />
          </div>
          <button
            id="btn-send-message"
            type="submit"
            className="chat-send-btn"
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
            title="Send"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </form>
        <p className="chat-input-hint">
          AI reads your message → extracts data → fills the form automatically
        </p>
      </div>
    </section>
  )
}

export default ChatPanel
