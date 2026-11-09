import React from "react";

interface EmptyStateProps {
  title: string;
  hint: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({ title, hint }) => (
  <div className="empty-state">
    <svg width="56" height="56" viewBox="0 0 64 64" aria-hidden="true">
      <circle cx="32" cy="32" r="29" fill="none" stroke="#B45309" strokeWidth="3" />
      <circle cx="32" cy="32" r="9" fill="none" stroke="#B45309" strokeWidth="3" />
      <line x1="32" y1="3" x2="32" y2="16" stroke="#B45309" strokeWidth="3" />
      <line x1="32" y1="48" x2="32" y2="61" stroke="#B45309" strokeWidth="3" />
      <line x1="3" y1="32" x2="16" y2="32" stroke="#B45309" strokeWidth="3" />
      <line x1="48" y1="32" x2="61" y2="32" stroke="#B45309" strokeWidth="3" />
    </svg>
    <h3>{title}</h3>
    <p className="muted">{hint}</p>
  </div>
);

export default EmptyState;