from typing import Any

class ReportGenerator:
    def generate_text_report(self, r: Any) -> str:
        lines = []
        lines.append(f"=== REPORT: {r.ticker} ===")
        lines.append(f"Date: {r.timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        lines.append(f"RATING: {r.recommendation} ({r.trade_type})")
        lines.append(f"Confidence: {r.confidence*100:.0f}%")
        lines.append(f"Rationale: {r.rationale}")
        lines.append("")

        lines.append("--- LEVELS ---")
        lines.append(f"Price: {r.price:.2f}")
        lines.append(f"Signal: {r.entry_signal}")
        if r.recommendation != "HOLD":
            lines.append(f"Stop:     {r.stop_loss:.2f} ({r.risk_reward:.1f}R)")
            lines.append(f"Target:   {r.target:.2f}")
            lines.append(f"Size:     {r.position_size_shares} shares ({r.position_size_pct*100:.1f}%)")
        lines.append("")

        lines.append("--- CONTEXT ---")
        regime = r.regime.value if hasattr(r.regime, 'value') else r.regime
        lines.append(f"Regime:    {regime}")
        lines.append(f"Trend:     {r.trend_strength}")
        lines.append(f"Patterns:  {', '.join(r.patterns) if r.patterns else 'None'}")
        lines.append(f"Volume:    {r.volume_status} ({r.volume_trend})")
        lines.append(f"Sentiment: {r.sentiment_summary} ({r.sentiment_score:.2f})")

        if r.backtest_win_rate:
            lines.append("")
            lines.append("--- HISTORY ---")
            lines.append(f"Win Rate: {r.backtest_win_rate*100:.0f}%")
            lines.append(f"Avg Move: {r.backtest_avg_move*100:.1f}%")

        return "\n".join(lines)
