import streamlit as st
from groq import Groq
import PyPDF2
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="M&A Due Diligence Copilot", page_icon="🏦")
st.title("🏦 M&A Due Diligence Copilot")
st.caption("Professional M&A analysis with DCF, NPV & Scenario Analysis")

# ─── DEAL DETAILS ───────────────────────────────────────────
st.header("📋 Deal Details")
col1, col2, col3 = st.columns(3)
with col1:
    acquirer = st.text_input("Acquirer Company", placeholder="e.g. STK Pharma")
with col2:
    target = st.text_input("Target Company", placeholder="e.g. ABC Retail")
with col3:
    deal_size = st.text_input("Deal Size", placeholder="e.g. $500M")

col4, col5, col6 = st.columns(3)
with col4:
    acquirer_sector = st.selectbox("Acquirer Sector",
        ["Pharma","Financial Services","Automotive",
         "Technology","Retail","FMCG","Manufacturing","Other"])
with col5:
    target_sector = st.selectbox("Target Sector",
        ["Retail","Pharma","Financial Services","Automotive",
         "Technology","FMCG","Manufacturing","Other"])
with col6:
    projection_years = st.selectbox("DCF Projection Period",
        ["3 Years","5 Years","7 Years","10 Years"])

# ─── DCF INPUTS ─────────────────────────────────────────────
st.header("📊 DCF & Valuation Inputs")
st.caption("Fill these for accurate DCF, NPV and Scenario Analysis")
col7, col8, col9 = st.columns(3)
with col7:
    wacc = st.number_input("WACC / Discount Rate (%)",
           min_value=1.0, max_value=30.0, value=12.0, step=0.5)
    terminal_growth = st.number_input("Terminal Growth Rate (%)",
                      min_value=0.0, max_value=10.0, value=3.0, step=0.5)
with col8:
    target_revenue = st.number_input("Target Current Revenue ($M)",
                     min_value=0.0, value=100.0, step=10.0)
    target_ebitda_margin = st.number_input("Target EBITDA Margin (%)",
                           min_value=0.0, max_value=60.0,
                           value=15.0, step=1.0)
with col9:
    revenue_growth_base = st.number_input("Expected Revenue Growth % (Base)",
                          min_value=0.0, max_value=50.0,
                          value=10.0, step=1.0)
    capex_percent = st.number_input("Capex as % of Revenue",
                    min_value=0.0, max_value=30.0,
                    value=5.0, step=0.5)

col10, col11, col12 = st.columns(3)
with col10:
    tax_rate = st.number_input("Tax Rate (%)",
               min_value=0.0, max_value=50.0, value=25.0, step=1.0)
with col11:
    depreciation_percent = st.number_input("Depreciation as % of Revenue",
                           min_value=0.0, max_value=20.0,
                           value=3.0, step=0.5)
with col12:
    synergy_value = st.number_input("Expected Annual Synergies ($M)",
                    min_value=0.0, value=20.0, step=5.0)

# ─── ACQUIRER DOCUMENTS ─────────────────────────────────────
st.header("🏢 Acquirer Company Documents")
st.caption("Upload as many as you have — more docs = better analysis")
col13, col14 = st.columns(2)
with col13:
    acq_annual = st.file_uploader("Annual Report (PDF)",
                  type="pdf", key="acq_annual")
    acq_investor = st.file_uploader("Investor Presentation (PDF)",
                   type="pdf", key="acq_investor")
with col14:
    acq_credit = st.file_uploader("Credit Rating Report (PDF)",
                  type="pdf", key="acq_credit")
    acq_concall = st.file_uploader("Concall Transcript (PDF)",
                   type="pdf", key="acq_concall")

# ─── TARGET DOCUMENTS ───────────────────────────────────────
st.header("🎯 Target Company Documents")
col15, col16 = st.columns(2)
with col15:
    tgt_annual = st.file_uploader("Annual Report (PDF)",
                  type="pdf", key="tgt_annual")
    tgt_investor = st.file_uploader("Investor Presentation (PDF)",
                   type="pdf", key="tgt_investor")
with col16:
    tgt_credit = st.file_uploader("Credit Rating Report (PDF)",
                  type="pdf", key="tgt_credit")
    tgt_concall = st.file_uploader("Concall Transcript (PDF)",
                   type="pdf", key="tgt_concall")

