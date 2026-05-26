export type QueryCategory = "STRENGTH" | "ROBUSTNESS";

export type Query = {
  id: string;
  category: QueryCategory;
  label: string;
  description: string;
  command: string;
  clipFile: string;
  clipDurationSeconds: number;
};

export const QUERIES: Query[] = [
  {
    id: "01_volvo_net_sales",
    category: "STRENGTH",
    label: "Precise data lookup",
    description: "Retrieves a specific metric from a single document",
    command: 'make query Q="What is the Q1 2025 net sales of Volvo Group?"',
    clipFile: "01_volvo_net_sales.mp4",
    clipDurationSeconds: 14,
  },
  {
    id: "02_compare_margins",
    category: "STRENGTH",
    label: "Multi-document comparison",
    description: "Pulls data from two reports and generates analysis",
    command:
      'make query Q="Compare the EBIT margin of Volvo Group and Atlas Copco in Q1 2025"',
    clipFile: "02_compare_margins.mp4",
    clipDurationSeconds: 18,
  },
  {
    id: "03_kpi_ericsson",
    category: "STRENGTH",
    label: "Structured KPI extraction",
    description: "Specialised agent returns metrics in a clean format",
    command: 'make query Q="Extract all key financial metrics for Ericsson in Q1 2025"',
    clipFile: "03_kpi_ericsson.mp4",
    clipDurationSeconds: 18,
  },
  {
    id: "04_portfolio_risks",
    category: "STRENGTH",
    label: "Portfolio-wide aggregation",
    description: "Synthesises risks across all 4 portfolio companies",
    command:
      'make query Q="What are the main financial risks across our portfolio based on the latest reports?"',
    clipFile: "04_portfolio_risks.mp4",
    clipDurationSeconds: 22,
  },
  {
    id: "05_briefing_investor",
    category: "STRENGTH",
    label: "Executive briefing",
    description: "Routes to the briefing agent for summary output",
    command: 'make query Q="Give me an executive briefing on Investor AB"',
    clipFile: "05_briefing_investor.mp4",
    clipDurationSeconds: 20,
  },
  {
    id: "06_error_unknown_company",
    category: "ROBUSTNESS",
    label: "Out-of-scope query",
    description: "Returns no results for companies outside the portfolio",
    command: 'make query Q="What is the Q1 2025 revenue of Tesla?"',
    clipFile: "06_error_unknown_company.mp4",
    clipDurationSeconds: 10,
  },
  {
    id: "07_error_missing_info",
    category: "ROBUSTNESS",
    label: "Missing information",
    description: "Refuses to hallucinate when data isn't in the source",
    command:
      'make query Q="What is the CEO compensation of Volvo Group in Q1 2025?"',
    clipFile: "07_error_missing_info.mp4",
    clipDurationSeconds: 14,
  },
  {
    id: "08_free_cash_flow",
    category: "STRENGTH",
    label: "Surfaces critical details",
    description: "Highlights a negative cash flow that's easy to miss manually",
    command: 'make query Q="What is the Q1 2025 free cash flow of Ericsson?"',
    clipFile: "08_free_cash_flow.mp4",
    clipDurationSeconds: 14,
  },
];

export const FPS = 30;
export const LABEL_CARD_DURATION_SECONDS = 3;
export const CLIP_OUTRO_DURATION_SECONDS = 1.5;
export const INTRO_DURATION_SECONDS = 5;
export const OUTRO_DURATION_SECONDS = 5;

export const getQueryTotalDurationFrames = (q: Query): number =>
  Math.round(
    (LABEL_CARD_DURATION_SECONDS + q.clipDurationSeconds + CLIP_OUTRO_DURATION_SECONDS) *
      FPS,
  );

export const getTotalDurationFrames = (): number => {
  const queryFrames = QUERIES.reduce((sum, q) => sum + getQueryTotalDurationFrames(q), 0);
  return Math.round((INTRO_DURATION_SECONDS + OUTRO_DURATION_SECONDS) * FPS) + queryFrames;
};
