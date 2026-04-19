"""AI Hedge Fund - Main entry point.

Orchestrates the AI-driven hedge fund pipeline:
  1. Fetch market data
  2. Run analyst agents
  3. Aggregate signals
  4. Generate portfolio decisions
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Hedge Fund — run analysis on a set of tickers."
    )
    parser.add_argument(
        "--tickers",
        type=str,
        required=True,
        help="Comma-separated list of stock tickers, e.g. AAPL,MSFT,GOOG",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=(datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d"),
        help="Start date for historical data (YYYY-MM-DD). Defaults to 90 days ago.",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=datetime.today().strftime("%Y-%m-%d"),
        help="End date for historical data (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--portfolio-cash",
        type=float,
        default=100_000.0,
        help="Starting cash available for the portfolio (USD). Default: 100,000.",
    )
    parser.add_argument(
        "--show-reasoning",
        action="store_true",
        help="Print each agent's reasoning to stdout.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Optional path to write the final decisions as JSON.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the AI hedge fund pipeline."""
    args = parse_args()

    tickers: list[str] = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if not tickers:
        print("Error: no valid tickers provided.", file=sys.stderr)
        sys.exit(1)

    print(f"[{datetime.now().isoformat()}] Starting AI Hedge Fund")
    print(f"  Tickers      : {', '.join(tickers)}")
    print(f"  Date range   : {args.start_date} → {args.end_date}")
    print(f"  Starting cash: ${args.portfolio_cash:,.2f}")
    print()

    # ---------------------------------------------------------------------------
    # Pipeline steps (modules imported lazily to keep startup fast)
    # ---------------------------------------------------------------------------
    from src.agents.orchestrator import run_hedge_fund  # noqa: PLC0415

    result = run_hedge_fund(
        tickers=tickers,
        start_date=args.start_date,
        end_date=args.end_date,
        portfolio_cash=args.portfolio_cash,
        show_reasoning=args.show_reasoning,
    )

    # ---------------------------------------------------------------------------
    # Output
    # ---------------------------------------------------------------------------
    print("\n=== Portfolio Decisions ===")
    for ticker, decision in result["decisions"].items():
        action = decision["action"].upper()
        qty = decision.get("quantity", 0)
        confidence = decision.get("confidence", 0.0)
        print(f"  {ticker:<8} {action:<6}  qty={qty:>6}  confidence={confidence:.1%}")

    if args.output_json:
        with open(args.output_json, "w") as fh:
            json.dump(result, fh, indent=2, default=str)
        print(f"\nResults written to {args.output_json}")


if __name__ == "__main__":
    main()