# ─── INDUSTRY CONTEXT ───────────────────────────────────────
st.header("🌍 Industry Context")
col17, col18 = st.columns(2)
with col17:
    industry_report = st.file_uploader("Industry/Market Report (PDF)",
                       type="pdf", key="industry")
with col18:
    strategic_rationale = st.text_area(
        "Why is this acquisition being considered?",
        placeholder="e.g. STK Pharma wants retail distribution for OTC medicines...",
        height=120)

# ─── EXTRACT PDF ────────────────────────────────────────────
def extract_pdf_text(file, max_chars=3000):
    if file is None:
        return "Not provided"
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text[:max_chars]

# ─── DCF CALCULATION ────────────────────────────────────────
def calculate_dcf(revenue, ebitda_margin, growth_base, wacc,
                  terminal_growth, capex_pct, tax_rate,
                  depreciation_pct, years, synergies):

    wacc_r = wacc / 100
    tg_r = terminal_growth / 100
    tax_r = tax_rate / 100

    scenarios = {
        "Bull Case": growth_base * 1.3,
        "Base Case": growth_base,
        "Bear Case": growth_base * 0.6
    }

    results = {}
    for scenario, growth in scenarios.items():
        growth_r = growth / 100
        fcfs = []
        rev = revenue
        for yr in range(1, int(years) + 1):
            rev = rev * (1 + growth_r)
            ebitda = rev * (ebitda_margin / 100)
            ebit = ebitda - (rev * depreciation_pct / 100)
            nopat = ebit * (1 - tax_r)
            capex = rev * (capex_pct / 100)
            dep = rev * (depreciation_pct / 100)
            syn = synergies if yr >= 2 else synergies * 0.3
            fcf = nopat + dep - capex + syn
            fcfs.append(fcf)

        # Terminal value
        terminal_fcf = fcfs[-1] * (1 + tg_r)
        terminal_value = terminal_fcf / (wacc_r - tg_r)

        # Discount all cash flows
        pv_fcfs = []
        for i, fcf in enumerate(fcfs):
            pv = fcf / ((1 + wacc_r) ** (i + 1))
            pv_fcfs.append(pv)

        pv_terminal = terminal_value / ((1 + wacc_r) ** int(years))
        enterprise_value = sum(pv_fcfs) + pv_terminal

        results[scenario] = {
            "fcfs": [round(f, 1) for f in fcfs],
            "pv_fcfs": [round(p, 1) for p in pv_fcfs],
            "terminal_value": round(terminal_value, 1),
            "pv_terminal": round(pv_terminal, 1),
            "enterprise_value": round(enterprise_value, 1),
            "npv": round(enterprise_value - revenue * 2, 1),
            "growth_used": round(growth, 1)
        }
    return results

