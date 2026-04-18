import { useSelector, useDispatch } from 'react-redux'
import { useEffect, useRef, useState } from 'react'
import { resetForm, clearHighlights } from '../../store/formSlice'
import { saveInteraction } from '../../api/chatApi'
import './FormPanel.css'

/**
 * FormPanel — Left 50% of the split screen.
 * Renders all HCP interaction form fields as READ-ONLY (disabled).
 * Fields auto-populate via Redux when the AI sends a bulkUpdate.
 * Highlights recently-updated fields with a flash animation.
 */
const FormPanel = () => {
  const dispatch = useDispatch()
  const { formData, lastUpdatedFields } = useSelector((state) => state.form)

  const [saveStatus, setSaveStatus] = useState(null) // null | 'saving' | 'success' | 'error'
  const [saveMessage, setSaveMessage] = useState('')
  const highlightTimerRef = useRef(null)

  // Clear highlight classes after animation completes
  useEffect(() => {
    if (lastUpdatedFields.length > 0) {
      clearTimeout(highlightTimerRef.current)
      highlightTimerRef.current = setTimeout(() => {
        dispatch(clearHighlights())
      }, 1600)
    }
    return () => clearTimeout(highlightTimerRef.current)
  }, [lastUpdatedFields, dispatch])

  const isHighlighted = (field) => lastUpdatedFields.includes(field)

  const isFormEmpty = !formData.hcp_name && !formData.date && !formData.interaction_type

  // ── Save to DB ───────────────────────────────────────────────────────────
  const handleSave = async () => {
    if (isFormEmpty) return
    setSaveStatus('saving')
    try {
      const result = await saveInteraction(formData)
      setSaveStatus('success')
      setSaveMessage(`✓ Saved (ID: ${result.id})`)
    } catch {
      setSaveStatus('error')
      setSaveMessage('Save failed. Check backend.')
    }
    setTimeout(() => setSaveStatus(null), 3500)
  }

  const handleReset = () => {
    dispatch(resetForm())
    setSaveStatus(null)
  }

  // ── Helpers ──────────────────────────────────────────────────────────────
  const sentimentClass = formData.sentiment
    ? `sentiment-badge sentiment-badge--${formData.sentiment}`
    : ''

  const sentimentEmoji = { positive: '😊', neutral: '😐', negative: '😟' }

  return (
    <section className="form-panel" aria-label="HCP Interaction Form">
      {/* ── Header ── */}
      <div className="form-panel__header">
        <div className="form-panel__header-row">
          <h1 className="form-panel__title">
            <span className="form-panel__title-icon">📋</span>
            HCP Interaction Record
          </h1>
          <span className="form-panel__badge">READ-ONLY</span>
        </div>
        <p className="form-panel__subtitle">
          All fields controlled by AI assistant →
        </p>
      </div>

      {/* ── Body ── */}
      <div className="form-panel__body">

        {/* Empty state hint */}
        {isFormEmpty && (
          <div className="form-empty-hint" role="status">
            <span className="form-empty-hint__icon">🤖</span>
            <p className="form-empty-hint__text">
              Start chatting on the right to auto-fill this form.<br />
              Try: <em>"Met Dr. Mehta today, discussed oncology drug…"</em>
            </p>
          </div>
        )}

        {/* ── Section: Interaction Details ── */}
        <div className="form-section">
          <span className="form-section__title">Interaction Details</span>

          <div className="form-row">
            <div className="form-field">
              <label className="form-field__label" htmlFor="field-hcp-name">
                <span className="form-field__label-icon">👤</span> HCP Name
              </label>
              <input
                id="field-hcp-name"
                type="text"
                className={`form-input ${isHighlighted('hcp_name') ? 'is-updated' : ''}`}
                value={formData.hcp_name || ''}
                disabled
                placeholder="Auto-filled by AI"
                readOnly
              />
            </div>

            <div className="form-field">
              <label className="form-field__label" htmlFor="field-date">
                <span className="form-field__label-icon">📅</span> Date
              </label>
              <input
                id="field-date"
                type="text"
                className={`form-input ${isHighlighted('date') ? 'is-updated' : ''}`}
                value={formData.date || ''}
                disabled
                placeholder="YYYY-MM-DD"
                readOnly
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label className="form-field__label" htmlFor="field-interaction-type">
                <span className="form-field__label-icon">🔗</span> Interaction Type
              </label>
              <input
                id="field-interaction-type"
                type="text"
                className={`form-input ${isHighlighted('interaction_type') ? 'is-updated' : ''}`}
                value={formData.interaction_type || ''}
                disabled
                placeholder="in-person / phone / email / virtual"
                readOnly
              />
            </div>

            <div className="form-field">
              <label className="form-field__label" htmlFor="field-sentiment">
                <span className="form-field__label-icon">💬</span> Sentiment
              </label>
              {formData.sentiment ? (
                <div
                  id="field-sentiment"
                  className={`followup-display ${isHighlighted('sentiment') ? 'is-updated' : ''}`}
                >
                  <span className={sentimentClass}>
                    {sentimentEmoji[formData.sentiment]} {formData.sentiment}
                  </span>
                </div>
              ) : (
                <input
                  id="field-sentiment"
                  type="text"
                  className={`form-input ${isHighlighted('sentiment') ? 'is-updated' : ''}`}
                  value=""
                  disabled
                  placeholder="positive / neutral / negative"
                  readOnly
                />
              )}
            </div>
          </div>
        </div>

        {/* ── Section: Products & Materials ── */}
        <div className="form-section">
          <span className="form-section__title">Products &amp; Materials</span>

          <div className="form-field">
            <label className="form-field__label">
              <span className="form-field__label-icon">💊</span> Products Discussed
            </label>
            <div
              className={`tag-list ${isHighlighted('products_discussed') ? 'is-updated' : ''}`}
              role="list"
              aria-label="Products discussed"
            >
              {formData.products_discussed && formData.products_discussed.length > 0
                ? formData.products_discussed.map((p, i) => (
                    <span key={i} className="tag-pill" role="listitem">{p}</span>
                  ))
                : <span style={{ color: 'var(--clr-text-muted)', fontSize: '13px', alignSelf: 'center' }}>
                    No products logged yet
                  </span>
              }
            </div>
          </div>

          <div className="form-field">
            <label className="form-field__label">
              <span className="form-field__label-icon">📄</span> Materials Shared
            </label>
            <div
              className={`tag-list ${isHighlighted('materials_shared') ? 'is-updated' : ''}`}
              role="list"
              aria-label="Materials shared"
            >
              {formData.materials_shared && formData.materials_shared.length > 0
                ? formData.materials_shared.map((m, i) => (
                    <span key={i} className="tag-pill tag-pill--accent" role="listitem">{m}</span>
                  ))
                : <span style={{ color: 'var(--clr-text-muted)', fontSize: '13px', alignSelf: 'center' }}>
                    No materials logged yet
                  </span>
              }
            </div>
          </div>
        </div>

        {/* ── Section: Follow-up & Notes ── */}
        <div className="form-section">
          <span className="form-section__title">Follow-up &amp; Notes</span>

          <div className="form-field">
            <label className="form-field__label">
              <span className="form-field__label-icon">🔔</span> Follow-up Required
            </label>
            <div
              className={`followup-display ${isHighlighted('follow_up_required') ? 'is-updated' : ''}`}
              role="status"
              aria-label={`Follow-up ${formData.follow_up_required ? 'required' : 'not required'}`}
            >
              <div
                className={`followup-display__indicator ${
                  formData.follow_up_required ? 'followup-display__indicator--checked' : ''
                }`}
              >
                {formData.follow_up_required && '✓'}
              </div>
              <span className="followup-display__text">
                {formData.follow_up_required
                  ? 'Yes — Follow-up required'
                  : 'No follow-up required'}
              </span>
            </div>
          </div>

          <div className="form-field">
            <label className="form-field__label" htmlFor="field-notes">
              <span className="form-field__label-icon">📝</span> Notes
            </label>
            <textarea
              id="field-notes"
              className={`form-input ${isHighlighted('notes') ? 'is-updated' : ''}`}
              value={formData.notes || ''}
              disabled
              placeholder="AI-generated interaction notes will appear here…"
              readOnly
            />
          </div>
        </div>
      </div>

      {/* ── Footer Actions ── */}
      <div className="form-panel__footer">
        <button
          id="btn-reset-form"
          className="btn btn--secondary"
          onClick={handleReset}
          title="Clear all form fields"
        >
          🔄 Reset
        </button>
        <button
          id="btn-save-interaction"
          className="btn btn--success"
          onClick={handleSave}
          disabled={isFormEmpty || saveStatus === 'saving'}
          title="Save interaction to database"
        >
          {saveStatus === 'saving' ? '⏳ Saving…' : '💾 Save Interaction'}
        </button>
        {saveStatus && saveStatus !== 'saving' && (
          <span
            className={`save-status save-status--${saveStatus === 'success' ? 'success' : 'error'}`}
            role="status"
          >
            {saveMessage}
          </span>
        )}
      </div>
    </section>
  )
}

export default FormPanel
