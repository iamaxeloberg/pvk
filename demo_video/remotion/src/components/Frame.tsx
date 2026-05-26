import { AbsoluteFill } from "remotion";
import { FONT_STYLESHEET, NOTHING } from "../theme";

/**
 * Outer frame shared by every composition.
 * - Injects the Google Fonts stylesheet
 * - Provides the pure-black background
 * - Adds subtle horizontal grid lines for the industrial feel
 */
export const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      <style>{FONT_STYLESHEET}</style>
      <AbsoluteFill style={{ background: NOTHING.bg }}>
        {/* Faint horizontal grid lines */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `linear-gradient(to bottom, ${NOTHING.faint} 1px, transparent 1px)`,
            backgroundSize: "100% 60px",
            opacity: 0.35,
            pointerEvents: "none",
          }}
        />
        {/* Vertical edge markers */}
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: 32,
            width: 1,
            background: NOTHING.faint,
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            right: 32,
            width: 1,
            background: NOTHING.faint,
          }}
        />
        {children}
      </AbsoluteFill>
    </>
  );
};

/** Striped horizontal pattern — used as section dividers / pacing markers */
export const StripeBar: React.FC<{ height?: number; segments?: number }> = ({
  height = 4,
  segments = 60,
}) => {
  const cells = Array.from({ length: segments });
  return (
    <div style={{ display: "flex", gap: 4, width: "100%" }}>
      {cells.map((_, i) => (
        <div
          key={i}
          style={{
            flex: 1,
            height,
            background: i % 3 === 0 ? NOTHING.fg : NOTHING.muted,
            opacity: i % 3 === 0 ? 0.9 : 0.25,
          }}
        />
      ))}
    </div>
  );
};

/** Single thin horizontal rule */
export const Rule: React.FC<{ color?: string }> = ({ color = NOTHING.divider }) => (
  <div style={{ width: "100%", height: 1, background: color }} />
);

/** A small dot — mimics the Nothing brand glyph */
export const Dot: React.FC<{ size?: number; color?: string }> = ({
  size = 10,
  color = NOTHING.fg,
}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: "50%",
      background: color,
      display: "inline-block",
    }}
  />
);