# ─── DISPLAY DCF RESULTS ────────────────────────────────────
def show_industry_benchmarks(sector):
    benchmarks = {
        "Pharma": {
            "wacc_range": "10% – 13%",
            "ebitda_multiple": "12x – 18x",
            "revenue_multiple": "3x – 5x",
            "good_irr": ">15%",
            "good_npv": "Positive + >20% of deal size",
            "terminal_growth": "3% – 5%",
            "typical_dcf_range": "$500M – $5000M for mid-size",
            "red_flag_ebitda": "Below 8x EBITDA multiple = distressed",
            "premium_paid": "20% – 40% over market price is normal",
            "notes": [
                "✅ Good deal: EBITDA multiple < 15x with synergies",
                "✅ Good deal: IRR > 15% in base case",
                "✅ Good deal: NPV positive even in bear case",
                "⚠️ Caution: Paying > 5x revenue without IP assets",
                "❌ Bad deal: EBITDA multiple > 20x for generic pharma",
                "❌ Bad deal: NPV negative in base case scenario"
            ]
        },
        "Retail": {
            "wacc_range": "9% – 12%",
            "ebitda_multiple": "6x – 12x",
            "revenue_multiple": "0.5x – 1.5x",
            "good_irr": ">12%",
            "good_npv": "Positive + >15% of deal size",
            "terminal_growth": "2% – 4%",
            "typical_dcf_range": "$100M – $2000M for mid-size",
            "red_flag_ebitda": "Below 5x EBITDA = serious distress",
            "premium_paid": "15% – 30% over market price is normal",
            "notes": [
                "✅ Good deal: EBITDA multiple < 10x with store synergies",
                "✅ Good deal: IRR > 12% in base case",
                "✅ Good deal: Strong same-store sales growth > 8%",
                "⚠️ Caution: High inventory + low margin business",
                "❌ Bad deal: EBITDA multiple > 14x for traditional retail",
                "❌ Bad deal: Declining footfall trend in target stores"
            ]
        },
        "Technology": {
            "wacc_range": "10% – 15%",
            "ebitda_multiple": "15x – 30x",
            "revenue_multiple": "4x – 10x",
            "good_irr": ">18%",
            "good_npv": "Positive + >25% of deal size",
            "terminal_growth": "4% – 6%",
            "typical_dcf_range": "$200M – $10000M",
            "red_flag_ebitda": "Negative EBITDA OK if high growth > 30%",
            "premium_paid": "30% – 60% over market price is normal",
            "notes": [
                "✅ Good deal: ARR growth > 25% YoY",
                "✅ Good deal: Net Revenue Retention > 110%",
                "✅ Good deal: Strong IP / patents / proprietary tech",
                "⚠️ Caution: High customer concentration (>30% one client)",
                "❌ Bad deal: Revenue multiple > 12x for slow-growth SaaS",
                "❌ Bad deal: High churn rate > 15% annually"
            ]
        },
        "Financial Services": {
            "wacc_range": "11% – 14%",
            "ebitda_multiple": "8x – 15x",
            "revenue_multiple": "2x – 4x",
            "good_irr": ">14%",
            "good_npv": "Positive + >18% of deal size",
            "terminal_growth": "3% – 5%",
            "typical_dcf_range": "$500M – $8000M",
            "red_flag_ebitda": "NPA ratio > 5% is serious red flag",
            "premium_paid": "20% – 45% over book value is normal",
            "notes": [
                "✅ Good deal: P/B ratio < 2x for banks",
                "✅ Good deal: NPA ratio < 2% — clean book",
                "✅ Good deal: CASA ratio > 40% — cheap funding",
                "⚠️ Caution: Hidden NPAs in restructured loans",
                "❌ Bad deal: P/B ratio > 4x without franchise value",
                "❌ Bad deal: NPA ratio > 5% — bad loan book"
            ]
        },
        "Automotive": {
            "wacc_range": "9% – 12%",
            "ebitda_multiple": "5x – 10x",
            "revenue_multiple": "0.5x – 1.2x",
            "good_irr": ">12%",
            "good_npv": "Positive + >15% of deal size",
            "terminal_growth": "2% – 4%",
            "typical_dcf_range": "$500M – $5000M",
            "red_flag_ebitda": "Below 4x EBITDA = serious distress",
            "premium_paid": "15% – 35% over market price is normal",
            "notes": [
                "✅ Good deal: EBITDA multiple < 8x with platform synergies",
                "✅ Good deal: EV/hybrid capability being acquired",
                "✅ Good deal: Strong dealer network in new geography",
                "⚠️ Caution: ICE-heavy portfolio in EV transition era",
                "❌ Bad deal: EBITDA multiple > 12x for ICE-only OEM",
                "❌ Bad deal: High pension liabilities + union obligations"
            ]
        },
        "FMCG": {
            "wacc_range": "9% – 11%",
            "ebitda_multiple": "12x – 20x",
            "revenue_multiple": "2x – 4x",
            "good_irr": ">14%",
            "good_npv": "Positive + >20% of deal size",
            "terminal_growth": "3% – 5%",
            "typical_dcf_range": "$300M – $5000M",
            "red_flag_ebitda": "Below 10x EBITDA = weak brand value",
            "premium_paid": "25% – 50% over market price is normal",
            "notes": [
                "✅ Good deal: Strong brand with pricing power",
                "✅ Good deal: Distribution reach in underpenetrated markets",
                "✅ Good deal: Gross margin > 40%",
                "⚠️ Caution: Private label threat from retailers",
                "❌ Bad deal: EBITDA multiple > 22x for regional brand",
                "❌ Bad deal: Declining market share 3 years in a row"
            ]
        },
        "Manufacturing": {
            "wacc_range": "10% – 13%",
            "ebitda_multiple": "5x – 9x",
            "revenue_multiple": "0.5x – 1.5x",
            "good_irr": ">13%",
            "good_npv": "Positive + >15% of deal size",
            "terminal_growth": "2% – 3%",
            "typical_dcf_range": "$100M – $2000M",
            "red_flag_ebitda": "Below 4x EBITDA = commoditized business",
            "premium_paid": "15% – 30% over market price is normal",
            "notes": [
                "✅ Good deal: Proprietary process or technology",
                "✅ Good deal: Long-term customer contracts > 3 years",
                "✅ Good deal: EBITDA multiple < 7x with cost synergies",
                "⚠️ Caution: High fixed cost + cyclical revenue",
                "❌ Bad deal: EBITDA multiple > 11x for commodity mfg",
                "❌ Bad deal: Aging plant needing heavy capex"
            ]
        },
        "Other": {
            "wacc_range": "10% – 14%",
            "ebitda_multiple": "7x – 15x",
            "revenue_multiple": "1x – 3x",
            "good_irr": ">14%",
            "good_npv": "Positive in base case",
            "terminal_growth": "3% – 4%",
            "typical_dcf_range": "Depends on sector",
            "red_flag_ebitda": "Below 5x EBITDA warrants deep scrutiny",
            "premium_paid": "20% – 40% over market price is typical",
            "notes": [
                "✅ Good deal: IRR > 14% in base case",
                "✅ Good deal: NPV positive even in bear case",
                "✅ Good deal: Clear strategic rationale beyond financials",
                "⚠️ Caution: Benchmark against closest sector peers",
                "❌ Bad deal: NPV negative in base case",
                "❌ Bad deal: Paying top-of-cycle multiples"
            ]
        }
    }

    data = benchmarks.get(sector, benchmarks["Other"])

    st.subheader(f"📚 Industry Benchmark — {sector} Sector")
    st.caption("Use these benchmarks to judge if your deal is good or bad")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Typical WACC Range", data["wacc_range"])
        st.metric("EBITDA Multiple Range", data["ebitda_multiple"])
        st.metric("Normal Acquisition Premium", data["premium_paid"])
    with col_b:
        st.metric("Revenue Multiple Range", data["revenue_multiple"])
        st.metric("Good IRR Benchmark", data["good_irr"])
        st.metric("Terminal Growth Rate", data["terminal_growth"])
    with col_c:
        st.metric("Good NPV Benchmark", data["good_npv"])
        st.metric("Typical DCF Range", data["typical_dcf_range"])
        st.metric("Red Flag Signal", data["red_flag_ebitda"])

    st.markdown("#### 🚦 Deal Quality Checklist")
    for note in data["notes"]:
        if note.startswith("✅"):
            st.success(note)
        elif note.startswith("⚠️"):
            st.warning(note)
        elif note.startswith("❌"):
            st.error(note)

