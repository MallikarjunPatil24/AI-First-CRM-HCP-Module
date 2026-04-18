/**
 * LoadingDots — Animated three-dot typing indicator.
 * Shown in the chat panel while waiting for an AI response.
 */
const LoadingDots = () => (
  <div className="loading-dots" aria-label="AI is thinking">
    <span></span>
    <span></span>
    <span></span>
  </div>
)

export default LoadingDots
