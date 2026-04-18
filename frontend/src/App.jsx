import FormPanel from './components/FormPanel/FormPanel'
import ChatPanel from './components/ChatPanel/ChatPanel'

/**
 * App — Root component.
 * Renders the full-screen split layout:
 *   Left 50%  → FormPanel (read-only, AI-controlled)
 *   Right 50% → ChatPanel (AI assistant)
 */
const App = () => {
  return (
    <div className="app-shell">
      {/* ── Global Header ── */}
      <header className="app-header" role="banner">
        <span className="app-header__logo" aria-hidden="true">🧬</span>
        <span className="app-header__title">AI-First CRM · HCP Interaction Module</span>
        <span className="app-header__subtitle">Powered by LangGraph + Groq</span>
      </header>

      {/* ── Split Screen ── */}
      <main className="app-split" role="main">
        <FormPanel />
        <div className="panel-divider" role="separator" aria-hidden="true" />
        <ChatPanel />
      </main>
    </div>
  )
}

export default App