def display_dcf_results(dcf_results, deal_size_str, years):
    st.subheader("📊 DCF Valuation & Scenario Analysis")

    try:
        deal_val = float(deal_size_str.replace("$","").replace("M","")
                        .replace("m","").replace(",","").strip())
    except:
        deal_val = None

    col_b, col_base, col_bear = st.columns(3)
    cols = [col_b, col_base, col_bear]
    colors = ["🟢", "🟡", "🔴"]

    for i, (scenario, data) in enumerate(dcf_results.items()):
        with cols[i]:
            st.metric(
                label=f"{colors[i]} {scenario}",
                value=f"${data['enterprise_value']}M",
                delta=f"NPV: ${data['npv']}M"
            )
            st.caption(f"Growth assumed: {data['growth_used']}%")
            if deal_val:
                premium = ((deal_val - data['enterprise_value'])
                          / data['enterprise_value'] * 100)
                if premium > 20:
                    st.error(f"Deal premium: {premium:.1f}% — Overpriced")
                elif premium > 0:
                    st.warning(f"Deal premium: {premium:.1f}% — Fair")
                else:
                    st.success(f"Discount: {abs(premium):.1f}% — Underpriced")

    # FCF Table
    st.subheader("📈 Free Cash Flow Projections ($M)")
    year_labels = [f"Year {i+1}" for i in range(int(years))]
    table_data = {"Year": year_labels}
    for scenario, data in dcf_results.items():
        table_data[scenario] = [f"${v}M" for v in data["fcfs"]]
    st.table(table_data)

    # Summary Table
    st.subheader("🏁 Valuation Summary")
    summary = {
        "Metric": ["Enterprise Value", "PV of Terminal Value", "NPV of Deal"],
    }
    for scenario, data in dcf_results.items():
        summary[scenario] = [
            f"${data['enterprise_value']}M",
            f"${data['pv_terminal']}M",
            f"${data['npv']}M"
        ]
    st.table(summary)

