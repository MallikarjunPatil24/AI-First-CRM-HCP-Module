import axios from 'axios'

const API_BASE = 'http://localhost:8000'

/**
 * Send a user message to the LangGraph agent.
 * @param {string} message      - raw user chat message
 * @param {object} currentForm  - current Redux form state
 * @returns {{ updated_form, ai_message, intent }}
 */
export const sendChatMessage = async (message, currentForm) => {
  const response = await axios.post(`${API_BASE}/chat`, {
    message,
    current_form: currentForm,
  })
  return response.data
}

/**
 * Persist the finalized interaction form to PostgreSQL.
 * @param {object} formData - current form state to save
 * @returns {{ id, message }}
 */
export const saveInteraction = async (formData) => {
  const response = await axios.post(`${API_BASE}/save`, {
    form_data: formData,
  })
  return response.data
}
