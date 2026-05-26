import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import type { Query } from "../queries";
import { FONTS, NOTHING } from "../theme";
import { Dot, Frame, Rule, StripeBar } from "./Frame";

type Props = {
  query: Query;
  queryIndex: number;
  totalQueries: number;
};

export const LabelCard: React.FC<Props> = ({ query, queryIndex, totalQueries }) => {
  const frame = useCurrentFrame();

  const fadeIn = (start: number, end: number) =>
    interpolate(frame, [start, end], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  const fadeOut = interpolate(frame, [70, 80], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const headerOpacity = Math.min(fadeIn(0, 8), fadeOut);
  const labelOpacity = Math.min(fadeIn(6, 18), fadeOut);
  const descOpacity = Math.min(fadeIn(14, 26), fadeOut);
  const cmdOpacity = Math.min(fadeIn(22, 36), fadeOut);
  const yOffset = interpolate(frame, [6, 22], [16, 0], { extrapolateRight: "clamp" });

  const queryNum = String(queryIndex + 1).padStart(2, "0");
  const totalNum = String(totalQueries).padStart(2, "0");
  const isRobustness = query.category === "ROBUSTNESS";

  return (
    <Frame>
      {/* Top bar */}
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
        <div>// QUERY / {queryNum} OF {totalNum}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Dot size={8} color={isRobustness ? NOTHING.red : NOTHING.fg} />
          <span>[ {query.category} ]</span>
        </div>
      </div>

      {/* Center */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 120px",
          gap: 40,
        }}
      >
        <div
          style={{
            opacity: labelOpacity,
            transform: `translateY(${yOffset}px)`,
            fontFamily: FONTS.dot,
            fontWeight: 700,
            fontSize: 130,
            color: NOTHING.fg,
            letterSpacing: 4,
            lineHeight: 1.05,
            textAlign: "center",
            textTransform: "uppercase",
          }}
        >
          {query.label}
        </div>

        <div
          style={{
            opacity: descOpacity,
            fontFamily: FONTS.sans,
            fontSize: 24,
            color: NOTHING.dim,
            letterSpacing: 3,
            textAlign: "center",
            maxWidth: 1400,
            lineHeight: 1.5,
          }}
        >
          {query.description}
        </div>

        <div
          style={{
            opacity: cmdOpacity,
            marginTop: 30,
            padding: "18px 32px",
            border: `1px solid ${NOTHING.divider}`,
            fontFamily: FONTS.mono,
            fontSize: 18,
            color: NOTHING.dim,
            letterSpacing: 0.5,
            maxWidth: 1500,
          }}
        >
          <span style={{ color: NOTHING.muted }}>$ </span>
          {query.command}
        </div>
      </AbsoluteFill>

      {/* Bottom strip */}
      <div
        style={{
          position: "absolute",
          left: 60,
          right: 60,
          bottom: 60,
          opacity: headerOpacity,
        }}
      >
        <Rule color={NOTHING.muted} />
        <div style={{ marginTop: 14 }}>
          <StripeBar segments={60} height={2} />
        </div>
      </div>
    </Frame>
  );
};
