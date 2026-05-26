import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, NOTHING } from "../theme";
import { Dot, Frame, Rule, StripeBar } from "./Frame";

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = (start: number, end: number) =>
    interpolate(frame, [start, end], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 12, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const headerOpacity = Math.min(fadeIn(0, 10), fadeOut);
  const logoOpacity = Math.min(fadeIn(8, 26), fadeOut);
  const taglineOpacity = Math.min(fadeIn(22, 38), fadeOut);
  const footerOpacity = Math.min(fadeIn(32, 48), fadeOut);
  const logoScale = interpolate(frame, [8, 26], [0.96, 1], { extrapolateRight: "clamp" });

  return (
    <Frame>
      {/* Top header */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 60,
          right: 60,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontFamily: FONTS.sans,
          fontSize: 16,
          color: NOTHING.dim,
          letterSpacing: 4,
          opacity: headerOpacity,
        }}
      >
        <div>// QUANTERA / SYSTEM REEL</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Dot size={8} color={NOTHING.red} />
          <span>REC 0001</span>
        </div>
      </div>

      {/* Center stack */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 48,
        }}
      >
        <Img
          src={staticFile("quantera-logo.png")}
          style={{
            width: 1100,
            height: "auto",
            opacity: logoOpacity,
            transform: `scale(${logoScale})`,
          }}
        />

        <div
          style={{
            opacity: taglineOpacity,
            display: "flex",
            alignItems: "center",
            gap: 24,
            fontFamily: FONTS.sans,
            fontSize: 20,
            color: NOTHING.dim,
            letterSpacing: 8,
          }}
        >
          <div style={{ width: 60, height: 1, background: NOTHING.red }} />
          <span>FINANCIAL · DOCUMENT · INTELLIGENCE</span>
          <div style={{ width: 60, height: 1, background: NOTHING.red }} />
        </div>
      </AbsoluteFill>

      {/* Bottom strip */}
      <div
        style={{
          position: "absolute",
          left: 60,
          right: 60,
          bottom: 60,
          opacity: footerOpacity,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontFamily: FONTS.sans,
            fontSize: 14,
            color: NOTHING.muted,
            letterSpacing: 4,
            marginBottom: 16,
          }}
        >
          <div>[ 0008 ] QUERIES</div>
          <div>[ DEMO REEL — 03:00 ]</div>
          <div>DD1367 · GROUP 14</div>
        </div>
        <Rule color={NOTHING.muted} />
        <div style={{ marginTop: 14 }}>
          <StripeBar segments={80} height={3} />
        </div>
      </div>
    </Frame>
  );
};
