import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import type { Query } from "../queries";
import { RESPONSES } from "../responses";
import { FONTS, NOTHING } from "../theme";
import { Dot, Frame, Rule, StripeBar } from "./Frame";
import { TerminalSimulator } from "./TerminalSimulator";

type Props = {
  query: Query;
  queryIndex: number;
  totalQueries: number;
};

export const ClipFrame: React.FC<Props> = ({ query, queryIndex, totalQueries }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const response = RESPONSES[query.id];

  const isRobustness = query.category === "ROBUSTNESS";
  const queryNum = String(queryIndex + 1).padStart(2, "0");
  const totalNum = String(totalQueries).padStart(2, "0");

  return (
    <Frame>
      <AbsoluteFill style={{ opacity }}>
        {/* Top bar */}
        <div
          style={{
            position: "absolute",
            top: 50,
            left: 60,
            right: 60,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontFamily: FONTS.sans,
            fontSize: 16,
            color: NOTHING.dim,
            letterSpacing: 4,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <span>// {queryNum} / {totalNum}</span>
            <div style={{ width: 50, height: 1, background: NOTHING.muted }} />
            <span style={{ color: NOTHING.fg, textTransform: "uppercase" }}>
              {query.label}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <Dot size={8} color={isRobustness ? NOTHING.red : NOTHING.fg} />
            <span>[ {query.category} ]</span>
          </div>
        </div>

        {/* Terminal area */}
        <div
          style={{
            position: "absolute",
            top: 110,
            left: 60,
            right: 60,
            bottom: 110,
            border: `1px solid ${NOTHING.divider}`,
            overflow: "hidden",
          }}
        >
          {/* Terminal chrome / titlebar */}
          <div
            style={{
              height: 36,
              background: NOTHING.bgPanel,
              borderBottom: `1px solid ${NOTHING.divider}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 16px",
              fontFamily: FONTS.sans,
              fontSize: 12,
              color: NOTHING.muted,
              letterSpacing: 3,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Dot size={6} color={NOTHING.muted} />
              <Dot size={6} color={NOTHING.muted} />
              <Dot size={6} color={NOTHING.muted} />
              <span style={{ marginLeft: 12 }}>// QUANTERA SHELL</span>
            </div>
            <div>{query.id}</div>
          </div>

          {response ? (
            <div style={{ height: "calc(100% - 36px)" }}>
              <TerminalSimulator command={query.command} response={response} />
            </div>
          ) : (
            <div
              style={{
                color: NOTHING.muted,
                padding: 40,
                fontFamily: FONTS.mono,
                fontSize: 18,
              }}
            >
              [ no response defined for {query.id} ]
            </div>
          )}
        </div>

        {/* Bottom strip */}
        <div
          style={{
            position: "absolute",
            left: 60,
            right: 60,
            bottom: 50,
          }}
        >
          <Rule color={NOTHING.muted} />
          <div
            style={{
              marginTop: 12,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontFamily: FONTS.sans,
              fontSize: 13,
              color: NOTHING.muted,
              letterSpacing: 3,
            }}
          >
            <span>{query.description}</span>
            <span>R-{queryNum}</span>
          </div>
          <div style={{ marginTop: 8 }}>
            <StripeBar segments={60} height={2} />
          </div>
        </div>
      </AbsoluteFill>
    </Frame>
  );
};
