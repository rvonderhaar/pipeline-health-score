import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from benchmarks import INDUSTRY_BENCHMARKS, LIST_TAG_TIERS

TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def load_data(uploaded_file):
    """Load CSV or Excel file into a DataFrame."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file, dtype=str, encoding="utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, dtype=str, encoding="latin-1")
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file, dtype=str)
    else:
        raise ValueError("Unsupported file type. Upload a CSV or Excel file.")
    df.columns = df.columns.str.strip()
    return df


def _pct(count, total):
    return round(count / total * 100, 1) if total > 0 else 0.0


def _has_value(series):
    """Count non-blank, non-null values."""
    return series.fillna("").str.strip().ne("").sum()


def _is_bad_last_name(series):
    """Count last names that contain asterisks."""
    return series.fillna("").str.contains(r"\*", regex=True).sum()


def _parse_dates(series):
    """Parse a date column, coercing errors."""
    return pd.to_datetime(series, format="mixed", errors="coerce", dayfirst=False)


def _letter_grade(score):
    """Convert 0-100 score to letter grade."""
    if score >= 93:
        return "A"
    elif score >= 85:
        return "B+"
    elif score >= 77:
        return "B"
    elif score >= 70:
        return "B-"
    elif score >= 63:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 47:
        return "C-"
    elif score >= 40:
        return "D+"
    elif score >= 32:
        return "D"
    elif score >= 25:
        return "D-"
    else:
        return "F"


def _grade_color(grade):
    """Return a color for the grade."""
    if grade.startswith("A"):
        return "#2ecc71"
    elif grade.startswith("B"):
        return "#27ae60"
    elif grade.startswith("C"):
        return "#f39c12"
    elif grade.startswith("D"):
        return "#e67e22"
    else:
        return "#e74c3c"


def _compare_to_benchmark(actual_pct, benchmark_pct, higher_is_better=True):
    """Score 0-100 based on how actual compares to benchmark.
    At benchmark = 70 (meets expectations). Above = up to 100. Below = down to 0."""
    if benchmark_pct == 0:
        return 70.0  # no benchmark to compare against
    ratio = actual_pct / benchmark_pct if benchmark_pct > 0 else 1.0
    if higher_is_better:
        if ratio >= 1.2:
            return 100.0
        elif ratio >= 1.0:
            return 70.0 + (ratio - 1.0) * 150.0  # 70-100 range
        else:
            return max(0, ratio * 70.0)  # 0-70 range
    else:
        # For metrics where lower is better (e.g., bad last name %)
        if ratio <= 0.8:
            return 100.0
        elif ratio <= 1.0:
            return 70.0 + (1.0 - ratio) * 150.0
        else:
            return max(0, 70.0 - (ratio - 1.0) * 70.0)


def score_contact_quality(account_df, industry):
    """Score contact quality for an account's records against industry benchmarks."""
    bench = INDUSTRY_BENCHMARKS.get(industry)
    total = len(account_df)
    if total == 0:
        return {"score": 0, "grade": "F", "details": {}}

    # Calculate actual percentages
    first_name_count = _has_value(account_df.get("First Name", pd.Series(dtype=str)))
    bad_ln_count = _is_bad_last_name(account_df.get("Last Name", pd.Series(dtype=str)))
    title_count = _has_value(account_df.get("Title", pd.Series(dtype=str)))
    direct_count = _has_value(account_df.get("Direct Phone", pd.Series(dtype=str)))
    mobile_count = _has_value(account_df.get("Mobile", pd.Series(dtype=str)))

    direct_filled = account_df.get("Direct Phone", pd.Series(dtype=str)).fillna("").str.strip().ne("")
    mobile_filled = account_df.get("Mobile", pd.Series(dtype=str)).fillna("").str.strip().ne("")
    both_count = (direct_filled & mobile_filled).sum()
    either_count = (direct_filled | mobile_filled).sum()

    email_count = _has_value(account_df.get("Email", pd.Series(dtype=str)))

    actuals = {
        "first_name_pct": _pct(first_name_count, total),
        "bad_last_name_pct": _pct(bad_ln_count, total),
        "title_pct": _pct(title_count, total),
        "direct_phone_pct": _pct(direct_count, total),
        "mobile_pct": _pct(mobile_count, total),
        "both_phones_pct": _pct(both_count, total),
        "either_phone_pct": _pct(either_count, total),
        "email_pct": _pct(email_count, total),
    }

    if bench is None:
        bench = {
            "first_name_pct": 86, "bad_last_name_pct": 18, "title_pct": 86,
            "direct_phone_pct": 44, "mobile_pct": 43, "both_phones_pct": 24,
            "email_pct": 75, "tags_filled_pct": 44, "tier1_pct": 16, "suspension_pct": 36,
        }

    # Score each factor against benchmark
    name_score = _compare_to_benchmark(actuals["first_name_pct"], bench["first_name_pct"])
    bad_ln_score = _compare_to_benchmark(actuals["bad_last_name_pct"], bench["bad_last_name_pct"], higher_is_better=False)
    title_score = _compare_to_benchmark(actuals["title_pct"], bench["title_pct"])
    email_score = _compare_to_benchmark(actuals["email_pct"], bench["email_pct"])

    # Phone scoring: either phone is good (15%), both is best (additional 15%)
    # Benchmark "either" against avg of direct + mobile benchmarks
    either_bench = min(99, bench["direct_phone_pct"] + bench["mobile_pct"] - bench["both_phones_pct"])
    either_score = _compare_to_benchmark(actuals["either_phone_pct"], either_bench)
    both_score = _compare_to_benchmark(actuals["both_phones_pct"], bench["both_phones_pct"])

    # Weighted combination — names and phones are HIGH, email/title are lower
    weighted_score = (
        name_score * 0.25 +
        bad_ln_score * 0.10 +
        title_score * 0.05 +
        either_score * 0.15 +
        both_score * 0.15 +
        email_score * 0.05
    ) / 0.75  # normalize since list tags are scored separately

    # But cap at 0-100
    weighted_score = max(0, min(100, weighted_score))

    details = {
        "total_records": total,
        "first_name_count": int(first_name_count),
        "first_name_pct": actuals["first_name_pct"],
        "bad_last_name_count": int(bad_ln_count),
        "bad_last_name_pct": actuals["bad_last_name_pct"],
        "title_count": int(title_count),
        "title_pct": actuals["title_pct"],
        "direct_phone_count": int(direct_count),
        "direct_phone_pct": actuals["direct_phone_pct"],
        "mobile_count": int(mobile_count),
        "mobile_pct": actuals["mobile_pct"],
        "either_phone_count": int(either_count),
        "either_phone_pct": actuals["either_phone_pct"],
        "both_phones_count": int(both_count),
        "both_phones_pct": actuals["both_phones_pct"],
        "email_count": int(email_count),
        "email_pct": actuals["email_pct"],
        "benchmark_industry": industry if industry in INDUSTRY_BENCHMARKS else "Company Average",
    }

    return {"score": round(weighted_score, 1), "grade": _letter_grade(weighted_score), "details": details}


