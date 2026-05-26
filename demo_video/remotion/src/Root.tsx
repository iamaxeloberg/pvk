import { Composition } from "remotion";
import { QuanteraDemo } from "./QuanteraDemo";
import { FPS, getTotalDurationFrames } from "./queries";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="QuanteraDemo"
      component={QuanteraDemo}
      durationInFrames={getTotalDurationFrames()}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
