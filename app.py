import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scoring import load_data, analyze_file, _letter_grade, _grade_color, build_score_explanations

st.set_page_config(page_title="Pipeline Health Score", page_icon="📊", layout="wide")

# ── Theme — mid-dark gray palette ────────────────────────────────────
BG = "#1e2130"
CARD = "#272b3d"
BORDER = "#353a50"
TEXT = "#e0e3ed"
TEXT_MID = "#9ba2b8"
TEXT_DIM = "#6b7394"
GREEN = "#34d399"
BLUE = "#60a5fa"
PURPLE = "#a78bfa"
AMBER = "#fbbf24"
RED = "#f87171"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: {BG};
        color: {TEXT};
    }}
    .js-plotly-plot .plotly .modebar {{ display:none !important; }}
    div[data-testid="stMetric"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 14px 16px;
    }}
    div[data-testid="stMetric"] label {{
        color: {TEXT_MID} !important;
        font-size: 11px !important;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        font-size: 18px !important;
        font-weight: 600 !important;
        color: {TEXT} !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap:0; border-bottom:1px solid {BORDER}; }}
    .stTabs [data-baseweb="tab"] {{ font-size:13px; font-weight:500; color:{TEXT_MID}; padding:10px 20px; }}
    .stTabs [aria-selected="true"] {{ color:{TEXT} !important; border-bottom-color:{BLUE} !important; }}
    section[data-testid="stSidebar"] {{ background:#1a1d2e; border-right:1px solid {BORDER}; }}
    .stDataFrame {{ border-radius:10px; overflow:hidden; }}
    div[data-testid="stRadio"] > div {{ gap:0 !important; }}
    div[data-testid="stRadio"] label {{
        font-size:12px !important; font-weight:500 !important;
        padding:5px 14px !important; border:1px solid {BORDER} !important;
        border-radius:6px !important; margin-right:4px !important;
    }}
</style>
""", unsafe_allow_html=True)


# ── Reusable components ──────────────────────────────────────────────

def grade_color(grade):
    if grade.startswith("A"): return GREEN
    if grade.startswith("B"): return BLUE
    if grade.startswith("C"): return AMBER
    if grade.startswith("D"): return "#fb923c"
    return RED


def hero_card(account_name, grade, industry, records, age_str, owner):
    gc = grade_color(grade)
    st.markdown(f"""
    <div style="text-align:center; padding:36px 20px; border-radius:16px;
                background:#3d4260;
                border:1px solid #4e5478; margin-bottom:24px;">
        <div style="font-size:20px; font-weight:600; color:#fff; margin-bottom:2px;">{account_name}</div>
        <div style="font-size:12px; color:#b0b6cc; margin-bottom:20px;">
            {industry} &nbsp;&middot;&nbsp; {records:,} records &nbsp;&middot;&nbsp; Age: {age_str} &nbsp;&middot;&nbsp; {owner}
        </div>
        <div style="font-size:72px; font-weight:700; color:{gc}; line-height:1; letter-spacing:-2px;">{grade}</div>
    </div>""", unsafe_allow_html=True)


def sub_grades(items):
    cols_html = ""
    for val, label, tip in items:
        color = grade_color(val) if len(val) <= 2 else TEXT
        cols_html += f"""
        <div style="flex:1; text-align:center; padding:18px 8px 14px;
                    background:{CARD}; border:1px solid {BORDER}; border-radius:12px;" title="{tip}">
            <div style="font-size:26px; font-weight:700; color:{color}; line-height:1; margin-bottom:6px;">{val}</div>
            <div style="font-size:9px; font-weight:600; color:{TEXT_DIM}; text-transform:uppercase; letter-spacing:1px;">{label}</div>
        </div>"""
    st.markdown(f'<div style="display:flex; gap:10px; margin-bottom:24px;">{cols_html}</div>', unsafe_allow_html=True)


def section_divider(title, grade=None, score=None):
    badge = f'<span style="font-size:12px; font-weight:700; padding:3px 8px; border-radius:5px; color:#fff; background:{grade_color(grade)};">{grade}</span>' if grade else ""
    sc = f'<span style="font-size:12px; color:{TEXT_DIM}; margin-left:4px;">{score}</span>' if score is not None else ""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin:28px 0 14px; padding-bottom:10px; border-bottom:1px solid {BORDER};">
        <span style="font-size:14px; font-weight:600; color:{TEXT};">{title}</span>{badge}{sc}
    </div>""", unsafe_allow_html=True)


def render_flags(flags):
    if not flags:
        st.markdown(f'<div style="color:{TEXT_DIM}; font-size:12px; font-style:italic; padding:6px 0;">No flags — pipeline looks healthy</div>', unsafe_allow_html=True)
        return
    for sev, msg in flags:
        bg = "rgba(248,113,113,0.10)" if sev == "RED" else "rgba(251,191,36,0.10)"
        bc = RED if sev == "RED" else AMBER
        st.markdown(f'<div style="padding:10px 14px; border-radius:8px; margin-bottom:6px; font-size:12px; font-weight:500; background:{bg}; border-left:3px solid {bc}; color:{bc};">{msg}</div>', unsafe_allow_html=True)


def plotly_defaults(fig, height=400):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT_MID, size=11),
        margin=dict(l=0, r=16, t=4, b=4),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        coloraxis_showscale=False, showlegend=False,
    )
    return fig


