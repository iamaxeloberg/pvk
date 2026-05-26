import { Audio, getStaticFiles, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Looks for `public/soundtrack.mp3` (or .wav/.m4a/.ogg) and plays it under
 * the entire composition with a short fade-out at the end. If no file is
 * present, renders nothing — the video still produces fine, just without audio.
 *
 * To swap the track: replace `public/soundtrack.mp3` and re-render.
 */
export const Soundtrack: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  const candidates = ["soundtrack.mp3", "soundtrack.wav", "soundtrack.m4a", "soundtrack.ogg"];
  const staticFiles = getStaticFiles();

  const match = candidates.find((name) =>
    staticFiles.some((f) => f.src.endsWith(`/${name}`)),
  );

  if (!match) return null;

  const fadeOutFrames = fps * 2;
  const fadeOutVolume = interpolate(
    frame,
    [durationInFrames - fadeOutFrames, durationInFrames],
    [0.55, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const fadeInVolume = interpolate(frame, [0, fps], [0, 0.55], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const volume = Math.min(fadeInVolume, fadeOutVolume);

  return <Audio src={staticFile(match)} volume={volume} loop />;
};
