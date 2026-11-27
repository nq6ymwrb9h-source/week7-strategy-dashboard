from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'reports'/'week7'
FIG=OUT/'figures'
st.set_page_config(page_title='W7 | Multi-Factor Strategy Research',page_icon='📊',layout='wide')
st.title('Week 7 | Multi-Factor Strategy Research')
st.caption('Independent A-share research dashboard · 2020–2024 backtest NAV period · Historical results only')

@st.cache_data
def load_csv(name):
    p=OUT/name
    return pd.read_csv(p) if p.is_file() else None

def show_image(name,caption):
    p=FIG/name
    if p.is_file():
        st.image(str(p),caption=caption,use_container_width=True)
    else: st.warning(f'Missing figure: {name}')

nav=st.sidebar.radio('Research sections',['Overview', 'Strategy Comparison', 'Risk & Drawdown', 'Transaction Costs', 'Yearly Performance', 'Methods & Limitations', 'Turnover Optimization', 'Capacity Analysis', 'Joint Constraints', 'Risk & Capital Utilization', 'Model Validation'])

import w7_research_extensions as extensions
if nav in extensions.PAGES:
    extensions.render(nav)
    st.stop()

st.sidebar.caption('W7 only · independent deployment')
perf=load_csv('week7_strategy_comparison.csv')
labels={'EW_11':'11-factor Equal Weight','IC_11':'11-factor Rolling IC','IR_11':'11-factor Rolling ICIR','EW_2':'2-factor Equal Weight'}
if nav=='Overview':
    st.subheader('Four portfolio strategies')
    if perf is None:st.error('Missing week7_strategy_comparison.csv')
    else:
        cols=st.columns(4)
        for col,(code,label) in zip(cols,labels.items()):
            rows=perf.loc[perf['strategy']==code]
            if not rows.empty:
                r=rows.iloc[0]
                col.metric(label,f"{float(r['ann_return']):.2%}",f"Sharpe {float(r['sharpe']):.3f}",delta_color='off')
        show_image('w7_annual_return.png','Annualized return comparison')
    st.info('The two-factor baseline led this historical test. This is not evidence of future superiority; the baseline was selected after observing results.')
elif nav=='Strategy Comparison':
    st.subheader('Portfolio performance')
    if perf is not None:
        view=perf.copy()
        view['strategy']=view['strategy'].map(labels).fillna(view['strategy'])
        st.dataframe(view,use_container_width=True,hide_index=True)
        if {'strategy','ann_return'}.issubset(view):
            fig=px.bar(view,x='strategy',y='ann_return',color='strategy',title='Annualized returns',labels={'ann_return':'Annual return','strategy':'Strategy'})
            fig.update_layout(showlegend=False,yaxis_tickformat='.0%')
            st.plotly_chart(fig,use_container_width=True)
    show_image('w7_annual_return.png','Comparison from original W7 research')
elif nav=='Risk & Drawdown':
    st.subheader('Risk and turnover')
    show_image('w7_risk_turnover.png','Volatility, Sharpe and turnover')
    show_image('w7_max_drawdown.png','Maximum drawdown')
elif nav=='Transaction Costs':
    st.subheader('Transaction cost sensitivity')
    show_image('w7_cost_sensitivity.png','Gross, main and high-cost assumptions')
    costs=load_csv('week7_cost_sensitivity.csv')
    if costs is not None:st.dataframe(costs,use_container_width=True,hide_index=True)
elif nav=='Yearly Performance':
    st.subheader('Annual performance')
    show_image('w7_yearly_returns.png','Annual returns by strategy')
    yearly=load_csv('week7_yearly_comparison.csv')
    if yearly is not None:st.dataframe(yearly,use_container_width=True,hide_index=True)
    st.caption('Yearly comparison covers the strategies present in the original W7 yearly files. The 11-factor EW annual series may not be included.')
else:
    st.subheader('Methodology and limitations')
    st.markdown('''**Research design.** W7 compared equal-weight, rolling IC-weighted and rolling ICIR-weighted scores on 11 price/volume factors, plus a two-factor equal-weight baseline. Holdings target: 50 stocks.\n\n**Time period.** Rolling rebalances begin in 2019; portfolio NAV performance used in the comparisons begins in 2020. Exact dates and assumptions should be verified against the underlying reports.\n\n**Data coverage.** EP, BP and CFP were excluded from the W7 dynamic tests because their source matrices had sparse coverage.\n\n**Execution and cost risk.** Realized fills, suspensions, price limits, transaction costs and capacity require separate validation.\n\n**Statistical limitations.** Strict point-in-time correctness and absence of look-ahead have not been independently audited. Factor selection and the two-factor baseline introduce selection bias. Results are historical research, not investment advice.\n\n**Reconciliation.** The W7 backtest summary reported passing engine reconciliation within the chosen tolerance, but that does not establish external validity.''')
