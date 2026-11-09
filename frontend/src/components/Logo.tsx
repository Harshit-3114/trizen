import React from "react";

interface LogoProps {
  size?: number;
  variant?: "dark" | "light";
  withWordmark?: boolean;
}

const BLADES = [0, 1, 2, 3, 4, 5];

const Logo: React.FC<LogoProps> = ({ size = 32, variant = "dark", withWordmark = true }) => {
  const color = variant === "dark" ? "#1C1917" : "#FAF7F2";
  return (
    <span className="logo" style={{ color }}>
      <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="Trizen Photos logo">
        <circle cx="32" cy="32" r="29" fill="none" stroke="currentColor" strokeWidth="4" />
        {BLADES.map((i) => (
          <path
            key={i}
            d="M32 5 L47 33 L32 28.5 L17 33 Z"
            fill="currentColor"
            transform={`rotate(${i * 60} 32 32)`}
          />
        ))}
      </svg>
      {withWordmark && (
        <span className="logo-word">
          <strong>Trizen</strong>
          <span>Photos</span>
        </span>
      )}
    </span>
  );
};

export default Logo;