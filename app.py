import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(
    page_title="Marketing ROI Simulator",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Marketing Campaign ROI Simulator")
st.markdown("**Business experimentation platform for acquisition strategy optimization | A/B Testing + CLV Analysis**")
st.divider()

# Sidebar
st.sidebar.title("⚙️ Campaign Parameters")
page = st.sidebar.radio("Navigate", [
    "🎯 Campaign Designer",
    "🧪 A/B Test Analyzer",
    "💰 CLV Calculator",
    "📊 Sensitivity Analysis"
])

# ─── PAGE 1: CAMPAIGN DESIGNER ───
if page == "🎯 Campaign Designer":
    st.header("Campaign Designer")
    st.markdown("Design and simulate marketing campaigns to estimate ROI before spending a dollar.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📧 Campaign Setup")
        campaign_type = st.selectbox("Campaign Type", [
            "Credit Card Acquisition",
            "Loyalty Program Sign-up",
            "Premium Upgrade",
            "Winback Campaign"
        ])
        channel = st.selectbox("Channel", ["Email", "SMS", "Push Notification", "Direct Mail"])
        audience_size = st.number_input("Audience Size", 1000, 10000000, 100000, step=10000)

    with col2:
        st.subheader("💳 Offer Details")
        bonus_amount = st.slider("Sign-up Bonus ($)", 0, 500, 100)
        offer_duration = st.slider("Offer Duration (days)", 7, 90, 30)
        base_conversion_rate = st.slider("Base Conversion Rate (%)", 0.5, 15.0, 3.0, 0.1)

        # Bonus impact on conversion (higher bonus = higher conversion)
        bonus_lift = (bonus_amount / 100) * 0.8
        adjusted_conversion = min(base_conversion_rate + bonus_lift, 25.0)
        st.metric("Adjusted Conversion Rate", f"{adjusted_conversion:.2f}%",
                  delta=f"+{bonus_lift:.2f}% from bonus")

    with col3:
        st.subheader("💰 Economics")
        avg_revenue_per_customer = st.slider("Avg Annual Revenue/Customer ($)", 100, 2000, 500)
        customer_lifetime = st.slider("Expected Customer Lifetime (years)", 1, 10, 3)
        cost_per_contact = st.slider("Cost Per Contact ($)", 0.1, 10.0, 1.5, 0.1)

    st.divider()

    # Calculations
    conversions = int(audience_size * (adjusted_conversion / 100))
    total_bonus_cost = conversions * bonus_amount
    total_contact_cost = audience_size * cost_per_contact
    total_cost = total_bonus_cost + total_contact_cost
    total_revenue = conversions * avg_revenue_per_customer * customer_lifetime
    net_profit = total_revenue - total_cost
    roi = ((net_profit) / total_cost * 100) if total_cost > 0 else 0
    cac = total_cost / conversions if conversions > 0 else 0
    clv = avg_revenue_per_customer * customer_lifetime
    clv_cac_ratio = clv / cac if cac > 0 else 0

    # KPIs
    st.subheader("📊 Campaign Results")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Conversions", f"{conversions:,}")
    with col2:
        st.metric("Total Cost", f"${total_cost:,.0f}")
    with col3:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col4:
        st.metric("Net Profit", f"${net_profit:,.0f}",
                  delta=f"{'Profitable' if net_profit > 0 else 'Loss'}")
    with col5:
        st.metric("ROI", f"{roi:.1f}%")

    col1, col2 = st.columns(2)

    with col1:
        # Cost breakdown
        fig = go.Figure(data=[go.Pie(
            labels=['Bonus Cost', 'Contact Cost', 'Net Profit'],
            values=[total_bonus_cost, total_contact_cost, max(net_profit, 0)],
            hole=0.4,
            marker_colors=['#e74c3c', '#f39c12', '#2ecc71']
        )])
        fig.update_layout(title='Revenue Breakdown')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bonus amount vs ROI curve
        bonuses = list(range(0, 501, 25))
        rois = []
        for b in bonuses:
            b_lift = (b / 100) * 0.8
            b_conv = min(base_conversion_rate + b_lift, 25.0)
            b_conversions = int(audience_size * (b_conv / 100))
            b_cost = b_conversions * b + audience_size * cost_per_contact
            b_revenue = b_conversions * avg_revenue_per_customer * customer_lifetime
            b_roi = ((b_revenue - b_cost) / b_cost * 100) if b_cost > 0 else 0
            rois.append(b_roi)

        fig2 = px.line(x=bonuses, y=rois,
                       title='Bonus Amount vs ROI',
                       labels={'x': 'Bonus Amount ($)', 'y': 'ROI (%)'})
        fig2.add_vline(x=bonus_amount, line_dash="dash", line_color="red",
                       annotation_text=f"Current: ${bonus_amount}")
        fig2.add_hline(y=0, line_color="white", line_dash="dot")
        st.plotly_chart(fig2, use_container_width=True)

    # Summary table
    st.subheader("📋 Campaign Summary")
    summary = pd.DataFrame({
        'Metric': ['Audience Size', 'Conversion Rate', 'Conversions', 'Bonus Cost',
                   'Contact Cost', 'Total Cost', 'Total Revenue', 'Net Profit',
                   'ROI', 'CAC', 'CLV', 'CLV:CAC Ratio'],
        'Value': [f"{audience_size:,}", f"{adjusted_conversion:.2f}%", f"{conversions:,}",
                  f"${total_bonus_cost:,.0f}", f"${total_contact_cost:,.0f}",
                  f"${total_cost:,.0f}", f"${total_revenue:,.0f}", f"${net_profit:,.0f}",
                  f"{roi:.1f}%", f"${cac:.2f}", f"${clv:,.0f}", f"{clv_cac_ratio:.1f}x"]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ─── PAGE 2: A/B TEST ANALYZER ───
elif page == "🧪 A/B Test Analyzer":
    st.header("A/B Test Analyzer")
    st.markdown("Design statistically rigorous experiments and analyze results.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Test Design")
        baseline_rate = st.slider("Baseline Conversion Rate (%)", 0.5, 20.0, 3.0, 0.1)
        expected_lift = st.slider("Expected Lift (%)", 5.0, 100.0, 20.0, 1.0)
        significance = st.slider("Statistical Significance (%)", 80, 99, 95)
        power = st.slider("Statistical Power (%)", 70, 99, 80)

        # Sample size calculation
        alpha = 1 - significance/100
        beta = 1 - power/100
        p1 = baseline_rate / 100
        p2 = p1 * (1 + expected_lift/100)

        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(1 - beta)

        p_avg = (p1 + p2) / 2
        n = (z_alpha * np.sqrt(2 * p_avg * (1-p_avg)) +
             z_beta * np.sqrt(p1*(1-p1) + p2*(1-p2)))**2 / (p2-p1)**2

        n = int(np.ceil(n))

        st.metric("Required Sample Size (per group)", f"{n:,}")
        st.metric("Total Audience Needed", f"{n*2:,}")

    with col2:
        st.subheader("Test Results Analyzer")
        st.markdown("Input your actual test results:")

        control_visitors = st.number_input("Control Group Visitors", 100, 1000000, 10000)
        control_conversions = st.number_input("Control Conversions", 0, 100000, 300)
        treatment_visitors = st.number_input("Treatment Group Visitors", 100, 1000000, 10000)
        treatment_conversions = st.number_input("Treatment Conversions", 0, 100000, 380)

        control_rate = control_conversions / control_visitors
        treatment_rate = treatment_conversions / treatment_visitors
        lift = (treatment_rate - control_rate) / control_rate * 100

        # Statistical test
        _, p_value = stats.proportions_ztest(
            [treatment_conversions, control_conversions],
            [treatment_visitors, control_visitors]
        )

        is_significant = p_value < (1 - significance/100)

        st.divider()
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Control Rate", f"{control_rate*100:.2f}%")
        with col_b:
            st.metric("Treatment Rate", f"{treatment_rate*100:.2f}%",
                      delta=f"{lift:+.1f}% lift")
        with col_c:
            st.metric("P-Value", f"{p_value:.4f}")

        if is_significant:
            st.success(f"✅ STATISTICALLY SIGNIFICANT - Deploy the treatment! (p={p_value:.4f})")
        else:
            st.error(f"❌ NOT SIGNIFICANT - Need more data or the effect is too small (p={p_value:.4f})")

    # Conversion rate visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=['Control'], y=[control_rate*100],
                         marker_color='#e74c3c', text=f"{control_rate*100:.2f}%",
                         textposition='outside'))
    fig.add_trace(go.Bar(name='Treatment', x=['Treatment'], y=[treatment_rate*100],
                         marker_color='#2ecc71', text=f"{treatment_rate*100:.2f}%",
                         textposition='outside'))
    fig.update_layout(title='Control vs Treatment Conversion Rate',
                      yaxis_title='Conversion Rate (%)', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 3: CLV CALCULATOR ───
elif page == "💰 CLV Calculator":
    st.header("Customer Lifetime Value Calculator")
    st.markdown("Understand the true long-term value of acquired customers.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Parameters")
        avg_monthly_spend = st.slider("Avg Monthly Spend ($)", 10, 2000, 200)
        gross_margin = st.slider("Gross Margin (%)", 5, 80, 30)
        monthly_churn = st.slider("Monthly Churn Rate (%)", 0.5, 20.0, 2.0, 0.1)
        discount_rate = st.slider("Annual Discount Rate (%)", 5, 30, 10)

        # CLV calculation
        monthly_margin = avg_monthly_spend * (gross_margin/100)
        monthly_discount = discount_rate / 12 / 100
        clv = monthly_margin / (monthly_churn/100 + monthly_discount)
        avg_lifetime_months = 1 / (monthly_churn/100)

        st.divider()
        st.metric("Customer Lifetime Value", f"${clv:,.0f}")
        st.metric("Avg Customer Lifetime", f"{avg_lifetime_months:.0f} months ({avg_lifetime_months/12:.1f} years)")
        st.metric("Monthly Margin per Customer", f"${monthly_margin:.0f}")

    with col2:
        # CLV over time
        months = list(range(1, 61))
        survival_rates = [(1 - monthly_churn/100)**m for m in months]
        cumulative_clv = [monthly_margin * sum([(1-monthly_churn/100)**i /
                           (1+monthly_discount)**i for i in range(m)]) for m in months]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=cumulative_clv, fill='tozeroy',
                                  name='Cumulative CLV', line=dict(color='#2ecc71')))
        fig.update_layout(title='Cumulative CLV Over Time (60 months)',
                           xaxis_title='Months', yaxis_title='Cumulative CLV ($)')
        st.plotly_chart(fig, use_container_width=True)

    # Segment comparison
    st.subheader("Customer Segment Comparison")
    segments = {
        'Budget': {'spend': avg_monthly_spend * 0.5, 'churn': monthly_churn * 1.5},
        'Standard': {'spend': avg_monthly_spend, 'churn': monthly_churn},
        'Premium': {'spend': avg_monthly_spend * 2, 'churn': monthly_churn * 0.6},
        'VIP': {'spend': avg_monthly_spend * 4, 'churn': monthly_churn * 0.3},
    }

    seg_data = []
    for seg, params in segments.items():
        m = params['spend'] * (gross_margin/100)
        c = params['churn']/100
        v = m / (c + monthly_discount)
        seg_data.append({'Segment': seg, 'CLV': v, 'Monthly Spend': params['spend']})

    seg_df = pd.DataFrame(seg_data)
    fig2 = px.bar(seg_df, x='Segment', y='CLV', color='CLV',
                   color_continuous_scale='Greens', title='CLV by Customer Segment',
                   text=seg_df['CLV'].apply(lambda x: f'${x:,.0f}'))
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

