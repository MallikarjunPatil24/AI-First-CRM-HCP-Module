import { createSlice } from '@reduxjs/toolkit'

/**
 * Redux slice for the HCP interaction form.
 *
 * Rules:
 * - The form is NEVER edited manually by the user.
 * - All updates come via bulkUpdate dispatched after an AI response.
 * - setField is available for individual updates if needed by tools.
 * - resetForm clears everything back to initial empty state.
 */

const initialFormData = {
  hcp_name: '',
  date: '',
  interaction_type: '',
  sentiment: '',
  products_discussed: [],
  materials_shared: [],
  follow_up_required: false,
  notes: '',
}

const formSlice = createSlice({
  name: 'form',
  initialState: {
    formData: { ...initialFormData },
    lastUpdatedFields: [],   // tracks which fields changed in the last AI response
  },
  reducers: {
    /**
     * Update a single field by name.
     * @param {string} action.payload.field  - field key
     * @param {*}      action.payload.value  - new value
     */
    setField: (state, action) => {
      const { field, value } = action.payload
      if (field in state.formData) {
        state.formData[field] = value
        state.lastUpdatedFields = [field]
      }
    },

    /**
     * Merge a partial form object from the AI response.
     * Null / undefined values from AI are skipped to preserve existing data.
     * @param {object} action.payload - partial form dict from updated_form
     */
    bulkUpdate: (state, action) => {
      const updates = action.payload
      const changed = []
      for (const [key, value] of Object.entries(updates)) {
        if (key in state.formData && value !== null && value !== undefined) {
          state.formData[key] = value
          changed.push(key)
        }
      }
      state.lastUpdatedFields = changed
    },

    /** Reset the entire form to its initial empty state. */
    resetForm: (state) => {
      state.formData = { ...initialFormData }
      state.lastUpdatedFields = []
    },

    /** Clear the highlight tracking after animation completes. */
    clearHighlights: (state) => {
      state.lastUpdatedFields = []
    },
  },
})

export const { setField, bulkUpdate, resetForm, clearHighlights } = formSlice.actions
export default formSlice.reducer
