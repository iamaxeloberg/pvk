// Nothing-inspired design tokens.
// - Pure black backgrounds, white text, single red accent.
// - Dot-matrix font (Doto from Google Fonts) for headings.
// - Wide letter-spacing, ALL CAPS, bracketed serial numbers.

export const NOTHING = {
  bg: "#000000",
  bgPanel: "#0a0a0a",
  fg: "#ffffff",
  dim: "#9a9a9a",
  muted: "#5a5a5a",
  faint: "#2e2e2e",
  red: "#ff3232",
  divider: "#262626",
};

export const FONTS = {
  // Dot-matrix display font — closest free alternative to Nothing's NDot
  dot: "'Doto', 'Major Mono Display', monospace",
  // Wide tracking sans for body / labels
  sans: "'Space Mono', 'IBM Plex Mono', monospace",
  // Terminal mono
  mono: "'JetBrains Mono', 'Fira Code', 'Menlo', monospace",
};

// Google Fonts stylesheet — injected at the top of every composition frame.
export const FONT_STYLESHEET = `
  @import url('https://fonts.googleapis.com/css2?family=Doto:wght@300;500;700;900&family=Space+Mono:wght@400;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
`;
