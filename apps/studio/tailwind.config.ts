import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: { 50: "#eff6ff", 100: "#dbeafe", 500: "#3b82f6", 600: "#2563eb", 700: "#1d4ed8" },
        evidence: { supported: "#22c55e", attacked: "#ef4444", neutral: "#6b7280" },
      },
    },
  },
  plugins: [],
};
export default config;