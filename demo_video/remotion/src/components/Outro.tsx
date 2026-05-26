import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, NOTHING } from "../theme";
import { Dot, Frame, Rule, StripeBar } from "./Frame";

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const opacity = interpolate(
    frame,
    [0, 14, durationInFrames - 12, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <Frame>
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 60,
          right: 60,
          display: "flex",
          justifyContent: "space-between",
          fontFamily: FONTS.sans,
          fontSize: 16,
          color: NOTHING.dim,
          letterSpacing: 4,
          opacity,
        }}
      >
        <div>// END OF REEL</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Dot size={8} color={NOTHING.red} />
          <span>EOF</span>
        </div>
      </div>

      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          opacity,
        }}
      >
        <Img
          src={staticFile("quantera-logo.png")}
          style={{
            width: 980,
            height: "auto",
          }}
        />
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          left: 60,
          right: 60,
          bottom: 60,
          opacity,
        }}
      >
        <Rule color={NOTHING.muted} />
        <div style={{ marginTop: 14 }}>
          <StripeBar segments={80} height={3} />
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontFamily: FONTS.sans,
            fontSize: 14,
            color: NOTHING.muted,
            letterSpacing: 4,
            marginTop: 16,
          }}
        >
          <div>// GROUP 14</div>
          <div>[ DD1367 ] SOFTWARE ENGINEERING IN PROJECT FORM</div>
          <div>2026.05.28</div>
        </div>
      </div>
    </Frame>
  );
};