PHASE_SORT = {"01 Suspect": 0, "02 Cleansing": 1, "03 Lead": 2, "04 Suspended": 3}
OUTCOME_SORT = {"01 Intro": 0, "03 No Interest": 1, "02 Wait": 2, "Info": 3, "04 No Response": 4, "Appt A": 5}


# ── App ──────────────────────────────────────────────────────────────

st.markdown(f"""
<div style="margin-bottom:28px;">
    <h1 style="font-size:24px; font-weight:700; color:{TEXT}; letter-spacing:-0.5px; margin:0 0 2px;">Pipeline Health Score</h1>
    <p style="font-size:13px; color:{TEXT_DIM}; margin:0;">Automated pipeline analysis &amp; health grading</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload pipeline export", type=["csv", "xlsx", "xls"], label_visibility="collapsed")

if uploaded_file is not None:
    with st.spinner("Analyzing..."):
        df = load_data(uploaded_file)
        results, owner_grades = analyze_file(df)

    all_managers = sorted(set(r["sales_manager"] for r in results.values()))
    with st.sidebar:
        st.markdown(f'<p style="font-size:11px; font-weight:600; color:{TEXT_DIM}; text-transform:uppercase; letter-spacing:1px;">Filters</p>', unsafe_allow_html=True)
        selected_manager = st.selectbox("Sales Manager", ["All"] + all_managers, key="sb_mgr")

    filtered = {k: v for k, v in results.items() if selected_manager == "All" or v["sales_manager"] == selected_manager}

    _ob = {}
    for a, r in filtered.items():
        o = r["delivery_owner"]
        _ob.setdefault(o, []).append({"account": a, "sop_score": r["sop"]["score"]})
    f_owner_grades = {o: {"avg_sop_score": round(np.mean([x["sop_score"] for x in a]), 1),
                          "avg_sop_grade": _letter_grade(np.mean([x["sop_score"] for x in a])),
                          "account_count": len(a), "accounts": a} for o, a in _ob.items()}

    tab_dash, tab_acct, tab_own = st.tabs(["Dashboard", "Account Details", "Delivery Owner Grades"])

    # ═══════════════════════════════════════════════════════════
    # DASHBOARD
    # ═══════════════════════════════════════════════════════════
    with tab_dash:
        if not filtered:
            st.warning("No accounts match the current filter.")
        else:
            scores = [r["overall_score"] for r in filtered.values()]
            avg_s = sum(scores) / len(scores)
            avg_sop = np.mean([r["sop"]["score"] for r in filtered.values()])
            avg_cq = np.mean([r["contact_quality"]["score"] for r in filtered.values()])
            avg_lt = np.mean([r["list_tags"]["score"] for r in filtered.values()])
            healthy = sum(1 for s in scores if s >= 85)

            c1, c2, c3 = st.columns(3)
            c1.metric("Accounts Analyzed", len(filtered))
            c2.metric("Average Score", f"{avg_s:.0f} ({_letter_grade(avg_s)})",
                       help="Weighted: SOP 40%, Contact Quality 25%, List Tags 25%, Pipeline Age 10%")
            c3.metric("Healthy Pipelines (B+)", healthy)

            cb1, cb2, cb3 = st.columns(3)
            cb1.metric("Avg SOP", f"{avg_sop:.0f} ({_letter_grade(avg_sop)})",
                       help="Pipeline distribution, KDM rate, past due calls. 40% of overall.")
            cb2.metric("Avg Contact Quality", f"{avg_cq:.0f} ({_letter_grade(avg_cq)})",
                       help="Name, phone, title, email completeness vs industry benchmark. 25% of overall.")
            cb3.metric("Avg List Tags", f"{avg_lt:.0f} ({_letter_grade(avg_lt)})",
                       help="Historical tier data vs industry benchmark. 25% of overall.")

            st.markdown(f'<div style="height:12px;"></div>', unsafe_allow_html=True)

            sort_dir = st.radio("Sort", ["Low to High", "High to Low"], horizontal=True, key="d_sort", label_visibility="collapsed")
            asc = sort_dir == "Low to High"

            cl, cr = st.columns(2)
            with cl:
                st.markdown(f'<p style="font-size:12px; font-weight:600; color:{TEXT_MID}; margin-bottom:2px;">Overall Score Distribution</p>', unsafe_allow_html=True)
                sdf = pd.DataFrame([{"Account": n, "Score": r["overall_score"], "Grade": r["overall_grade"]} for n, r in filtered.items()])
                sdf = sdf.sort_values("Score", ascending=not asc).reset_index(drop=True)
                fig = px.bar(sdf, x="Score", y="Account", orientation="h", color="Score",
                             color_continuous_scale=[RED, AMBER, GREEN], range_color=[0, 100], hover_data=["Grade"])
                fig.update_layout(yaxis=dict(dtick=1, categoryorder="array", categoryarray=sdf["Account"].tolist()), xaxis_range=[0, 100])
                st.plotly_chart(plotly_defaults(fig, max(380, len(filtered) * 26)), use_container_width=True)

            with cr:
                st.markdown(f'<p style="font-size:12px; font-weight:600; color:{TEXT_MID}; margin-bottom:2px;">Category Breakdown</p>', unsafe_allow_html=True)
                cat = st.radio("", ["SOP", "Contact Quality", "List Tags"], horizontal=True, key="d_cat", label_visibility="collapsed")
                ck = {"SOP": "sop", "Contact Quality": "contact_quality", "List Tags": "list_tags"}[cat]
                cc = {"SOP": BLUE, "Contact Quality": GREEN, "List Tags": PURPLE}[cat]
                cdf = pd.DataFrame([{"Account": n, "Score": r[ck]["score"], "Grade": r[ck]["grade"]} for n, r in filtered.items()])
                cdf = cdf.sort_values("Score", ascending=not asc).reset_index(drop=True)
                fig2 = px.bar(cdf, x="Score", y="Account", orientation="h", hover_data=["Grade"])
                fig2.update_traces(marker_color=cc, marker_opacity=0.85)
                fig2.update_layout(yaxis=dict(dtick=1, categoryorder="array", categoryarray=cdf["Account"].tolist()), xaxis_range=[0, 100])
                st.plotly_chart(plotly_defaults(fig2, max(380, len(filtered) * 26)), use_container_width=True)

    # ═══════════════════════════════════════════════════════════
    # ACCOUNT DETAILS
    # ═══════════════════════════════════════════════════════════
    with tab_acct:
        fmode = st.radio("View by", ["Select Accounts", "Delivery Owner"], horizontal=True, key="a_mode")
        if fmode == "Select Accounts":
            sel_accts = st.multiselect("Accounts", sorted(filtered.keys()),
                                       default=[sorted(filtered.keys())[0]] if filtered else [], key="a_sel")
        else:
            a_own = st.selectbox("Delivery Owner", sorted(set(r["delivery_owner"] for r in filtered.values())), key="a_own")
            sel_accts = sorted([n for n, r in filtered.items() if r["delivery_owner"] == a_own])
            st.caption(f"{len(sel_accts)} accounts")

        for idx, acct in enumerate(sel_accts):
            r = filtered[acct]
            exp = build_score_explanations(r)
            sop = r["sop"]["details"]
            cq = r["contact_quality"]["details"]
            lt = r["list_tags"]["details"]

            age_y, age_m = sop["account_age_years"], sop["account_age_remaining_months"]
            age_str = f"{age_y}y {age_m}m" if age_y > 0 else f"{age_m}m"

            # ── Hero ──
            hero_card(acct, r["overall_grade"], r["industry"], r["record_count"], age_str, r["delivery_owner"])
            sub_grades([
                (r["sop"]["grade"], "SOP Compliance", exp["sop"]),
                (r["contact_quality"]["grade"], "Contact Quality", exp["contact"]),
                (r["list_tags"]["grade"], "List Tags", exp["tags"]),
                (r["avg_record_age"], "Avg Record Age", exp["age"]),
            ])

            # ── Flags ──
            section_divider("Flags")
            render_flags(r["flags"])

            # ── SOP ──
            section_divider("SOP Compliance", r["sop"]["grade"], r["sop"]["score"])
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Suspects", sop["suspect_count"], help=exp["suspects"])
            s2.metric("Cleansing", sop["cleansing_count"], help=exp["cleansing"])
            s3.metric("Intros", sop["intro_count"], help=exp["intros"])
            s4.metric("Suspended", sop["suspended_count"], help=exp["suspended"])
            s5, s6, s7, s8 = st.columns(4)
            s5.metric("KDMs (30d)", f"{sop['kdm_last_30']} / {sop['kdm_monthly_target']}", help=exp["kdm"])
            s6.metric("Account Age", age_str)
            s7.metric("Past Due Calls", sop["past_due_count"], help=exp["past_due"])
            s8.metric("Severe Past Due (7d+)", sop["severe_past_due"])

            # ── Funnel: 3 phases, hover on Lead shows outcome breakdown ──
            lb = sop.get("lead_outcome_breakdown", {})
            lead_hover = "<br>".join([f"  {oc}: {cnt}" for oc, cnt in
                         sorted(lb.items(), key=lambda x: OUTCOME_SORT.get(x[0], 99))]) if lb else "No lead data"

            fc, sc = st.columns([3, 1])
            with fc:
                ff = go.Figure(go.Funnel(
                    y=["01 Suspect", "02 Cleansing", "03 Lead"],
                    x=[sop["suspect_count"], sop["cleansing_count"], sop["lead_count"]],
                    text=[str(sop["suspect_count"]), str(sop["cleansing_count"]), str(sop["lead_count"])],
                    textinfo="text",
                    hovertext=[
                        f"01 Suspect: {sop['suspect_count']} records",
                        f"02 Cleansing: {sop['cleansing_count']} records",
                        f"03 Lead: {sop['lead_count']} records<br><br><b>Outcome Breakdown:</b><br>{lead_hover}",
                    ],
                    hoverinfo="text",
                    marker=dict(color=[GREEN, BLUE, PURPLE]),
                    connector=dict(line=dict(color="rgba(255,255,255,0.04)", width=1)),
                ))
                st.plotly_chart(plotly_defaults(ff, 220), use_container_width=True)
            with sc:
                st.markdown(f"""
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                            padding:20px 12px; border-radius:12px; background:rgba(248,113,113,0.10);
                            border:1px solid rgba(248,113,113,0.15); text-align:center; min-height:160px;">
                    <div style="font-size:28px; font-weight:700; color:{RED};">{sop['suspended_count']}</div>
                    <div style="font-size:9px; font-weight:600; color:{RED}; text-transform:uppercase; letter-spacing:1px; margin-top:4px;">Suspended</div>
                    <div style="font-size:10px; color:rgba(248,113,113,0.6); margin-top:8px;">{sop['suspended_last_30']} in last 30d</div>
                </div>""", unsafe_allow_html=True)

            # ── Contact Quality ──
            section_divider("Contact Quality", r["contact_quality"]["grade"], r["contact_quality"]["score"])
            st.markdown(f'<p style="font-size:11px; color:{TEXT_DIM}; margin:-8px 0 12px;">Benchmarked against: {cq["benchmark_industry"]}</p>', unsafe_allow_html=True)
            q1, q2, q3 = st.columns(3)
            q1.metric("Full Names", f"{cq['first_name_count']:,} ({cq['first_name_pct']}%)",
                      help="Records with a real first name filled in.")
            q2.metric("Bad Last Names", f"{cq['bad_last_name_count']:,} ({cq['bad_last_name_pct']}%)",
                      help="Last names with asterisks — missing data.")
            q3.metric("Titles", f"{cq['title_count']:,} ({cq['title_pct']}%)",
                      help="Records with job title. Bonus factor.")
            q4, q5, q6 = st.columns(3)
            q4.metric("Any Phone", f"{cq['either_phone_count']:,} ({cq['either_phone_pct']}%)",
                      help="Records with at least one phone number (Direct or Mobile). Positive factor.")
            q5.metric("Both Phones", f"{cq['both_phones_count']:,} ({cq['both_phones_pct']}%)",
                      help="Records with BOTH Direct and Mobile — best contact rate.")
            q6.metric("Email", f"{cq['email_count']:,} ({cq['email_pct']}%)",
                      help="Email addresses. Low weight in scoring.")

            # ── List Tags ──
            section_divider("List Tag Details", r["list_tags"]["grade"], r["list_tags"]["score"])
            st.markdown(f'<p style="font-size:11px; color:{TEXT_DIM}; margin:-8px 0 12px;">Industry benchmark: {lt["benchmark_tags_pct"]}% filled, {lt["benchmark_tier1_pct"]}% Tier 1 &nbsp;&middot;&nbsp; Accepts tag codes (A, T, W, NI, I1) and tier numbers (1, 2, 3)</p>', unsafe_allow_html=True)
            t1, t2, t3 = st.columns(3)
            t1.metric("Tags Filled", f"{lt['tags_filled']:,} ({lt['tags_filled_pct']}%)",
                      help="Records with any historical list tag (letter codes or tier numbers).")
            t2.metric("Tier 1 (A / T / 1)", f"{lt['tier1_count']:,} ({lt['tier1_pct']}%)",
                      help="Appt A, Appt Rescheduled, TOC Open, or tier number 1 — highest value.")
            t3.metric("Tier 2 (W / NI / 2)", f"{lt['tier2_count']:,} ({lt['tier2_pct']}%)",
                      help="Wait, No Interest, or tier number 2 — mid value.")
            t4, _, _ = st.columns(3)
            t4.metric("Tier 3 (I1 / 3)", f"{lt['tier3_count']:,} ({lt['tier3_pct']}%)",
                      help="Intro records or tier number 3 — lower value historical data.")

            # ── Tier 1 pipeline location: single bar chart with hover outcome detail ──
            if lt.get("tier1_by_phase") and lt["tier1_count"] > 0:
                st.markdown(f'<p style="font-size:11px; font-weight:500; color:{TEXT_MID}; margin-top:14px;">Tier 1 Records — Pipeline Location</p>', unsafe_allow_html=True)
                phase_detail = lt.get("tier1_phase_outcome_detail", {})
                phase_items = sorted(lt["tier1_by_phase"].items(), key=lambda x: PHASE_SORT.get(x[0], 99))
                p_names = [p for p, _ in phase_items]
                p_counts = [c for _, c in phase_items]
                p_hovers = []
                for phase, count in phase_items:
                    outcomes = phase_detail.get(phase, {})
                    if outcomes:
                        detail = "<br>".join([f"  {oc}: {cnt}" for oc, cnt in
                                 sorted(outcomes.items(), key=lambda x: OUTCOME_SORT.get(x[0], 99))])
                        p_hovers.append(f"{phase}: {count}<br><br><b>DevOutcome:</b><br>{detail}")
                    else:
                        p_hovers.append(f"{phase}: {count}")

                fig_t1 = go.Figure(go.Bar(
                    y=p_names, x=p_counts, orientation="h",
                    marker_color=PURPLE, marker_opacity=0.85,
                    hovertext=p_hovers, hoverinfo="text",
                    text=p_counts, textposition="auto",
                ))
                fig_t1.update_layout(yaxis=dict(categoryorder="array", categoryarray=p_names))
                st.plotly_chart(plotly_defaults(fig_t1, max(140, len(p_names) * 40)), use_container_width=True)

            # ── List Source ──
            section_divider("Primary List Source")
            src = r["list_sources"]
            if src["breakdown"]:
                sdf = pd.DataFrame([{"Source": k, "Count": v, "Pct": f"{src['pct_breakdown'][k]}%"}
                       for k, v in sorted(src["breakdown"].items(), key=lambda x: -x[1])])
                st.dataframe(sdf, use_container_width=True, hide_index=True)

            if idx < len(sel_accts) - 1:
                st.markdown(f'<div style="height:40px; border-bottom:1px solid {BORDER}; margin-bottom:28px;"></div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # DELIVERY OWNER GRADES
    # ═══════════════════════════════════════════════════════════
    with tab_own:
        st.markdown(f"""
        <div style="margin-bottom:20px;">
            <h2 style="font-size:20px; font-weight:700; color:{TEXT}; margin:0 0 2px;">Delivery Owner Performance</h2>
            <p style="font-size:12px; color:{TEXT_DIM}; margin:0;">Graded on average SOP Compliance across accounts</p>
        </div>""", unsafe_allow_html=True)

        if f_owner_grades:
            odf = pd.DataFrame([
                {"Delivery Owner": o, "Accounts": d["account_count"],
                 "Avg SOP Score": d["avg_sop_score"], "SOP Grade": d["avg_sop_grade"]}
                for o, d in sorted(f_owner_grades.items(), key=lambda x: -x[1]["avg_sop_score"])
            ])
            st.dataframe(odf, use_container_width=True, hide_index=True)

            fig_o = px.bar(odf.sort_values("Avg SOP Score", ascending=True),
                x="Avg SOP Score", y="Delivery Owner", orientation="h",
                color="Avg SOP Score", color_continuous_scale=[RED, AMBER, GREEN],
                range_color=[0, 100], hover_data=["SOP Grade", "Accounts"])
            fig_o.update_layout(xaxis_range=[0, 100])
            st.plotly_chart(plotly_defaults(fig_o, max(280, len(f_owner_grades) * 28)), use_container_width=True)

            st.markdown(f'<div style="height:12px;"></div>', unsafe_allow_html=True)
            sel_own = st.selectbox("Drill down", sorted(f_owner_grades.keys()), key="o_dd")
            if sel_own:
                og = f_owner_grades[sel_own]
                gc = grade_color(og["avg_sop_grade"])
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:14px; margin:14px 0 16px;">
                    <div style="font-size:32px; font-weight:700; color:{gc};">{og['avg_sop_grade']}</div>
                    <div>
                        <div style="font-size:15px; font-weight:600; color:{TEXT};">{sel_own}</div>
                        <div style="font-size:11px; color:{TEXT_MID};">SOP: {og['avg_sop_score']} &middot; {og['account_count']} accounts</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                adf = pd.DataFrame(og["accounts"]).sort_values("sop_score", ascending=False)
                adf["SOP Grade"] = adf["sop_score"].apply(_letter_grade)
                adf.columns = ["Account", "SOP Score", "SOP Grade"]
                st.dataframe(adf, use_container_width=True, hide_index=True)

else:
    st.markdown(f"""
    <div style="text-align:center; padding:80px 20px;">
        <div style="font-size:48px; margin-bottom:12px; opacity:0.3;">📊</div>
        <p style="font-size:14px; color:{TEXT_DIM};">Drop a CSV or Excel file to analyze pipeline health</p>
    </div>""", unsafe_allow_html=True)
    with st.expander("Required Columns"):
        st.markdown("""
| Column | Purpose |
|---|---|
| Account Name | Groups records into pipelines |
| DevPhase / DevOutcome | Pipeline stage tracking |
| First Name / Last Name / Title | Contact quality |
| Direct Phone / Mobile | Phone coverage |
| Email | Contact quality |
| List Tag | Historical tier data (A, T, W, NI, I1 or 1, 2, 3) |
| Created Date | Pipeline age |
| Suspended Date | Suspension velocity |
| KDM Identified Date/Time | KDM rate |
| Next Call Date | Past due detection |
| Industry | Benchmark comparison |
| Primary List Source | Data origin |
| Delivery Owner | Owner grading |
| Sales Manager | Manager filtering |
        """)
