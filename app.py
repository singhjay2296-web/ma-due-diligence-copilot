import streamlit as st
from groq import Groq
import PyPDF2
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Jay Manral's M&A Due Diligence Copilot", page_icon="🏦")

# ─── HEADER ─────────────────────────────────────────────────
st.title("🏦 Jay Manral's M&A Due Diligence Copilot")
st.caption("Professional M&A analysis with DCF, NPV, Scenario & Sensitivity Analysis")
st.markdown("**Built by Jay Manral | Strategy Consultant | IBM Consulting | MBA, IIT Bombay**")
st.markdown("---")

# ─── FIX METRIC FONT TRUNCATION ─────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 1rem !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.3 !important;
}
[data-testid="stMetricLabel"] {
    white-space: normal !important;
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE INIT ──────────────────────────────────────
if 'analysis_done' not in st.session_state:
    st.session_state['analysis_done'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = ""
if 'last_acquirer' not in st.session_state:
    st.session_state['last_acquirer'] = ""
if 'last_target' not in st.session_state:
    st.session_state['last_target'] = ""
if 'dcf_results' not in st.session_state:
    st.session_state['dcf_results'] = None
if 'sens_results' not in st.session_state:
    st.session_state['sens_results'] = None
if 'deal_size_saved' not in st.session_state:
    st.session_state['deal_size_saved'] = ""
if 'years_int_saved' not in st.session_state:
    st.session_state['years_int_saved'] = 5
if 'target_sector_saved' not in st.session_state:
    st.session_state['target_sector_saved'] = ""

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

col_c1, col_c2 = st.columns(2)
with col_c1:
    acquirer_country = st.text_input("🌐 Acquirer Country", placeholder="e.g. India")
with col_c2:
    target_country = st.text_input("🌍 Target Country", placeholder="e.g. United States")

cross_border = (
    acquirer_country.strip().lower() != target_country.strip().lower()
    and acquirer_country.strip() != ""
    and target_country.strip() != ""
)
if cross_border:
    st.info(f"🌐 **Cross-Border Deal Detected:** {acquirer_country} → {target_country}  \nGlobal expansion context will be included in the analysis.")

# ─── DCF INPUTS ─────────────────────────────────────────────
st.header("📊 DCF & Valuation Inputs")
st.caption("Fill these for accurate DCF, NPV and Scenario Analysis")
col7, col8, col9 = st.columns(3)
with col7:
    wacc = st.number_input("WACC / Discount Rate (%)", min_value=1.0, max_value=30.0, value=12.0, step=0.5)
    terminal_growth = st.number_input("Terminal Growth Rate (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
with col8:
    target_revenue = st.number_input("Target Current Revenue ($M)", min_value=0.0, value=100.0, step=10.0)
    target_ebitda_margin = st.number_input("Target EBITDA Margin (%)", min_value=0.0, max_value=60.0, value=15.0, step=1.0)
with col9:
    revenue_growth_base = st.number_input("Expected Revenue Growth % (Base)", min_value=0.0, max_value=50.0, value=10.0, step=1.0)
    capex_percent = st.number_input("Capex as % of Revenue", min_value=0.0, max_value=30.0, value=5.0, step=0.5)

col10, col11, col12 = st.columns(3)
with col10:
    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=25.0, step=1.0)
with col11:
    depreciation_percent = st.number_input("Depreciation as % of Revenue", min_value=0.0, max_value=20.0, value=3.0, step=0.5)
with col12:
    synergy_value = st.number_input("Expected Annual Synergies ($M)", min_value=0.0, value=20.0, step=5.0)

# ─── ACQUIRER DOCUMENTS ─────────────────────────────────────
st.header("🏢 Acquirer Company Documents")
st.caption("Upload as many as you have — more docs = better analysis")
col13, col14 = st.columns(2)
with col13:
    acq_annual   = st.file_uploader("Annual Report (PDF)", type="pdf", key="acq_annual")
    acq_investor = st.file_uploader("Investor Presentation (PDF)", type="pdf", key="acq_investor")
with col14:
    acq_credit  = st.file_uploader("Credit Rating Report (PDF)", type="pdf", key="acq_credit")
    acq_concall = st.file_uploader("Concall Transcript (PDF)", type="pdf", key="acq_concall")

# ─── TARGET DOCUMENTS ───────────────────────────────────────
st.header("🎯 Target Company Documents")
col15, col16 = st.columns(2)
with col15:
    tgt_annual   = st.file_uploader("Annual Report (PDF)", type="pdf", key="tgt_annual")
    tgt_investor = st.file_uploader("Investor Presentation (PDF)", type="pdf", key="tgt_investor")
with col16:
    tgt_credit  = st.file_uploader("Credit Rating Report (PDF)", type="pdf", key="tgt_credit")
    tgt_concall = st.file_uploader("Concall Transcript (PDF)", type="pdf", key="tgt_concall")

# ─── INDUSTRY CONTEXT ───────────────────────────────────────
st.header("🌍 Industry Context")
col17a, col17b = st.columns(2)
with col17a:
    industry_report_acquirer = st.file_uploader(
        f"Acquirer Industry/Market Report — {acquirer_country if acquirer_country else 'Acquirer Country'} (PDF)",
        type="pdf", key="industry_acquirer")
with col17b:
    industry_report_target = st.file_uploader(
        f"Target Industry/Market Report — {target_country if target_country else 'Target Country'} (PDF)",
        type="pdf", key="industry_target")

industry_report = st.file_uploader("General / Global Industry Report (PDF) — optional", type="pdf", key="industry_general")

strategic_rationale = st.text_area(
    "Why is this acquisition being considered?",
    placeholder="e.g. STK Pharma wants retail distribution for OTC medicines...",
    height=120)

# ─── HELPER FUNCTIONS ───────────────────────────────────────
def extract_pdf_text(file, max_chars=3000):
    if file is None:
        return "Not provided"
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text[:max_chars]

def calculate_dcf(revenue, ebitda_margin, growth_base, wacc,
                  terminal_growth, capex_pct, tax_rate,
                  depreciation_pct, years, synergies):
    wacc_r = wacc / 100
    tg_r   = terminal_growth / 100
    tax_r  = tax_rate / 100
    scenarios = {
        "Bull Case": growth_base * 1.3,
        "Base Case": growth_base,
        "Bear Case": growth_base * 0.6
    }
    results = {}
    for scenario, growth in scenarios.items():
        growth_r = growth / 100
        fcfs = []
        rev  = revenue
        for yr in range(1, int(years) + 1):
            rev    = rev * (1 + growth_r)
            ebitda = rev * (ebitda_margin / 100)
            ebit   = ebitda - (rev * depreciation_pct / 100)
            nopat  = ebit * (1 - tax_r)
            capex  = rev * (capex_pct / 100)
            dep    = rev * (depreciation_pct / 100)
            syn    = synergies if yr >= 2 else synergies * 0.3
            fcfs.append(nopat + dep - capex + syn)
        terminal_fcf   = fcfs[-1] * (1 + tg_r)
        terminal_value = terminal_fcf / (wacc_r - tg_r)
        pv_fcfs        = [fcf / ((1 + wacc_r) ** (i + 1)) for i, fcf in enumerate(fcfs)]
        pv_terminal    = terminal_value / ((1 + wacc_r) ** int(years))
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

def calculate_sensitivity(revenue, ebitda_margin, growth_base, base_wacc,
                           base_tg, capex_pct, tax_rate, depreciation_pct, years, synergies):
    wacc_deltas   = [-2, -1, 0, +1, +2]
    growth_deltas = [-4, -2, 0, +2, +4]
    tg_deltas     = [-1.0, -0.5, 0.0, +0.5, +1.0]
    margin_deltas = [-4, -2, 0, +2, +4]

    def single_ev(rev, ebitda_m, growth, wacc_r_pct, tg_pct, capex_p, tax_r_pct, dep_p, yrs, syn):
        w  = wacc_r_pct / 100
        tg = tg_pct / 100
        t  = tax_r_pct / 100
        fcfs = []
        r = rev
        for yr in range(1, int(yrs) + 1):
            r      = r * (1 + growth / 100)
            ebitda = r * (ebitda_m / 100)
            ebit   = ebitda - (r * dep_p / 100)
            nopat  = ebit * (1 - t)
            capex  = r * (capex_p / 100)
            dep    = r * (dep_p / 100)
            s      = syn if yr >= 2 else syn * 0.3
            fcfs.append(nopat + dep - capex + s)
        tv    = fcfs[-1] * (1 + tg) / (w - tg)
        pv    = sum(fcf / ((1 + w) ** (i + 1)) for i, fcf in enumerate(fcfs))
        pv_tv = tv / ((1 + w) ** int(yrs))
        return round(pv + pv_tv, 1)

    wacc_labels   = [f"{base_wacc + d:.1f}%" for d in wacc_deltas]
    growth_labels = [f"{growth_base + d:.1f}%" for d in growth_deltas]
    matrix1 = []
    for wd in wacc_deltas:
        row = []
        for gd in growth_deltas:
            ev = single_ev(revenue, ebitda_margin, growth_base + gd,
                           base_wacc + wd, base_tg, capex_pct, tax_rate,
                           depreciation_pct, years, synergies)
            row.append(ev)
        matrix1.append(row)

    tg_labels     = [f"{base_tg + d:.1f}%" for d in tg_deltas]
    margin_labels = [f"{ebitda_margin + d:.1f}%" for d in margin_deltas]
    matrix2 = []
    for td in tg_deltas:
        row = []
        for md in margin_deltas:
            ev = single_ev(revenue, ebitda_margin + md, growth_base,
                           base_wacc, base_tg + td, capex_pct, tax_rate,
                           depreciation_pct, years, synergies)
            row.append(ev)
        matrix2.append(row)

    return {
        "matrix1": matrix1, "wacc_labels": wacc_labels, "growth_labels": growth_labels,
        "matrix2": matrix2, "tg_labels": tg_labels, "margin_labels": margin_labels,
    }

def display_sensitivity(sens, deal_size_str):
    st.subheader("🔬 Sensitivity Analysis")
    st.caption("Enterprise Value ($M) across key assumption combinations. ← base marks your inputs.")
    import pandas as pd

    st.markdown("##### Matrix 1: Enterprise Value ($M) — WACC vs Revenue Growth Rate")
    mid_row1 = len(sens["wacc_labels"]) // 2
    mid_col1 = len(sens["growth_labels"]) // 2
    rows1 = {}
    for i, w_lbl in enumerate(sens["wacc_labels"]):
        row_label = f"WACC {w_lbl}" + (" ←base" if i == mid_row1 else "")
        row_data  = {}
        for j, g_lbl in enumerate(sens["growth_labels"]):
            col_label = f"Gr {g_lbl}" + (" ←base" if j == mid_col1 else "")
            row_data[col_label] = f"${sens['matrix1'][i][j]}M"
        rows1[row_label] = row_data
    st.table(pd.DataFrame(rows1).T)

    st.markdown("##### Matrix 2: Enterprise Value ($M) — Terminal Growth Rate vs EBITDA Margin")
    mid_row2 = len(sens["tg_labels"]) // 2
    mid_col2 = len(sens["margin_labels"]) // 2
    rows2 = {}
    for i, t_lbl in enumerate(sens["tg_labels"]):
        row_label = f"TGR {t_lbl}" + (" ←base" if i == mid_row2 else "")
        row_data  = {}
        for j, m_lbl in enumerate(sens["margin_labels"]):
            col_label = f"Mgn {m_lbl}" + (" ←base" if j == mid_col2 else "")
            row_data[col_label] = f"${sens['matrix2'][i][j]}M"
        rows2[row_label] = row_data
    st.table(pd.DataFrame(rows2).T)

    try:
        deal_val = float(deal_size_str.replace("$","").replace("M","").replace("m","").replace(",","").strip())
        st.caption(f"💡 Deal size: **${deal_val}M** | 🟢 EV ≥ 115% of deal = underpriced | 🟡 EV 90–115% = fair | 🔴 EV < 90% = overpriced")
    except Exception:
        pass

def show_industry_benchmarks(sector):
    benchmarks = {
        "Pharma": {
            "wacc_range": "10% – 13%", "ebitda_multiple": "12x – 18x",
            "revenue_multiple": "3x – 5x", "good_irr": ">15%",
            "good_npv": "Positive + >20% of deal size", "terminal_growth": "3% – 5%",
            "typical_dcf_range": "$500M – $5000M", "red_flag_ebitda": "Below 8x EBITDA = distressed",
            "premium_paid": "20% – 40% over market",
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
            "wacc_range": "9% – 12%", "ebitda_multiple": "6x – 12x",
            "revenue_multiple": "0.5x – 1.5x", "good_irr": ">12%",
            "good_npv": "Positive + >15% of deal size", "terminal_growth": "2% – 4%",
            "typical_dcf_range": "$100M – $2000M", "red_flag_ebitda": "Below 5x EBITDA = distress",
            "premium_paid": "15% – 30% over market",
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
            "wacc_range": "10% – 15%", "ebitda_multiple": "15x – 30x",
            "revenue_multiple": "4x – 10x", "good_irr": ">18%",
            "good_npv": "Positive + >25% of deal size", "terminal_growth": "4% – 6%",
            "typical_dcf_range": "$200M – $10000M", "red_flag_ebitda": "Negative EBITDA OK if growth >30%",
            "premium_paid": "30% – 60% over market",
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
            "wacc_range": "11% – 14%", "ebitda_multiple": "8x – 15x",
            "revenue_multiple": "2x – 4x", "good_irr": ">14%",
            "good_npv": "Positive + >18% of deal size", "terminal_growth": "3% – 5%",
            "typical_dcf_range": "$500M – $8000M", "red_flag_ebitda": "NPA ratio > 5% = red flag",
            "premium_paid": "20% – 45% over book value",
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
            "wacc_range": "9% – 12%", "ebitda_multiple": "5x – 10x",
            "revenue_multiple": "0.5x – 1.2x", "good_irr": ">12%",
            "good_npv": "Positive + >15% of deal size", "terminal_growth": "2% – 4%",
            "typical_dcf_range": "$500M – $5000M", "red_flag_ebitda": "Below 4x EBITDA = distress",
            "premium_paid": "15% – 35% over market",
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
            "wacc_range": "9% – 11%", "ebitda_multiple": "12x – 20x",
            "revenue_multiple": "2x – 4x", "good_irr": ">14%",
            "good_npv": "Positive + >20% of deal size", "terminal_growth": "3% – 5%",
            "typical_dcf_range": "$300M – $5000M", "red_flag_ebitda": "Below 10x EBITDA = weak brand",
            "premium_paid": "25% – 50% over market",
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
            "wacc_range": "10% – 13%", "ebitda_multiple": "5x – 9x",
            "revenue_multiple": "0.5x – 1.5x", "good_irr": ">13%",
            "good_npv": "Positive + >15% of deal size", "terminal_growth": "2% – 3%",
            "typical_dcf_range": "$100M – $2000M", "red_flag_ebitda": "Below 4x EBITDA = commoditized",
            "premium_paid": "15% – 30% over market",
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
            "wacc_range": "10% – 14%", "ebitda_multiple": "7x – 15x",
            "revenue_multiple": "1x – 3x", "good_irr": ">14%",
            "good_npv": "Positive in base case", "terminal_growth": "3% – 4%",
            "typical_dcf_range": "Depends on sector", "red_flag_ebitda": "Below 5x EBITDA = scrutiny needed",
            "premium_paid": "20% – 40% over market",
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
        deal_val = float(deal_size_str.replace("$","").replace("M","").replace("m","").replace(",","").strip())
    except Exception:
        deal_val = None
    col_b, col_base, col_bear = st.columns(3)
    cols   = [col_b, col_base, col_bear]
    colors = ["🟢", "🟡", "🔴"]
    for i, (scenario, data) in enumerate(dcf_results.items()):
        with cols[i]:
            st.metric(label=f"{colors[i]} {scenario}",
                      value=f"${data['enterprise_value']}M",
                      delta=f"NPV: ${data['npv']}M")
            st.caption(f"Growth assumed: {data['growth_used']}%")
            if deal_val:
                premium = ((deal_val - data['enterprise_value']) / data['enterprise_value'] * 100)
                if premium > 20:
                    st.error(f"Deal premium: {premium:.1f}% — Overpriced")
                elif premium > 0:
                    st.warning(f"Deal premium: {premium:.1f}% — Fair")
                else:
                    st.success(f"Discount: {abs(premium):.1f}% — Underpriced")
    st.subheader("📈 Free Cash Flow Projections ($M)")
    year_labels = [f"Year {i+1}" for i in range(int(years))]
    table_data  = {"Year": year_labels}
    for scenario, data in dcf_results.items():
        table_data[scenario] = [f"${v}M" for v in data["fcfs"]]
    st.table(table_data)
    st.subheader("🏁 Valuation Summary")
    summary = {"Metric": ["Enterprise Value", "PV of Terminal Value", "NPV of Deal"]}
    for scenario, data in dcf_results.items():
        summary[scenario] = [
            f"${data['enterprise_value']}M",
            f"${data['pv_terminal']}M",
            f"${data['npv']}M"
        ]
    st.table(summary)

def parse_and_render_result(result_text, acquirer, target):
    """
    Splits AI output at COMPARISON_TABLE_END marker.
    Before marker  → extract pipe table and render as st.dataframe
    After marker   → render as normal markdown
    """
    import pandas as pd

    marker = "COMPARISON_TABLE_END"

    if marker not in result_text:
        # Fallback: just render everything as markdown
        st.markdown(result_text)
        return

    before, after = result_text.split(marker, 1)

    # ── Find the pipe table inside 'before' ──────────────────
    lines = before.split("\n")
    table_lines = []
    pre_table   = []
    in_table    = False

    for line in lines:
        stripped = line.strip()
        if "|" in stripped and not in_table:
            in_table = True
        if in_table:
            if "|" in stripped:
                table_lines.append(stripped)
            else:
                if stripped:          # non-empty non-pipe line ends table
                    in_table = False
        else:
            pre_table.append(line)

    # Render text before the table (exec summary etc.)
    if pre_table:
        st.markdown("\n".join(pre_table))

    # Render the comparison table
    if table_lines:
        st.subheader("📊 Acquirer vs Target — Financial Comparison")
        rows = []
        for line in table_lines:
            cells = [c.strip() for c in line.split("|")]
            # Drop empty leading/trailing cells from lines like "| a | b |"
            cells = [c for c in cells if c != ""]
            if len(cells) >= 4:
                rows.append(cells[:4])

        if rows:
            # First row = header
            header = rows[0]
            data_rows = rows[1:]
            df = pd.DataFrame(data_rows, columns=header)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    header[0]: st.column_config.TextColumn(header[0], width="medium"),
                    header[1]: st.column_config.TextColumn(header[1], width="medium"),
                    header[2]: st.column_config.TextColumn(header[2], width="medium"),
                    header[3]: st.column_config.TextColumn(header[3], width="large"),
                }
            )

    # Render everything after the marker as normal markdown
    if after.strip():
        st.markdown(after.strip())


def run_analysis(docs, acquirer, target, deal_size,
                 acquirer_sector, target_sector,
                 acquirer_country, target_country,
                 rationale, dcf_results, wacc, terminal_growth, years):
    bull = dcf_results["Bull Case"]
    base = dcf_results["Base Case"]
    bear = dcf_results["Bear Case"]
    cross_border = (
        acquirer_country.strip().lower() != target_country.strip().lower()
        and acquirer_country.strip() != "" and target_country.strip() != ""
    )
    if cross_border:
        cross_border_note = f"""
═══════════════════════════════════
CROSS-BORDER / GLOBAL EXPANSION CONTEXT
═══════════════════════════════════
Acquirer Country : {acquirer_country}
Target Country   : {target_country}
Address: FX risk, regulatory approvals in both countries, repatriation of profits,
local labour laws in {target_country}, tax treaty implications, cultural integration,
geopolitical risk, and global expansion strategic value for {acquirer}.
Acquirer Industry Context ({acquirer_country}): {docs['industry_acquirer']}
Target Industry Context ({target_country}): {docs['industry_target']}
"""
    else:
        cross_border_note = f"""
═══════════════════════════════════
DOMESTIC DEAL CONTEXT
═══════════════════════════════════
Both companies in: {acquirer_country if acquirer_country else 'Not specified'}
Acquirer Industry Context: {docs['industry_acquirer']}
Target Industry Context:   {docs['industry_target']}
"""
    prompt = f"""
You are a Managing Director at McKinsey M&A practice.
Analyze ALL documents and give a complete due diligence report.

DEAL OVERVIEW
Acquirer : {acquirer} | Sector: {acquirer_sector} | Country: {acquirer_country}
Target   : {target}   | Sector: {target_sector}   | Country: {target_country}
Deal Size: {deal_size}
Strategic Rationale: {rationale}
{cross_border_note}

DCF RESULTS
Projection: {years} Yrs | WACC: {wacc}% | Terminal Growth: {terminal_growth}%
Bull Case EV: ${bull['enterprise_value']}M | FCFs: {bull['fcfs']} | NPV: ${bull['npv']}M
Base Case EV: ${base['enterprise_value']}M | FCFs: {base['fcfs']} | NPV: ${base['npv']}M
Bear Case EV: ${bear['enterprise_value']}M | FCFs: {bear['fcfs']} | NPV: ${bear['npv']}M

ACQUIRER DOCUMENTS
Annual Report: {docs['acq_annual']}
Investor Presentation: {docs['acq_investor']}
Credit Rating: {docs['acq_credit']}
Concall: {docs['acq_concall']}

TARGET DOCUMENTS
Annual Report: {docs['tgt_annual']}
Investor Presentation: {docs['tgt_investor']}
Credit Rating: {docs['tgt_credit']}
Concall: {docs['tgt_concall']}

GENERAL INDUSTRY CONTEXT
{docs['industry_general']}

PROVIDE ANALYSIS IN THESE SECTIONS:

1. EXECUTIVE SUMMARY
   Deal thesis (2 lines):
   [write thesis here]

   Top 3 reasons to PROCEED:
   a. [reason 1]
   b. [reason 2]
   c. [reason 3]

   Top 3 reasons to be CAUTIOUS:
   a. [reason 1]
   b. [reason 2]
   c. [reason 3]

   Upfront Recommendation:
   [write recommendation here]

2. ACQUIRER & TARGET COMPARISON PROFILE
   Output this section ONLY as a pipe-delimited table with EXACTLY this format, one row per line:
   Parameter | {acquirer} | {target} | Findings & Comments
   Revenue (Y1) | [value] | [value] | [finding]
   Revenue (Y2) | [value] | [value] | [finding]
   Revenue (Y3) | [value] | [value] | [finding]
   YoY Revenue Growth | [value] | [value] | [finding]
   EBITDA Margin (Y1) | [value] | [value] | [finding]
   EBITDA Margin (Y2) | [value] | [value] | [finding]
   EBITDA Margin (Y3) | [value] | [value] | [finding]
   Net Profit Margin | [value] | [value] | [finding]
   Total Debt | [value] | [value] | [finding]
   Net Debt | [value] | [value] | [finding]
   Cash & Liquid Assets | [value] | [value] | [finding]
   Free Cash Flow | [value] | [value] | [finding]
   Debt-to-Equity Ratio | [value] | [value] | [finding]
   Interest Coverage Ratio | [value] | [value] | [finding]
   Current Ratio | [value] | [value] | [finding]
   Credit Rating | [value] | [value] | [finding]
   Market Share | [value] | [value] | [finding]
   Key Competitive Moat | [value] | [value] | [finding]
   COMPARISON_TABLE_END

4. CROSS-SECTOR STRATEGIC FIT
   - Related or unrelated diversification?
   - Capability transfer, distribution synergies
   - Customer base overlap or new access
   - Global expansion rationale (if cross-border)
   - Strategic fit rating: Strong/Moderate/Weak + why

5. REVENUE SYNERGIES (What | How | $ Value | Timeline for each)
6. COST SYNERGIES (What | How | $ Value | Timeline for each)

7. DEEP FINANCIAL ANALYSIS
   A) DCF INTERPRETATION
   B) NPV ANALYSIS
   C) SCENARIO ANALYSIS (Bull/Base/Bear with probability weights)
   D) SENSITIVITY COMMENTARY (which input drives EV most? at what WACC does deal break?)
   E) VALUATION MULTIPLES vs sector benchmarks
   F) DEAL FUNDING ANALYSIS (debt/equity mix, post-deal leverage)
   G) RETURNS ANALYSIS (IRR, payback, EPS accretion/dilution Y1 & Y3)
   H) FINANCIAL RED FLAGS

8. CROSS-BORDER RISK (if applicable): FX, regulatory, geopolitical, tax, cultural
9. INTEGRATION RISK: culture, tech, talent, customers, timeline
10. RISK MATRIX (Risk | Probability | Impact | Mitigation)
11. DEAL RECOMMENDATION
    Verdict: PROCEED / CONDITIONS / DO NOT PROCEED
    Price range: Floor (bear) / Fair (base) / Max (bull)
    If Proceed: structure, conditions, first 100 days
    If Not: dealbreakers, alternatives

Use actual numbers from documents. State assumptions where data missing.
Write for a Fortune 500 board presentation.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000
    )
    return response.choices[0].message.content

# ─── SHOW PREVIOUS RESULT IF EXISTS ────────────────────────
if st.session_state['analysis_done']:
    display_dcf_results(
        st.session_state['dcf_results'],
        st.session_state['deal_size_saved'],
        st.session_state['years_int_saved']
    )
    display_sensitivity(st.session_state['sens_results'], st.session_state['deal_size_saved'])
    show_industry_benchmarks(st.session_state['target_sector_saved'])
    st.success("✅ Complete M&A Due Diligence Done!")
    st.markdown("---")
    parse_and_render_result(
        st.session_state['last_result'],
        st.session_state['last_acquirer'],
        st.session_state['last_target']
    )
    st.download_button(
        "📥 Download Full DD Report",
        st.session_state['last_result'],
        file_name=f"DD_{st.session_state['last_acquirer']}_acquires_{st.session_state['last_target']}.txt",
        mime="text/plain",
        key="download_persistent"
    )
    st.markdown("---")
    st.info("👆 Previous analysis shown above. Fill new details and click Run to refresh.")

# ─── RUN BUTTON ─────────────────────────────────────────────
if st.button("🔍 Run Complete M&A Due Diligence", type="primary"):
    if not acquirer or not target:
        st.warning("⚠️ Please enter both company names.")
    elif not acq_annual and not tgt_annual:
        st.warning("⚠️ Upload at least one annual report.")
    else:
        years_int = int(projection_years.split()[0])

        dcf_results = calculate_dcf(
            revenue=target_revenue, ebitda_margin=target_ebitda_margin,
            growth_base=revenue_growth_base, wacc=wacc,
            terminal_growth=terminal_growth, capex_pct=capex_percent,
            tax_rate=tax_rate, depreciation_pct=depreciation_percent,
            years=years_int, synergies=synergy_value
        )
        display_dcf_results(dcf_results, deal_size, years_int)

        sens = calculate_sensitivity(
            revenue=target_revenue, ebitda_margin=target_ebitda_margin,
            growth_base=revenue_growth_base, base_wacc=wacc,
            base_tg=terminal_growth, capex_pct=capex_percent,
            tax_rate=tax_rate, depreciation_pct=depreciation_percent,
            years=years_int, synergies=synergy_value
        )
        display_sensitivity(sens, deal_size)
        show_industry_benchmarks(target_sector)

        docs = {
            "acq_annual":        extract_pdf_text(acq_annual),
            "acq_investor":      extract_pdf_text(acq_investor),
            "acq_credit":        extract_pdf_text(acq_credit),
            "acq_concall":       extract_pdf_text(acq_concall),
            "tgt_annual":        extract_pdf_text(tgt_annual),
            "tgt_investor":      extract_pdf_text(tgt_investor),
            "tgt_credit":        extract_pdf_text(tgt_credit),
            "tgt_concall":       extract_pdf_text(tgt_concall),
            "industry_acquirer": extract_pdf_text(industry_report_acquirer),
            "industry_target":   extract_pdf_text(industry_report_target),
            "industry_general":  extract_pdf_text(industry_report),
        }

        with st.spinner("Running full AI analysis... 40-60 seconds ⏳"):
            result = run_analysis(
                docs=docs, acquirer=acquirer, target=target,
                deal_size=deal_size, acquirer_sector=acquirer_sector,
                target_sector=target_sector, acquirer_country=acquirer_country,
                target_country=target_country, rationale=strategic_rationale,
                dcf_results=dcf_results, wacc=wacc,
                terminal_growth=terminal_growth, years=projection_years
            )

        # ── Save everything to session state ──────────────────
        st.session_state['analysis_done']      = True
        st.session_state['last_result']        = result
        st.session_state['last_acquirer']      = acquirer
        st.session_state['last_target']        = target
        st.session_state['dcf_results']        = dcf_results
        st.session_state['sens_results']       = sens
        st.session_state['deal_size_saved']    = deal_size
        st.session_state['years_int_saved']    = years_int
        st.session_state['target_sector_saved']= target_sector

        st.success("✅ Complete M&A Due Diligence Done!")
        st.markdown("---")
        parse_and_render_result(result, acquirer, target)
        st.download_button(
            "📥 Download Full DD Report",
            result,
            file_name=f"DD_{acquirer}_acquires_{target}.txt",
            mime="text/plain",
            key="download_fresh"
        )