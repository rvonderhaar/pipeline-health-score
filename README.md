# Pipeline Health Score

Automated pipeline analysis and health grading tool for outbound sales operations. Upload a pipeline export and instantly see which accounts need attention — and why.

## What It Does

- **Scores every account's pipeline** on a letter-grade scale (A through F) based on SOP compliance, contact quality, and historical list tag data
- **Flags problems automatically** — clogged cleansing, low suspects, past-due calls, bad contact data, KDM identification gaps
- **Benchmarks against industry peers** — each account is compared to its own industry's averages across 24 industries
- **Grades Delivery Owners** on their accounts' average SOP compliance
- **Filters by Sales Manager** to scope the view to one manager's book of business

## Scoring Breakdown

| Component | Weight | What It Measures |
|---|---|---|
| SOP Compliance | 40% | Pipeline distribution (Suspect/Cleansing/Intro counts), KDM identification rate, past-due calls, suspension velocity |
| Contact Quality | 25% | Name completeness, phone coverage (any phone + both phones), title, email — vs industry benchmark |
| List Tags | 25% | Historical tier data (Tier 1/2/3) fill rate — vs industry benchmark |
| Pipeline Age | 10% | Average record age, fresh suspect availability |

## App Layout

**Dashboard** — Overview metrics, sortable score distribution chart, category breakdown by SOP/Contact/Tags

**Account Details** — Select individual accounts or filter by Delivery Owner. Each account shows: overall grade, flags, SOP metrics with pipeline funnel chart, contact quality details, list tag breakdown with Tier 1 pipeline location, and primary list source table

**Delivery Owner Grades** — Ranked by average SOP Compliance score with drill-down to individual accounts

## Required Input Columns

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
| KDM Identified Date/Time | KDM identification rate |
| Next Call Date | Past-due detection |
| Industry | Determines benchmark comparison |
| Primary List Source | Data origin breakdown |
| Delivery Owner | Owner grading |
| Sales Manager | Sidebar filtering |

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
