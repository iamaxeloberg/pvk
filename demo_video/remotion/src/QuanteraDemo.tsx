import { Sequence } from "remotion";
import { Intro } from "./components/Intro";
import { Outro } from "./components/Outro";
import { LabelCard } from "./components/LabelCard";
import { ClipFrame } from "./components/ClipFrame";
import { Soundtrack } from "./components/Soundtrack";
import {
  QUERIES,
  FPS,
  INTRO_DURATION_SECONDS,
  OUTRO_DURATION_SECONDS,
  LABEL_CARD_DURATION_SECONDS,
  CLIP_OUTRO_DURATION_SECONDS,
  getQueryTotalDurationFrames,
} from "./queries";

export const QuanteraDemo: React.FC = () => {
  const introFrames = Math.round(INTRO_DURATION_SECONDS * FPS);
  const outroFrames = Math.round(OUTRO_DURATION_SECONDS * FPS);
  const labelFrames = Math.round(LABEL_CARD_DURATION_SECONDS * FPS);
  const clipOutroFrames = Math.round(CLIP_OUTRO_DURATION_SECONDS * FPS);

  let cursor = introFrames;

  const querySequences = QUERIES.map((query, index) => {
    const totalFrames = getQueryTotalDurationFrames(query);
    const clipFrames = totalFrames - labelFrames - clipOutroFrames;
    const labelStart = cursor;
    const clipStart = cursor + labelFrames;

    cursor += totalFrames;

    return (
      <>
        <Sequence
          key={`${query.id}-label`}
          from={labelStart}
          durationInFrames={labelFrames}
        >
          <LabelCard query={query} queryIndex={index} totalQueries={QUERIES.length} />
        </Sequence>
        <Sequence
          key={`${query.id}-clip`}
          from={clipStart}
          durationInFrames={clipFrames + clipOutroFrames}
        >
          <ClipFrame query={query} queryIndex={index} totalQueries={QUERIES.length} />
        </Sequence>
      </>
    );
  });

  return (
    <>
      <Soundtrack />
      <Sequence from={0} durationInFrames={introFrames}>
        <Intro />
      </Sequence>
      {querySequences}
      <Sequence from={cursor} durationInFrames={outroFrames}>
        <Outro />
      </Sequence>
    </>
  );
};