def score_list_tags(account_df, industry):
    """Score list tag quality against industry benchmark."""
    bench = INDUSTRY_BENCHMARKS.get(industry)
    total = len(account_df)
    if total == 0:
        return {"score": 0, "grade": "F", "details": {}}

    tags = account_df.get("List Tag", pd.Series(dtype=str)).fillna("").str.strip()
    filled = tags.ne("").sum()

    tier_counts = {1: 0, 2: 0, 3: 0, "untiered": 0}
    for tag_val in tags:
        if tag_val == "":
            continue
        tier = LIST_TAG_TIERS.get(tag_val)
        if tier:
            tier_counts[tier] += 1
        else:
            tier_counts["untiered"] += 1

    actuals = {
        "tags_filled_pct": _pct(filled, total),
        "tier1_pct": _pct(tier_counts[1], total),
        "tier2_pct": _pct(tier_counts[2], total),
        "tier3_pct": _pct(tier_counts[3], total),
    }

    if bench is None:
        bench = {"tags_filled_pct": 44, "tier1_pct": 16, "suspension_pct": 36}

    # If industry benchmark is 0% tags, don't penalize
    if bench["tags_filled_pct"] <= 1:
        tag_score = 70.0  # neutral — tags don't apply to this industry
    else:
        fill_score = _compare_to_benchmark(actuals["tags_filled_pct"], bench["tags_filled_pct"])
        tier1_score = _compare_to_benchmark(actuals["tier1_pct"], bench["tier1_pct"])
        tag_score = fill_score * 0.4 + tier1_score * 0.6

    tag_score = max(0, min(100, tag_score))

    # Tier 1 pipeline location breakdown
    tier1_mask = tags.isin(["A", "T", "1"])
    tier1_records = account_df[tier1_mask]
    tier1_by_phase = {}
    tier1_by_outcome = {}
    tier1_phase_outcome_detail = {}  # {phase: {outcome: count}} for hover
    if len(tier1_records) > 0:
        phases = tier1_records.get("DevPhase", pd.Series(dtype=str)).fillna("").str.strip()
        outcomes = tier1_records.get("DevOutcome", pd.Series(dtype=str)).fillna("").str.strip()
        tier1_by_phase = phases[phases != ""].value_counts().to_dict()
        tier1_by_outcome = outcomes[outcomes != ""].value_counts().to_dict()
        for phase in tier1_by_phase:
            phase_mask = phases == phase
            phase_outcomes = outcomes[phase_mask]
            tier1_phase_outcome_detail[phase] = phase_outcomes[phase_outcomes != ""].value_counts().to_dict()

    details = {
        "tags_filled": int(filled),
        "tags_filled_pct": actuals["tags_filled_pct"],
        "tier1_count": tier_counts[1],
        "tier1_pct": actuals["tier1_pct"],
        "tier2_count": tier_counts[2],
        "tier2_pct": actuals["tier2_pct"],
        "tier3_count": tier_counts[3],
        "tier3_pct": actuals["tier3_pct"],
        "benchmark_tags_pct": bench["tags_filled_pct"],
        "benchmark_tier1_pct": bench["tier1_pct"],
        "tier1_by_phase": tier1_by_phase,
        "tier1_by_outcome": tier1_by_outcome,
        "tier1_phase_outcome_detail": tier1_phase_outcome_detail,
    }

    return {"score": round(tag_score, 1), "grade": _letter_grade(tag_score), "details": details}


