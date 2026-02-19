import sys
import os
sys.path.append(os.getcwd())

import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
from stock_tracker.api.interface import MarketAnalyzer, AnalysisReport

analyzer = MarketAnalyzer()

def create_layout():
    return html.Div([
        html.H1("stockCheck by joshmode"),

        html.Div([
            dcc.Input(id='ticker-input', value='AAPL', type='text', placeholder="Enter Ticker (e.g. NVDA)"),
            html.Button('Analyze', id='submit-button', n_clicks=0),
        ], style={'padding': '20px'}),

        html.Div(id='output-container', style={'padding': '20px', 'border': '1px solid #ddd', 'margin': '20px', 'borderRadius': '5px'}),
        dcc.Graph(id='price-chart'),
    ])

app = dash.Dash(__name__)
app.layout = create_layout()

def _create_report_html(report: AnalysisReport) -> html.Div:
    color = "black"
    if report.recommendation == "BUY":
        color = "green"
    elif report.recommendation == "SELL":
        color = "red"

    regime_val = report.regime
    if hasattr(report.regime, 'value'):
        regime_val = report.regime.value

    cond_map = {
        "RANGE": "Ranging (Sideways)",
        "BULL_TREND": "Bull Trend",
        "BEAR_TREND": "Bear Trend",
        "VOLATILE": "Volatile / Choppy",
        "TRANSITION": "Transitioning"
    }
    cond_str = cond_map.get(str(regime_val), str(regime_val))

    return html.Div([
        html.H2(f"{report.ticker}", style={'marginBottom': '10px'}),
        html.H3(f"Rating: {report.recommendation} ({report.trade_type})", style={'color': color}),
        html.P(f"Confidence: {report.confidence*100:.1f}%"),
        html.P(f"Range: {report.confidence_interval_low:.2f} - {report.confidence_interval_high:.2f}"),
        html.Hr(),
        html.Div([
            html.Span(f"Price: {report.price:.2f}", style={'fontWeight': 'bold', 'marginRight': '15px'}),
            html.Span(f"Target: {report.target:.2f}", style={'color': 'green', 'marginRight': '15px'}),
            html.Span(f"Stop: {report.stop_loss:.2f}", style={'color': 'red'}),
        ]),
        html.P(f"R/R: {report.risk_reward:.2f}"),
        html.Hr(),
        html.P(f"Condition: {cond_str}"),
        html.P(f"Trend: {report.trend_strength}"),
        html.P(f"Sentiment: {report.sentiment_summary} ({report.sentiment_score:.2f})"),
        html.P(f"Patterns: {', '.join(report.patterns) if report.patterns else 'None'}"),
        html.P(f"Volume: {report.volume_status} ({report.volume_trend})"),
        html.P(f"Rationale: {report.rationale}", style={'fontStyle': 'italic'}),
    ])

def _create_chart(report: AnalysisReport, ticker: str) -> go.Figure:
    candles = report.candles
    if not candles:
         return go.Figure()

    dates = [c.timestamp for c in candles]
    opens = [c.open for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    closes = [c.close for c in candles]

    fig = go.Figure(data=[go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, name="OHLC")])

    if report.swings:
        s_dates = [s.timestamp for s in report.swings]
        s_prices = [s.price for s in report.swings]
        fig.add_trace(go.Scatter(x=s_dates, y=s_prices, mode='lines+markers', name='Structure', line=dict(color='blue', width=1)))

    if report.target > 0:
        fig.add_hline(y=report.target, line_dash="dash", line_color="green", annotation_text="Target")
    if report.stop_loss > 0:
        fig.add_hline(y=report.stop_loss, line_dash="dash", line_color="red", annotation_text="Stop")

    if report.confidence_interval_high > 0:
        fig.add_hline(y=report.confidence_interval_high, line_dash="dot", line_color="gray", annotation_text="High CI")
    if report.confidence_interval_low > 0:
        fig.add_hline(y=report.confidence_interval_low, line_dash="dot", line_color="gray", annotation_text="Low CI")

    fig.update_layout(title=f"{ticker} Analysis", xaxis_rangeslider_visible=False, template="plotly_white", height=600)
    return fig

@callback(
    [Output('output-container', 'children'), Output('price-chart', 'figure')],
    Input('submit-button', 'n_clicks'),
    State('ticker-input', 'value'),
    prevent_initial_call=True
)
def update(n_clicks, ticker_input):
    if not ticker_input:
        return "Enter ticker.", go.Figure()

    ticker = ticker_input.upper()

    try:
        report = analyzer.analyze(ticker)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}", go.Figure()

    if not report:
        return f"No data for {ticker}.", go.Figure()

    return _create_report_html(report), _create_chart(report, ticker)

if __name__ == '__main__':
    print("Dashboard at http://127.0.0.1:8050/")
    app.run(debug=True, use_reloader=False)
