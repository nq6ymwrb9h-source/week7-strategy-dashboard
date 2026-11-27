
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

DATA = Path(__file__).resolve().parent / "research_extensions"

PAGES = [
    "Turnover Optimization",
    "Capacity Analysis",
    "Joint Constraints",
    "Risk & Capital Utilization",
    "Model Validation"
]

COLORS = {
    "IC": "#2563eb",
    "IR": "#d97706",
    "EW_FINAL2": "#059669"
}

@st.cache_data
def load(name):
    return pd.read_csv(DATA / name)

def table(df, name):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=name,
        mime="text/csv",
        key="download_" + name
    )

def line(df, x, y, color, title,
         percent=False, dash=None):

    fig = px.line(
        df.sort_values(x),
        x=x,
        y=y,
        color=color,
        line_dash=dash,
        markers=True,
        title=title,
        color_discrete_map=COLORS
    )

    if percent:
        fig.update_yaxes(tickformat=".1%")

    fig.update_layout(
        template="plotly_white",
        height=450,
        legend_title_text=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

def strategy_filter(df, key):

    selected = st.multiselect(
        "Strategies",
        sorted(df["strategy"].unique()),
        default=sorted(df["strategy"].unique()),
        key=key
    )

    return df[df["strategy"].isin(selected)].copy()

def render(page):

    st.header(page)

    st.caption(
        "A-share historical research | "
        "2020-2024 | Not independent out-of-sample evidence"
    )

    if page == "Turnover Optimization":

        df = load("turnover.csv")

        c1, c2, c3 = st.columns(3)

        c1.metric("Experiments", len(df))
        c2.metric("Hard constraint cases", 15)
        c3.metric("Constraint violations", 0)

        view = strategy_filter(df, "turn_strategy")

        methods = st.multiselect(
            "Optimization methods",
            sorted(df["method"].unique()),
            default=sorted(df["method"].unique())
        )

        view = view[view["method"].isin(methods)]

        metric = st.selectbox(
            "Performance metric",
            [
                "ann_return",
                "sharpe",
                "max_drawdown",
                "fee_pct_initial"
            ]
        )

        if not view.empty:

            fig = px.scatter(
                view,
                x="annual_turnover",
                y=metric,
                color="strategy",
                symbol="method",
                hover_data=[
                    "parameter",
                    "max_holdings",
                    "avg_holdings"
                ],
                color_discrete_map=COLORS,
                title="Turnover-performance trade-off"
            )

            fig.update_xaxes(tickformat=".0%")

            if metric != "sharpe":
                fig.update_yaxes(tickformat=".1%")

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        hard = view[
            view["method"] == "Constraint"
        ]

        if not hard.empty:

            line(
                hard,
                "parameter",
                "ann_return",
                "strategy",
                "Hard turnover constraint sensitivity",
                True
            )

        st.info(
            "The 15 repaired hard-constraint cases "
            "strictly enforce 50 holdings. "
            "The other 30 cases use the original "
            "target-holdings mechanism."
        )

        table(view, "turnover_selection.csv")

    elif page == "Capacity Analysis":

        df = load("capacity.csv")

        c1, c2 = st.columns(2)

        c1.metric("Stress scenarios", len(df))
        c2.metric("Portfolio variants", 6)

        rate = st.select_slider(
            "ADV participation limit",
            options=[0.01, 0.03, 0.05, 0.10],
            value=0.05,
            format_func=lambda x: f"{x:.0%}"
        )

        view = strategy_filter(
            df, "capacity_strategy"
        )

        view = view[
            view["participation_limit"] == rate
        ].copy()

        view["capital_million"] = (
            view["capital"] / 1e6
        )

        line(
            view,
            "capital_million",
            "estimated_fill_ratio",
            "strategy",
            "Estimated executable amount",
            True,
            "variant"
        )

        line(
            view,
            "capital_million",
            "breach_fraction",
            "strategy",
            "Orders exceeding participation limit",
            True,
            "variant"
        )

        st.warning(
            "Historical order scaling only. "
            "Estimated executable amounts are not "
            "actual simulated fills or live capacity."
        )

        st.subheader("Conditional capacity thresholds")

        thresholds = load(
            "capacity_thresholds.csv"
        )

        st.dataframe(
            thresholds[
                thresholds["participation_limit"] == rate
            ],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Thresholds require estimated fill >=95%, "
            "breach <=5%, and ADV coverage >=95%. "
            "These are research assumptions."
        )

        table(view, "capacity_selection.csv")

    elif page == "Joint Constraints":

        df = load("joint.csv")

        c1, c2, c3 = st.columns(3)

        c1.metric("Backtests", len(df))
        c2.metric("Maximum holdings", 50)
        c3.metric("Validation passes", "36/36")

        rate = st.radio(
            "ADV participation limit",
            [0.05, 0.10],
            format_func=lambda x: f"{x:.0%}",
            horizontal=True,
            key="joint_rate"
        )

        view = strategy_filter(
            df, "joint_strategy"
        )

        view = view[
            view["participation_limit"] == rate
        ].copy()

        view["capital_million"] = (
            view["capital"] / 1e6
        )

        metrics = {
            "Annualized return": "ann_return",
            "Sharpe ratio": "sharpe",
            "Maximum drawdown": "max_drawdown",
            "Annualized turnover": "annual_turnover",
            "Average cash weight": "avg_cash_weight",
            "Target adjustment fulfillment":
                "execution_ratio"
        }

        label = st.selectbox(
            "Comparison metric",
            list(metrics)
        )

        metric = metrics[label]

        line(
            view,
            "capital_million",
            metric,
            "strategy",
            label,
            metric != "sharpe",
            "variant"
        )

        st.info(
            "Target adjustment fulfillment is executed "
            "amount divided by pre-constraint adjustment "
            "demand. It is not an order fill rate."
        )

        display = view.rename(columns={
            "execution_ratio":
                "target_adjustment_fulfillment"
        })

        table(display, "joint_selection.csv")

    elif page == "Risk & Capital Utilization":

        df = load("joint.csv")

        rate = st.radio(
            "ADV participation limit",
            [0.05, 0.10],
            format_func=lambda x: f"{x:.0%}",
            horizontal=True,
            key="risk_rate"
        )

        view = strategy_filter(
            df, "risk_strategy"
        )

        view = view[
            view["participation_limit"] == rate
        ].copy()

        view["capital_million"] = (
            view["capital"] / 1e6
        )

        line(
            view,
            "capital_million",
            "avg_cash_weight",
            "strategy",
            "Average cash allocation",
            True,
            "variant"
        )

        line(
            view,
            "capital_million",
            "max_drawdown",
            "strategy",
            "Maximum drawdown",
            True,
            "variant"
        )

        line(
            view,
            "capital_million",
            "sharpe",
            "strategy",
            "Risk-adjusted historical performance",
            False,
            "variant"
        )

        if (DATA / "market_risk.csv").exists():

            st.subheader("Market risk decomposition")

            risk = load("market_risk.csv")

            st.dataframe(
                risk,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Single-benchmark regression. "
                "Not full industry or multifactor attribution."
            )

        st.warning(
            "Cash allocation affects volatility and "
            "drawdown. Fixed slippage does not capture "
            "nonlinear market impact."
        )

    elif page == "Model Validation":

        turnover = load(
            "turnover_validation.csv"
        )

        joint = load("joint_validation.csv")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Turnover cases", "15/15")
        c2.metric("Joint cases", "36/36")
        c3.metric(
            "Audited stock-day orders",
            f"{joint['audited_orders'].sum():,}"
        )
        c4.metric(
            "Rebalance observations",
            f"{joint['regular_rebalances'].sum():,}"
        )

        st.subheader("Holding inflation repair")

        repair = load("repair_audit.csv")

        st.dataframe(
            repair,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Turnover constraint validation")

        st.dataframe(
            turnover,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Joint constraint validation")

        table(joint, "joint_validation.csv")

        st.subheader("ADV internal consistency")

        st.dataframe(
            load("adv_audit.csv"),
            hide_index=True
        )

        st.subheader("Empirical currency unit audit")

        st.dataframe(
            load("currency_audit.csv"),
            hide_index=True
        )

        st.subheader("Research limitations")

        st.markdown("""
- Historical parameter selection may introduce selection bias.
- Strict independent 2025 out-of-sample data are unavailable.
- Initial entry is exempt from turnover limits.
- Forced delisting trades are separately recorded.
- Adjusted prices and fixed slippage are simulation assumptions.
- Unfilled demand is reconsidered at the next rebalance.
- Validation covers specified constraints, not every possible model error.
""")