# ─── PAGE 4: SENSITIVITY ANALYSIS ───
elif page == "📊 Sensitivity Analysis":
    st.header("Sensitivity Analysis")
    st.markdown("Understand which variables have the biggest impact on your ROI.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Base Case Parameters")
        base_audience = st.number_input("Audience Size", value=100000)
        base_conversion = st.slider("Base Conversion Rate (%)", 0.5, 15.0, 3.0)
        base_bonus = st.slider("Bonus Amount ($)", 0, 500, 100)
        base_revenue = st.slider("Revenue Per Customer ($)", 100, 5000, 500)
        base_lifetime = st.slider("Customer Lifetime (years)", 1, 10, 3)
        base_contact_cost = st.slider("Cost Per Contact ($)", 0.1, 10.0, 1.5)

    # Base ROI calculation
    def calculate_roi(audience, conversion, bonus, revenue, lifetime, contact_cost):
        conv_rate = min(conversion + (bonus/100)*0.8, 25) / 100
        conversions = int(audience * conv_rate)
        cost = conversions * bonus + audience * contact_cost
        rev = conversions * revenue * lifetime
        return ((rev - cost) / cost * 100) if cost > 0 else 0

    base_roi = calculate_roi(base_audience, base_conversion, base_bonus,
                              base_revenue, base_lifetime, base_contact_cost)

    with col2:
        st.subheader("Base Case Results")
        st.metric("Base ROI", f"{base_roi:.1f}%")

        # Tornado chart
        variables = {
            'Conversion Rate': (base_conversion*0.7, base_conversion*1.3),
            'Bonus Amount': (base_bonus*0.5, base_bonus*1.5),
            'Revenue/Customer': (base_revenue*0.7, base_revenue*1.3),
            'Customer Lifetime': (base_lifetime*0.7, base_lifetime*1.3),
            'Contact Cost': (base_contact_cost*1.3, base_contact_cost*0.7),
        }

        tornado_data = []
        for var, (low, high) in variables.items():
            params = [base_audience, base_conversion, base_bonus,
                      base_revenue, base_lifetime, base_contact_cost]
            idx = ['Audience', 'Conversion Rate', 'Bonus Amount',
                   'Revenue/Customer', 'Customer Lifetime', 'Contact Cost'].index(var) \
                if var != 'Contact Cost' else 5

            p_low = params.copy()
            p_high = params.copy()
            p_low[idx] = low
            p_high[idx] = high

            roi_low = calculate_roi(*p_low)
            roi_high = calculate_roi(*p_high)
            tornado_data.append({
                'Variable': var,
                'Low ROI': roi_low - base_roi,
                'High ROI': roi_high - base_roi,
                'Range': abs(roi_high - roi_low)
            })

        tornado_df = pd.DataFrame(tornado_data).sort_values('Range', ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=tornado_df['Variable'],
            x=tornado_df['Low ROI'],
            orientation='h',
            name='Downside',
            marker_color='#e74c3c'
        ))
        fig.add_trace(go.Bar(
            y=tornado_df['Variable'],
            x=tornado_df['High ROI'],
            orientation='h',
            name='Upside',
            marker_color='#2ecc71'
        ))
        fig.update_layout(
            title='Tornado Chart - ROI Sensitivity',
            xaxis_title='ROI Change from Base (%)',
            barmode='overlay'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Monte Carlo Simulation
    st.subheader("🎲 Monte Carlo Simulation")
    st.markdown("Simulate 10,000 possible outcomes based on uncertainty ranges.")

    n_simulations = 10000
    np.random.seed(42)

    sim_conversions = np.random.normal(base_conversion, base_conversion*0.15, n_simulations)
    sim_revenue = np.random.normal(base_revenue, base_revenue*0.2, n_simulations)
    sim_lifetime = np.random.normal(base_lifetime, base_lifetime*0.15, n_simulations)

    sim_rois = [calculate_roi(base_audience, max(c, 0.1), base_bonus,
                               max(r, 10), max(l, 0.5), base_contact_cost)
                for c, r, l in zip(sim_conversions, sim_revenue, sim_lifetime)]

    sim_rois = np.array(sim_rois)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean ROI", f"{sim_rois.mean():.1f}%")
    with col2:
        st.metric("P10 (Pessimistic)", f"{np.percentile(sim_rois, 10):.1f}%")
    with col3:
        st.metric("P90 (Optimistic)", f"{np.percentile(sim_rois, 90):.1f}%")
    with col4:
        prob_positive = (sim_rois > 0).mean() * 100
        st.metric("Probability Profitable", f"{prob_positive:.1f}%")

    fig = px.histogram(sim_rois, nbins=60,
                        title='Monte Carlo ROI Distribution (10,000 simulations)',
                        labels={'value': 'ROI (%)', 'count': 'Frequency'},
                        color_discrete_sequence=['#3498db'])
    fig.add_vline(x=0, line_color="red", line_dash="dash", annotation_text="Break-even")
    fig.add_vline(x=sim_rois.mean(), line_color="green", line_dash="dash",
                   annotation_text=f"Mean: {sim_rois.mean():.1f}%")
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    Built by Saif Ullah | A/B Testing + CLV + Monte Carlo Simulation | 
    <a href='https://github.com/saif06910'>GitHub</a>
</div>
""", unsafe_allow_html=True)