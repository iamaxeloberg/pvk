// Authentic LLM-style responses derived from the actual demo data in
// quantera/data/markdown/. These mimic what the system would output when
// run against the live database — same numbers, same source data.

export type Response = {
  /** What the system logs while retrieving + routing */
  systemLines: string[];
  /** The actual answer body, with optional colour markup like {accent}text{/}  */
  responseLines: string[];
};

export const RESPONSES: Record<string, Response> = {
  "01_volvo_net_sales": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 1 relevant document",
      "[INFO] router: classified as 'general'",
      "[INFO] generator: generating response via claude...",
    ],
    responseLines: [
      "",
      "{accent}# Volvo Group — Q1 2025 Net Sales{/}",
      "",
      "Volvo Group reported {bold}Net Sales of SEK 132.4 billion{/} in Q1 2025,",
      "representing a {green}+8% increase year-over-year{/} compared to Q1 2024.",
      "",
      "This growth was driven by strong demand in the truck segment,",
      "with 55,400 truck deliveries (+6% YoY) despite a -4% decline in",
      "order intake reflecting softening market conditions.",
      "",
      "{muted}Source: volvo_group_report_csv.md{/}",
    ],
  },

  "02_compare_margins": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 2 relevant documents",
      "[INFO] router: classified as 'insight'",
      "[INFO] insight_agent: generating analysis via claude...",
    ],
    responseLines: [
      "",
      "{accent}# EBIT Margin Comparison — Q1 2025{/}",
      "",
      "{bold}Volvo Group:{/}     14.3% operating margin (+0.5pp YoY)",
      "{bold}Atlas Copco:{/}     22.1% EBIT margin     (+0.7pp YoY)",
      "",
      "Atlas Copco maintains a {green}~7.8 percentage point advantage{/} over",
      "Volvo Group, reflecting its higher-margin industrial equipment",
      "and compressor businesses versus Volvo's capital-intensive",
      "heavy truck segment.",
      "",
      "Both companies improved margins YoY, but Atlas Copco's larger",
      "absolute improvement (+0.7pp vs +0.5pp) suggests stronger",
      "pricing power in its core markets.",
      "",
      "{muted}Sources: volvo_group_report_csv.md, atlas_copco_report_csv.md{/}",
    ],
  },

  "03_kpi_ericsson": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 1 relevant document",
      "[INFO] router: classified as 'kpi'",
      "[INFO] kpi_agent: extracting metrics via claude...",
    ],
    responseLines: [
      "",
      "{accent}# KPI Report: Ericsson{/}",
      "{muted}Period: Q1 2025{/}",
      "",
      "- {bold}Net Sales:{/}        SEK 53.3B   {red}(-2% YoY){/}",
      "- {bold}Gross Margin:{/}     37.7%       {red}(-0.8pp){/}",
      "- {bold}EBIT:{/}             SEK 3.8B    {red}(-18% YoY){/}",
      "- {bold}EBIT Margin:{/}      7.1%        {red}(-1.4pp){/}",
      "- {bold}Net Income:{/}       SEK 2.4B    {red}(-25% YoY){/}",
      "- {bold}Free Cash Flow:{/}   SEK -1.2B   {red}(negative){/}",
      "- {bold}R&D Spending:{/}     SEK 10.8B   {green}(+3% YoY){/}",
      "- {bold}5G Contracts:{/}     142 signed  {green}(+8 vs Q1'24){/}",
      "- {bold}Employees:{/}        96,000      {red}(-4,000){/}",
      "",
      "{muted}9 metrics extracted and stored in kpi_store.{/}",
    ],
  },

  "04_portfolio_risks": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 4 relevant documents",
      "[INFO] router: classified as 'insight'",
      "[INFO] insight_agent: synthesising portfolio analysis...",
    ],
    responseLines: [
      "",
      "{accent}# Portfolio-Wide Risk Assessment — Q1 2025{/}",
      "",
      "{bold}Volvo Group — Cyclical exposure{/}",
      "  · North American heavy-duty truck market slowdown",
      "  · European emission regulation cost pressure",
      "  · Battery component supply chain disruption",
      "",
      "{bold}Ericsson — Top-line and margin pressure{/}",
      "  · Slower 5G rollout in India and Europe",
      "  · Intensifying competition from Huawei and Nokia",
      "  · Enterprise networking margin compression",
      "",
      "{bold}Atlas Copco — Macro and integration risk{/}",
      "  · Slowing industrial automation demand in China",
      "  · Currency headwinds from strong SEK vs USD",
      "  · Integration risk from recent compressor M&A",
      "",
      "{bold}Investor AB — Concentration and valuation{/}",
      "  · Heavy concentration in Swedish large-cap holdings",
      "  · PE valuation uncertainty in higher-rate environment",
      "  · Currency exposure on unhedged international assets",
      "",
      "{accent}Common themes:{/} all four portfolio companies cite",
      "currency exposure and demand-side cyclicality. Industrial",
      "names (Volvo, Atlas Copco) share supply-chain concerns.",
    ],
  },

  "05_briefing_investor": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 1 relevant document",
      "[INFO] router: classified as 'briefing'",
      "[INFO] briefing_agent: generating executive briefing...",
    ],
    responseLines: [
      "",
      "{accent}# Executive Briefing: Investor AB{/}",
      "{muted}Period: Q1 2025{/}",
      "",
      "{bold}Headline:{/} NAV grew 5% YoY to SEK 685B, supported by",
      "broad portfolio appreciation and disciplined capital allocation.",
      "",
      "{bold}Key Financials{/}",
      "  · NAV: SEK 685B (+5% YoY)",
      "  · NAV per Share: SEK 226.40 (+6%)",
      "  · Dividend Income: SEK 4.2B (+3%)",
      "  · Net Cash: SEK 28.5B",
      "",
      "{bold}Capital Activity{/}",
      "  · New investments: SEK 8.3B",
      "  · Divestments: SEK 3.1B",
      "  · Share buybacks: SEK 2.0B",
      "",
      "{bold}Outlook & Risks{/}",
      "  Strong balance sheet and net cash position give flexibility,",
      "  but concentration in Swedish large-cap names and PE valuation",
      "  uncertainty in the current rate environment warrant monitoring.",
      "",
      "{muted}Source: investor_ab_report_csv.md{/}",
    ],
  },

  "06_error_unknown_company": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[WARN] retriever: no documents matched 'Tesla'",
      "[INFO] retriever: retrieved 0 relevant documents",
    ],
    responseLines: [
      "",
      "{red}No relevant documents found for this query.{/}",
      "",
      "{muted}Indexed companies: Volvo Group, Ericsson,{/}",
      "{muted}Atlas Copco, Investor AB.{/}",
    ],
  },

  "07_error_missing_info": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 1 relevant document",
      "[INFO] router: classified as 'general'",
      "[INFO] generator: generating response via claude...",
    ],
    responseLines: [
      "",
      "{accent}# CEO Compensation — Volvo Group Q1 2025{/}",
      "",
      "{yellow}The provided document does not contain information about{/}",
      "{yellow}CEO compensation for Volvo Group in Q1 2025.{/}",
      "",
      "The Q1 2025 financial report covers operational and financial",
      "metrics (revenue, margins, cash flow, headcount, risk factors)",
      "but does not include executive compensation disclosures, which",
      "are typically published in the annual report and AGM materials.",
      "",
      "{muted}Source: volvo_group_report_csv.md{/}",
    ],
  },

  "08_free_cash_flow": {
    systemLines: [
      "[INFO] retriever: filtering index against query...",
      "[INFO] retriever: retrieved 1 relevant document",
      "[INFO] router: classified as 'kpi'",
      "[INFO] kpi_agent: extracting metric via claude...",
    ],
    responseLines: [
      "",
      "{accent}# KPI: Ericsson Free Cash Flow{/}",
      "{muted}Period: Q1 2025{/}",
      "",
      "{bold}Free Cash Flow:{/} {red}SEK -1.2 billion (negative){/}",
      "",
      "This represents a meaningful cash outflow for the quarter,",
      "driven by sustained R&D spending (SEK 10.8B, +3% YoY) and",
      "working capital pressure amid declining revenues.",
      "",
      "{yellow}Note:{/} A negative free cash flow in a quarter is a key",
      "signal that warrants follow-up — combined with the -25% net",
      "income decline, this points to operational headwinds requiring",
      "attention in subsequent quarters.",
      "",
      "{muted}Source: ericsson_report_csv.md{/}",
    ],
  },
};