def score_sop_compliance(account_df):
    """Score SOP compliance: DevPhase distribution, KDM rate, past due calls."""
    total = len(account_df)
    if total == 0:
        return {"score": 0, "grade": "F", "details": {}}

    dev_phase = account_df.get("DevPhase", pd.Series(dtype=str)).fillna("").str.strip()
    dev_outcome = account_df.get("DevOutcome", pd.Series(dtype=str)).fillna("").str.strip()

    suspect_count = (dev_phase == "01 Suspect").sum()
    cleansing_count = (dev_phase == "02 Cleansing").sum()
    lead_count = (dev_phase == "03 Lead").sum()
    suspended_count = (dev_phase == "04 Suspended").sum()

    # Intro count and full DevOutcome breakdown within leads
    intro_count = (dev_outcome == "01 Intro").sum()

    # DevOutcome breakdown for 03 Lead
    lead_mask = dev_phase == "03 Lead"
    lead_outcomes = dev_outcome[lead_mask].value_counts().to_dict()
    # Ensure consistent ordering
    outcome_order = ["01 Intro", "03 No Interest", "02 Wait", "Info", "04 No Response", "Appt A"]
    lead_outcome_breakdown = {}
    for oc in outcome_order:
        if oc in lead_outcomes:
            lead_outcome_breakdown[oc] = int(lead_outcomes[oc])
    # Catch any others
    for oc, cnt in lead_outcomes.items():
        if oc not in lead_outcome_breakdown:
            lead_outcome_breakdown[oc] = int(cnt)

    # --- Suspect score (0-100): 100+ is ideal ---
    if suspect_count >= 100:
        suspect_score = 100.0
    elif suspect_count >= 50:
        suspect_score = 50.0 + (suspect_count - 50) * 1.0
    else:
        suspect_score = max(0, suspect_count * 1.0)

    # --- Cleansing score (0-100): under 100 is ideal, 150+ is red ---
    if cleansing_count <= 100:
        cleansing_score = 100.0
    elif cleansing_count <= 150:
        cleansing_score = 100.0 - (cleansing_count - 100) * 1.2
    elif cleansing_count <= 300:
        cleansing_score = 40.0 - (cleansing_count - 150) * 0.27
    else:
        cleansing_score = 0.0

    # --- Intro score (0-100): ~35 is ideal ---
    intro_diff = abs(intro_count - 35)
    if intro_diff <= 5:
        intro_score = 100.0
    elif intro_diff <= 15:
        intro_score = 100.0 - (intro_diff - 5) * 4.0
    elif intro_diff <= 30:
        intro_score = 60.0 - (intro_diff - 15) * 2.0
    else:
        intro_score = max(0, 30.0 - (intro_diff - 30) * 1.0)

    # --- Suspended velocity ---
    susp_dates = _parse_dates(account_df.get("Suspended Date", pd.Series(dtype=str)))
    susp_valid = susp_dates.dropna()
    if len(susp_valid) > 0:
        recent_30 = susp_valid[susp_valid >= (TODAY - timedelta(days=30))].count()
        recent_7 = susp_valid[susp_valid >= (TODAY - timedelta(days=7))].count()
        # Flag if more than 10% of total records suspended in last 30 days
        susp_velocity_pct = _pct(recent_30, total)
        if susp_velocity_pct <= 2:
            susp_score = 100.0
        elif susp_velocity_pct <= 5:
            susp_score = 70.0
        elif susp_velocity_pct <= 10:
            susp_score = 40.0
        else:
            susp_score = 10.0
    else:
        susp_score = 100.0
        recent_30 = 0
        recent_7 = 0
        susp_velocity_pct = 0

    # --- KDM Identification Rate ---
    kdm_dates = _parse_dates(account_df.get("KDM Identified Date/Time", pd.Series(dtype=str)))
    created_dates = _parse_dates(account_df.get("Created Date", pd.Series(dtype=str)))
    earliest_created = created_dates.min()

    if pd.notna(earliest_created):
        account_age_months = max(1, (TODAY - earliest_created).days / 30.44)
    else:
        account_age_months = 1

    # KDM target scales: 50/month for first year, then decreases
    if account_age_months <= 12:
        kdm_monthly_target = 50
    elif account_age_months <= 24:
        kdm_monthly_target = 35
    else:
        kdm_monthly_target = 20

    # KDMs in last 30 days
    kdm_valid = kdm_dates.dropna()
    kdm_last_30 = kdm_valid[kdm_valid >= (TODAY - timedelta(days=30))].count()

    if kdm_monthly_target > 0:
        kdm_ratio = kdm_last_30 / kdm_monthly_target
        if kdm_ratio >= 1.0:
            kdm_score = 100.0
        elif kdm_ratio >= 0.7:
            kdm_score = 60.0 + (kdm_ratio - 0.7) * 133.3
        elif kdm_ratio >= 0.4:
            kdm_score = 30.0 + (kdm_ratio - 0.4) * 100.0
        else:
            kdm_score = max(0, kdm_ratio * 75.0)
    else:
        kdm_score = 70.0

    # --- Past Due Next Call Dates ---
    active_outcomes = ["01 Intro", "02 Wait", "03 No Interest"]
    active_mask = dev_outcome.isin(active_outcomes)
    active_records = account_df[active_mask]
    active_count = len(active_records)

    if active_count > 0:
        next_call = _parse_dates(active_records.get("Next Call Date", pd.Series(dtype=str)))
        has_ncd = next_call.notna().sum()
        past_due = (next_call < TODAY).sum()
        past_due_pct = _pct(past_due, has_ncd) if has_ncd > 0 else 0

        # Severity: also count 7+ days past due
        severe_past_due = (next_call < (TODAY - timedelta(days=7))).sum()
        yellow_past_due = past_due - severe_past_due

        if past_due_pct <= 15:
            past_due_score = 100.0
        elif past_due_pct <= 30:
            past_due_score = 70.0
        elif past_due_pct <= 50:
            past_due_score = 40.0
        else:
            past_due_score = max(0, 20.0 - (past_due_pct - 50) * 0.4)
    else:
        past_due_score = 70.0  # no active records to judge
        past_due_pct = 0
        past_due = 0
        yellow_past_due = 0
        severe_past_due = 0
        has_ncd = 0

    # --- Weighted SOP score ---
    sop_score = (
        suspect_score * 0.20 +
        cleansing_score * 0.20 +
        intro_score * 0.20 +
        susp_score * 0.10 +
        kdm_score * 0.15 +
        past_due_score * 0.15
    )
    sop_score = max(0, min(100, sop_score))

    details = {
        "suspect_count": int(suspect_count),
        "suspect_score": round(suspect_score, 1),
        "cleansing_count": int(cleansing_count),
        "cleansing_score": round(cleansing_score, 1),
        "lead_count": int(lead_count),
        "lead_outcome_breakdown": lead_outcome_breakdown,
        "intro_count": int(intro_count),
        "intro_score": round(intro_score, 1),
        "suspended_count": int(suspended_count),
        "suspended_last_30": int(recent_30),
        "suspended_last_7": int(recent_7),
        "susp_velocity_pct": susp_velocity_pct,
        "susp_score": round(susp_score, 1),
        "account_age_months": round(account_age_months, 1),
        "account_age_years": int(account_age_months // 12),
        "account_age_remaining_months": int(account_age_months % 12),
        "kdm_monthly_target": kdm_monthly_target,
        "kdm_last_30": int(kdm_last_30),
        "kdm_score": round(kdm_score, 1),
        "active_lead_count": int(active_count),
        "past_due_count": int(past_due),
        "yellow_past_due": int(yellow_past_due),
        "severe_past_due": int(severe_past_due),
        "past_due_pct": past_due_pct,
        "past_due_score": round(past_due_score, 1),
    }

    return {"score": round(sop_score, 1), "grade": _letter_grade(sop_score), "details": details}


def score_list_source(account_df):
    """Get Primary List Source breakdown (informational, not scored)."""
    sources = account_df.get("Primary List Source", pd.Series(dtype=str)).fillna("(blank)").str.strip()
    sources = sources.replace("", "(blank)")
    breakdown = sources.value_counts().to_dict()
    total = len(account_df)
    pct_breakdown = {k: _pct(v, total) for k, v in breakdown.items()}
    return {"breakdown": breakdown, "pct_breakdown": pct_breakdown}


def score_pipeline(account_df, industry):
    """Calculate overall pipeline health score for one account."""
    contact = score_contact_quality(account_df, industry)
    tags = score_list_tags(account_df, industry)
    sop = score_sop_compliance(account_df)
    sources = score_list_source(account_df)

    # Overall score: SOP 40%, Contact Quality 25%, List Tags 25%, (sources informational)
    # Remaining 10% reserved for pipeline age
    created_dates = _parse_dates(account_df.get("Created Date", pd.Series(dtype=str)))
    earliest = created_dates.min()
    latest = created_dates.max()
    if pd.notna(earliest):
        age_days = (TODAY - earliest).days
        # Freshness: pipelines older than 12 months with few suspects get penalized
        suspect_count = sop["details"]["suspect_count"]
        if age_days > 365 and suspect_count < 100:
            age_score = max(0, 50 - (age_days - 365) / 30 * 5)
        elif age_days > 365:
            age_score = 60.0
        else:
            age_score = 80.0 + min(20, (365 - age_days) / 365 * 20)
    else:
        age_score = 50.0

    overall = (
        sop["score"] * 0.40 +
        contact["score"] * 0.25 +
        tags["score"] * 0.25 +
        age_score * 0.10
    )
    overall = max(0, min(100, overall))

    # Build flags
    flags = _build_flags(sop, contact, tags, age_score, account_df)

    # Average record age
    valid_created = created_dates.dropna()
    if len(valid_created) > 0:
        avg_age_days = (TODAY - valid_created).dt.days.mean()
        avg_age_years = int(avg_age_days // 365)
        avg_age_months = int((avg_age_days % 365) // 30)
        avg_age_str = f"{avg_age_years}y {avg_age_months}m" if avg_age_years > 0 else f"{avg_age_months}m"
    else:
        avg_age_days = 0
        avg_age_years = 0
        avg_age_months = 0
        avg_age_str = "N/A"

    return {
        "overall_score": round(overall, 1),
        "overall_grade": _letter_grade(overall),
        "sop": sop,
        "contact_quality": contact,
        "list_tags": tags,
        "list_sources": sources,
        "pipeline_age_score": round(age_score, 1),
        "avg_record_age": avg_age_str,
        "avg_record_age_days": avg_age_days,
        "earliest_created": earliest,
        "latest_created": latest,
        "flags": flags,
    }


def _build_flags(sop, contact, tags, age_score, account_df):
    """Generate human-readable flags for what needs attention."""
    flags = []
    d = sop["details"]

    # SOP flags
    if d["suspect_count"] < 100:
        flags.append(("RED", f"Suspects critically low: {d['suspect_count']} (need 100+)"))
    if d["cleansing_count"] >= 150:
        flags.append(("RED", f"Cleansing clogged: {d['cleansing_count']} records (target <100)"))
    elif d["cleansing_count"] >= 100:
        flags.append(("YELLOW", f"Cleansing elevated: {d['cleansing_count']} records (target <100)"))
    if d["intro_count"] < 20:
        flags.append(("RED", f"Intro pipeline drained: only {d['intro_count']} (target ~35)"))
    elif d["intro_count"] < 30:
        flags.append(("YELLOW", f"Intro pipeline low: {d['intro_count']} (target ~35)"))
    elif d["intro_count"] > 50:
        flags.append(("YELLOW", f"Intro pipeline high: {d['intro_count']} (target ~35)"))
    if d["susp_velocity_pct"] > 5:
        flags.append(("RED", f"High suspension velocity: {d['suspended_last_30']} records in last 30 days ({d['susp_velocity_pct']}%)"))
    if d["kdm_last_30"] < d["kdm_monthly_target"] * 0.5:
        flags.append(("RED", f"KDM identification critically low: {d['kdm_last_30']}/month (target: {d['kdm_monthly_target']})"))
    elif d["kdm_last_30"] < d["kdm_monthly_target"]:
        flags.append(("YELLOW", f"KDM identification below target: {d['kdm_last_30']}/month (target: {d['kdm_monthly_target']})"))
    if d["past_due_pct"] > 50:
        flags.append(("RED", f"Pipeline not being worked: {d['past_due_pct']}% of active leads past due ({d['severe_past_due']} severely)"))
    elif d["past_due_pct"] > 30:
        flags.append(("YELLOW", f"Past due calls building up: {d['past_due_pct']}% of active leads past due"))

    # Contact quality flags
    cd = contact["details"]
    if cd["bad_last_name_pct"] > 30:
        flags.append(("RED", f"Bad name data: {cd['bad_last_name_pct']}% have asterisk last names"))
    if cd["both_phones_pct"] < 15:
        flags.append(("YELLOW", f"Low phone coverage: only {cd['both_phones_pct']}% have both Direct & Mobile"))

    # Tag flags (only if industry expects tags)
    td = tags["details"]
    if td["benchmark_tags_pct"] > 5 and td["tags_filled_pct"] < td["benchmark_tags_pct"] * 0.5:
        flags.append(("YELLOW", f"List tags below industry norm: {td['tags_filled_pct']}% (industry avg: {td['benchmark_tags_pct']}%)"))

    # Age flag
    if age_score < 40:
        flags.append(("RED", "Pipeline is aging — consider injecting fresh Suspects"))

    return flags


def analyze_file(df):
    """Analyze an entire uploaded file. Returns per-account results and delivery owner rollup."""
    # Determine industry per account
    accounts = df.groupby("Account Name")
    results = {}

    for account_name, account_df in accounts:
        if not account_name or str(account_name).strip() == "":
            continue
        # Get the most common industry for this account
        industries = account_df.get("Industry", pd.Series(dtype=str)).fillna("").str.strip()
        industry_counts = industries[industries != ""].value_counts()
        industry = industry_counts.index[0] if len(industry_counts) > 0 else "Unknown"

        result = score_pipeline(account_df, industry)
        result["industry"] = industry
        result["record_count"] = len(account_df)

        # Get delivery owner
        owners = account_df.get("Delivery Owner", pd.Series(dtype=str)).fillna("").str.strip()
        owner_counts = owners[owners != ""].value_counts()
        result["delivery_owner"] = owner_counts.index[0] if len(owner_counts) > 0 else "Unknown"

        # Get sales manager
        managers = account_df.get("Sales Manager", pd.Series(dtype=str)).fillna("").str.strip()
        manager_counts = managers[managers != ""].value_counts()
        result["sales_manager"] = manager_counts.index[0] if len(manager_counts) > 0 else "Unknown"

        results[account_name] = result

    # Delivery Owner rollup
    owner_scores = {}
    for account_name, result in results.items():
        owner = result["delivery_owner"]
        if owner not in owner_scores:
            owner_scores[owner] = []
        owner_scores[owner].append({
            "account": account_name,
            "overall_score": result["overall_score"],
            "sop_score": result["sop"]["score"],
            "contact_score": result["contact_quality"]["score"],
            "tags_score": result["list_tags"]["score"],
        })

    owner_grades = {}
    for owner, accts in owner_scores.items():
        avg_overall = np.mean([a["overall_score"] for a in accts])
        avg_sop = np.mean([a["sop_score"] for a in accts])
        owner_grades[owner] = {
            "avg_overall_score": round(avg_overall, 1),
            "avg_overall_grade": _letter_grade(avg_overall),
            "avg_sop_score": round(avg_sop, 1),
            "avg_sop_grade": _letter_grade(avg_sop),
            "account_count": len(accts),
            "accounts": accts,
        }

    return results, owner_grades


def build_score_explanations(result):
    """Build hover-friendly explanations for every score in a result."""
    sop = result["sop"]["details"]
    cq = result["contact_quality"]["details"]
    lt = result["list_tags"]["details"]
    industry = result.get("industry", "Unknown")

    explanations = {}

    # Overall
    parts = []
    parts.append(f"SOP Compliance ({result['sop']['grade']}) weighted 40%")
    parts.append(f"Contact Quality ({result['contact_quality']['grade']}) weighted 25%")
    parts.append(f"List Tags ({result['list_tags']['grade']}) weighted 25%")
    parts.append(f"Pipeline Age weighted 10%")
    explanations["overall"] = " | ".join(parts)

    # SOP
    sop_parts = []
    sop_parts.append(f"Suspects: {sop['suspect_count']} (target 100+, score {sop['suspect_score']})")
    sop_parts.append(f"Cleansing: {sop['cleansing_count']} (target <100, score {sop['cleansing_score']})")
    sop_parts.append(f"Intros: {sop['intro_count']} (target ~35, score {sop['intro_score']})")
    sop_parts.append(f"Suspension velocity: score {sop['susp_score']}")
    sop_parts.append(f"KDM rate: {sop['kdm_last_30']}/{sop['kdm_monthly_target']} target (score {sop['kdm_score']})")
    sop_parts.append(f"Past due: {sop['past_due_pct']}% (score {sop['past_due_score']})")
    explanations["sop"] = " | ".join(sop_parts)

    # Contact Quality
    cq_parts = []
    cq_parts.append(f"Benchmarked vs {cq['benchmark_industry']}")
    cq_parts.append(f"Names: {cq['first_name_pct']}% filled, {cq['bad_last_name_pct']}% bad")
    cq_parts.append(f"Phones: {cq['both_phones_pct']}% have both, {cq['direct_phone_pct']}% direct, {cq['mobile_pct']}% mobile")
    cq_parts.append(f"Title: {cq['title_pct']}% | Email: {cq['email_pct']}%")
    explanations["contact"] = " | ".join(cq_parts)

    # List Tags
    lt_parts = []
    if lt["benchmark_tags_pct"] <= 1:
        lt_parts.append(f"Industry ({industry}) typically has no list tags — scored neutral")
    else:
        lt_parts.append(f"Tags filled: {lt['tags_filled_pct']}% (industry avg: {lt['benchmark_tags_pct']}%)")
        lt_parts.append(f"Tier 1: {lt['tier1_pct']}% (industry avg: {lt['benchmark_tier1_pct']}%)")
    explanations["tags"] = " | ".join(lt_parts)

    # Individual SOP metrics
    explanations["suspects"] = f"{sop['suspect_count']} suspects. Target is 100+. Below 100 means the pipeline is running out of fresh records to call."
    explanations["cleansing"] = f"{sop['cleansing_count']} in cleansing. Target is under 100, red flag at 150+. High count means records are stuck and not progressing to leads."
    explanations["intros"] = f"{sop['intro_count']} intros. Target is ~35. Too low = pipeline drained, too high = leads not being worked."
    explanations["suspended"] = f"{sop['suspended_count']} total suspended. {sop['suspended_last_30']} moved in last 30 days. Watching for velocity spikes."
    explanations["kdm"] = f"{sop['kdm_last_30']} KDMs identified in last 30 days vs target of {sop['kdm_monthly_target']}. Target scales based on account age ({sop['account_age_months']:.0f} months)."
    explanations["past_due"] = f"{sop['past_due_count']} past due calls ({sop['past_due_pct']}% of active leads). {sop['severe_past_due']} are 7+ days overdue."
    explanations["age"] = f"Average record age across pipeline. Older records may need fresh suspects injected."

    return explanations
