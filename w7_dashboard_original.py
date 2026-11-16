from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reports/week7"
FIG = OUT / "figures"

st.set_page_config(
    page_title="W7 Quant Strategy Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("W7 | 多因子组合策略研究")
st.caption("2019–2024 A股量化研究 · 动态加权 · 风险与交易成本分析")

df = pd.read_csv(OUT / "week7_strategy_comparison.csv")
df = df.set_index("strategy")

labels = {
    "EW_11": "11因子等权",
    "IC_11": "11因子IC加权",
    "IR_11": "11因子IR加权",
    "EW_2": "2因子等权"
}

st.subheader("一、核心绩效指标")

cols = st.columns(4)

for col, key in zip(cols, labels):
    if key in df.index:
        row = df.loc[key]
        with col:
            st.metric(
                labels[key],
                f"{row['ann_return']:.2%}",
                f"Sharpe {row['sharpe']:.3f}",
                delta_color="off"
            )

st.subheader("二、策略绩效对比")

show = df.reset_index().copy()
show["strategy"] = show["strategy"].map(labels)
show["ann_return"] *= 100
show["ann_vol"] *= 100

st.dataframe(
    show.rename(columns={
        "strategy": "策略",
        "ann_return": "年化收益 (%)",
        "ann_vol": "年化波动率 (%)",
        "sharpe": "夏普比率",
        "ann_turnover": "年换手 (倍)"
    }),
    use_container_width=True,
    hide_index=True
)

st.subheader("三、收益与风险可视化")

for name in [
    "w7_annual_return.png",
    "w7_risk_turnover.png",
    "w7_max_drawdown.png"
]:
    p = FIG / name
    if p.exists():
        st.image(str(p), use_container_width=True)

st.subheader("四、交易成本敏感性")

p = OUT / "week7_cost_sensitivity.csv"
if p.exists():
    st.dataframe(
        pd.read_csv(p),
        use_container_width=True,
        hide_index=True
    )

p = FIG / "w7_cost_sensitivity.png"
if p.exists():
    st.image(str(p), use_container_width=True)

st.subheader("五、年度稳健性")

p = FIG / "w7_yearly_returns.png"
if p.exists():
    st.image(str(p), use_container_width=True)

p = OUT / "week7_yearly_comparison.csv"
if p.exists():
    st.dataframe(
        pd.read_csv(p),
        use_container_width=True,
        hide_index=True
    )

st.subheader("六、研究结论")

st.markdown("""
- 11因子滚动IC加权优于11因子简单等权。
- 双因子策略在本次历史回测中表现最好。
- 多因子数量增加不保证组合收益提高。
- 交易成本和换手率对动态策略有明显影响。
- 本研究属于历史回测，尚不能视为独立样本外验证。
""")

st.caption("Research Dashboard | Week 7")
