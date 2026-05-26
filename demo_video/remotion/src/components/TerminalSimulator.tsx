import { useCurrentFrame, useVideoConfig } from "remotion";
import type { Response } from "../responses";
import { FONTS, NOTHING } from "../theme";

type Props = {
  command: string;
  response: Response;
};

// Inline colour markup palette — all monochrome with a single red accent,
// matching the Nothing visual language.
const TOKEN_COLORS: Record<string, string> = {
  accent: NOTHING.fg,
  bold: NOTHING.fg,
  muted: NOTHING.muted,
  red: NOTHING.red,
  green: NOTHING.fg,
  yellow: NOTHING.fg,
};

const TOKEN_WEIGHT: Record<string, number> = {
  accent: 700,
  bold: 700,
  muted: 400,
  red: 700,
  green: 500,
  yellow: 500,
};

const renderLine = (line: string): React.ReactNode => {
  const parts: React.ReactNode[] = [];
  const regex = /\{(accent|red|green|yellow|bold|muted)\}([^{]*)\{\/\}/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(line)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={key++}>{line.slice(lastIndex, match.index)}</span>);
    }
    const tag = match[1];
    parts.push(
      <span
        key={key++}
        style={{
          color: TOKEN_COLORS[tag] ?? NOTHING.fg,
          fontWeight: TOKEN_WEIGHT[tag] ?? 400,
        }}
      >
        {match[2]}
      </span>,
    );
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < line.length) {
    parts.push(<span key={key++}>{line.slice(lastIndex)}</span>);
  }
  return parts;
};

const Cursor: React.FC<{ visible: boolean }> = ({ visible }) =>
  visible ? (
    <span
      style={{
        display: "inline-block",
        width: 10,
        height: 22,
        background: NOTHING.fg,
        marginLeft: 2,
        verticalAlign: "middle",
      }}
    />
  ) : null;

export const TerminalSimulator: React.FC<Props> = ({ command, response }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const promptDelay = 0.4;
  const typeDuration = Math.max(1.5, command.length * 0.04);
  const thinkingStart = promptDelay + typeDuration + 0.3;
  const thinkingDuration = 1.5;
  const systemLogStart = thinkingStart + thinkingDuration;
  const systemLogPerLine = 0.4;
  const systemLogDuration = response.systemLines.length * systemLogPerLine;
  const responseStart = systemLogStart + systemLogDuration + 0.4;
  const responsePerLine = 0.22;

  const typingProgress = Math.min(1, Math.max(0, (t - promptDelay) / typeDuration));
  const typedChars = Math.floor(typingProgress * command.length);
  const typedCommand = command.slice(0, typedChars);

  const isTyping = t > promptDelay && t < thinkingStart;
  const showThinking = t >= thinkingStart && t < systemLogStart;
  const thinkingDotsCount = (Math.floor((t - thinkingStart) * 3) % 4) + 1;

  const cursorBlink = Math.floor(t * 2) % 2 === 0;

  const systemLinesShown =
    t < systemLogStart
      ? 0
      : Math.min(
          response.systemLines.length,
          Math.floor((t - systemLogStart) / systemLogPerLine) + 1,
        );

  const responseLinesShown =
    t < responseStart
      ? 0
      : Math.min(
          response.responseLines.length,
          Math.floor((t - responseStart) / responsePerLine) + 1,
        );

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: NOTHING.bg,
        color: NOTHING.fg,
        fontFamily: FONTS.mono,
        fontSize: 20,
        lineHeight: 1.45,
        padding: "32px 40px",
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      {/* Prompt + command */}
      <div>
        <span style={{ color: NOTHING.dim, fontWeight: 600 }}>quantera</span>
        <span style={{ color: NOTHING.muted }}> · </span>
        <span style={{ color: NOTHING.muted }}>~ </span>
        <span style={{ color: NOTHING.red, marginRight: 8 }}>$</span>
        <span style={{ color: NOTHING.fg }}>{typedCommand}</span>
        <Cursor visible={t > promptDelay && (isTyping || cursorBlink)} />
      </div>

      {showThinking && (
        <div
          style={{
            color: NOTHING.muted,
            marginTop: 12,
            fontSize: 16,
            letterSpacing: 2,
          }}
        >
          [ {".".repeat(thinkingDotsCount).padEnd(4, " ")} ] PROCESSING
        </div>
      )}

      {systemLinesShown > 0 && (
        <div style={{ marginTop: 12 }}>
          {response.systemLines.slice(0, systemLinesShown).map((line, i) => (
            <div key={i} style={{ color: NOTHING.muted, fontSize: 15, letterSpacing: 0.3 }}>
              {line}
            </div>
          ))}
        </div>
      )}

      {responseLinesShown > 0 && (
        <div style={{ marginTop: 18 }}>
          {response.responseLines.slice(0, responseLinesShown).map((line, i) => (
            <div key={i} style={{ color: NOTHING.fg, minHeight: 28 }}>
              {renderLine(line)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