# ─── AI ANALYSIS ────────────────────────────────────────────
def run_analysis(docs, acquirer, target, deal_size,
                 acquirer_sector, target_sector,
                 rationale, dcf_results, wacc,
                 terminal_growth, years):

    bull = dcf_results["Bull Case"]
    base = dcf_results["Base Case"]
    bear = dcf_results["Bear Case"]

    prompt = f"""
You are a Managing Director at McKinsey M&A practice.
Analyze ALL documents and give a complete due diligence report.

═══════════════════════════════════
DEAL OVERVIEW
═══════════════════════════════════
Acquirer: {acquirer} | Sector: {acquirer_sector}
Target: {target} | Sector: {target_sector}
Deal Size: {deal_size}
Strategic Rationale: {rationale}

═══════════════════════════════════
DCF & SCENARIO ANALYSIS RESULTS
═══════════════════════════════════
Projection Period: {years} Years
WACC Used: {wacc}%
Terminal Growth Rate: {terminal_growth}%

Bull Case Enterprise Value: ${bull['enterprise_value']}M
  FCFs: {bull['fcfs']} | NPV: ${bull['npv']}M

Base Case Enterprise Value: ${base['enterprise_value']}M
  FCFs: {base['fcfs']} | NPV: ${base['npv']}M

Bear Case Enterprise Value: ${bear['enterprise_value']}M
  FCFs: {bear['fcfs']} | NPV: ${bear['npv']}M

═══════════════════════════════════
ACQUIRER DOCUMENTS
═══════════════════════════════════
Annual Report: {docs['acq_annual']}
Investor Presentation: {docs['acq_investor']}
Credit Rating: {docs['acq_credit']}
Concall: {docs['acq_concall']}

═══════════════════════════════════
TARGET DOCUMENTS
═══════════════════════════════════
Annual Report: {docs['tgt_annual']}
Investor Presentation: {docs['tgt_investor']}
Credit Rating: {docs['tgt_credit']}
Concall: {docs['tgt_concall']}

═══════════════════════════════════
INDUSTRY CONTEXT
═══════════════════════════════════
{docs['industry']}

═══════════════════════════════════
PROVIDE ANALYSIS IN THESE SECTIONS
═══════════════════════════════════

1. EXECUTIVE SUMMARY
   - Deal thesis in 2 lines
   - Top 3 reasons to proceed
   - Top 3 reasons to be cautious
   - Upfront recommendation

2. ACQUIRER PROFILE
   - Revenue trend (last 3 years)
   - EBITDA & net profit margins
   - Cash & debt position
   - Free cash flow strength
   - Strategic gaps this deal fills

3. TARGET PROFILE
   - Revenue trend (last 3 years)
   - EBITDA & net profit margins
   - Cash & debt position
   - Market share & moat
   - Key assets being acquired

4. CROSS-SECTOR STRATEGIC FIT
   Acquirer: {acquirer_sector} | Target: {target_sector}
   - Related or unrelated diversification?
   - Specific capability transferred
   - Distribution/channel synergies
   - Customer base overlap or new access
   - Strategic fit rating: Strong/Moderate/Weak + why

5. REVENUE SYNERGIES (with $ estimates)
   For each: What | How | $ Value | Timeline
   - Synergy 1
   - Synergy 2
   - Synergy 3
   - Total revenue synergy potential

6. COST SYNERGIES (with $ estimates)
   For each: What | How | $ Value | Timeline
   - Synergy 1
   - Synergy 2
   - Synergy 3
   - Total cost synergy potential

7. DEEP FINANCIAL ANALYSIS

   A) DCF INTERPRETATION
   - Interpret Bull/Base/Bear case results above
   - What assumptions drive each scenario
   - Which scenario is most likely and why
   - Key sensitivities in the DCF model

   B) NPV ANALYSIS
   - Is NPV positive in base case?
   - At what growth rate does NPV turn negative?
   - NPV breakeven analysis
   - Value at risk if bear case materializes

   C) SCENARIO ANALYSIS
   - Bull Case: What needs to go right
   - Base Case: Most likely outcome
   - Bear Case: Key downside risks
   - Probability weight each scenario

   D) VALUATION MULTIPLES
   - Revenue multiple implied by deal
   - EBITDA multiple vs sector average
   - P/E multiple comparison
   - Is deal overpriced/fair/underpriced?

   E) DEAL FUNDING ANALYSIS
   - Can acquirer fund this deal?
   - Recommended debt/equity mix
   - Post-deal leverage ratio
   - Impact on acquirer credit rating

   F) RETURNS ANALYSIS
   - Expected IRR
   - Payback period
   - EPS accretion/dilution Year 1 and Year 3
   - Break-even synergy required

   G) FINANCIAL RED FLAGS
   - Revenue concentration risk
   - Working capital issues
   - Off-balance sheet liabilities
   - Related party transactions
   - Contingent liabilities

8. INTEGRATION RISK
   - Culture clash risk (cross-sector deal)
   - Technology integration complexity
   - Talent retention risk
   - Customer churn during integration
   - Regulatory approvals needed
   - Integration timeline: X months

9. RISK MATRIX
   Format: Risk | Probability | Impact | Mitigation
   - Regulatory risk
   - Integration risk
   - Synergy realization risk
   - Market risk
   - Management departure risk

10. DEAL RECOMMENDATION
    Verdict: PROCEED / CONDITIONS / DO NOT PROCEED

    Price Negotiation Range based on DCF:
    - Floor price (bear case): $X
    - Fair price (base case): $X
    - Maximum to pay (bull case): $X

    If Proceed:
    - Deal structure recommended
    - Key conditions to include
    - First 100 days plan

    If Do Not Proceed:
    - Key dealbreakers
    - Alternative strategies
    - Better targets to consider

Use actual numbers from documents.
State assumptions clearly where data is missing.
Write for a Fortune 500 board presentation.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000
    )
    return response.choices[0].message.content

# ─── RUN BUTTON ─────────────────────────────────────────────
if st.button("🔍 Run Complete M&A Due Diligence", type="primary"):
    if not acquirer or not target:
        st.warning("⚠️ Please enter both company names.")
    elif not acq_annual and not tgt_annual:
        st.warning("⚠️ Upload at least one annual report.")
    else:
        years_int = int(projection_years.split()[0])

        # Calculate DCF first
        dcf_results = calculate_dcf(
            revenue=target_revenue,
            ebitda_margin=target_ebitda_margin,
            growth_base=revenue_growth_base,
            wacc=wacc,
            terminal_growth=terminal_growth,
            capex_pct=capex_percent,
            tax_rate=tax_rate,
            depreciation_pct=depreciation_percent,
            years=years_int,
            synergies=synergy_value
        )

        # Show DCF results immediately
        display_dcf_results(dcf_results, deal_size, years_int)

        # Then run AI analysis
        docs = {
            "acq_annual": extract_pdf_text(acq_annual),
            "acq_investor": extract_pdf_text(acq_investor),
            "acq_credit": extract_pdf_text(acq_credit),
            "acq_concall": extract_pdf_text(acq_concall),
            "tgt_annual": extract_pdf_text(tgt_annual),
            "tgt_investor": extract_pdf_text(tgt_investor),
            "tgt_credit": extract_pdf_text(tgt_credit),
            "tgt_concall": extract_pdf_text(tgt_concall),
            "industry": extract_pdf_text(industry_report),
        }

        with st.spinner("Running full AI analysis... 40-60 seconds ⏳"):
            result = run_analysis(
                docs, acquirer, target, deal_size,
                acquirer_sector, target_sector,
                strategic_rationale, dcf_results,
                wacc, terminal_growth, projection_years
            )

        st.success("✅ Complete M&A Due Diligence Done!")
        st.markdown("---")
        st.markdown(result)
        st.download_button(
            "📥 Download Full DD Report", result,
            file_name=f"DD_{acquirer}_acquires_{target}.txt",
            mime="text/plain")