import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f1720",
        panel: "#17212b",
        ink: "#e7eef6",
        muted: "#9fb0c0",
        trust: "#36c2a3",
        risk: "#ef596f",
        signal: "#5aa9ff",
        warning: "#f4b84a"
      },
      boxShadow: {
        glow: "0 0 40px rgba(54, 194, 163, 0.14)"
      }
    }
  },
  plugins: []
};

export default config;
