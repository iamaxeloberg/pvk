#!/usr/bin/env bash
# Record all 8 VHS tapes against the live demo database.
#
# PREREQUISITES:
#   - FreeLLMAPI running on localhost:3001
#   - Demo data prepared (run `make demo-prep` from quantera/ first)
#   - VHS + ttyd installed (in ~/.local/bin)
#
# Usage:
#   cd quantera/demo_video && ./record_all.sh

set -e

export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verify FreeLLMAPI is up
if ! curl -s -m 3 http://localhost:3001/v1/models > /dev/null; then
    echo "ERROR: FreeLLMAPI not responding on localhost:3001"
    echo "Start it before running this script."
    exit 1
fi

# Verify demo data
if [ ! -f ../data/quantera.db ]; then
    echo "ERROR: Demo database not found. Run 'make demo-prep' from quantera/ first."
    exit 1
fi

mkdir -p recordings

TAPES=(
    "01_volvo_net_sales"
    "02_compare_margins"
    "03_kpi_ericsson"
    "04_portfolio_risks"
    "05_briefing_investor"
    "06_error_unknown_company"
    "07_error_missing_info"
    "08_free_cash_flow"
)

for tape in "${TAPES[@]}"; do
    echo "=== Recording $tape ==="
    vhs "tapes/${tape}.tape"
    echo ""
done

echo ""
echo "=== Done. Recordings saved to demo_video/recordings/ ==="
ls -lh recordings/
