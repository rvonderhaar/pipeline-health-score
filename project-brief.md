# Pipeline Health Score — Project Brief

## Company Overview
- **Business model:** Outbound sales agency for small-to-medium businesses
- **Primary channel:** Cold calling
- **Team structure:**
  - **SDRs** (cold callers) — each has ~5 accounts
  - **POAs** (ops team) — each supports ~150 accounts
- **Service:** Call on behalf of clients into their ICPs, set appointments
  - Example: Bob owns a roofing company → we cold call his metro → set appointments for him
- **Monthly cycle:** Guarantee clients a certain number of appointments/month
- **Company goal:** 90% fulfillment rate (set 90% of guaranteed appointments)

## POA Responsibilities
- Supply leads for SDRs to call
- Analyze and prioritize best leads to push toward 90% fulfillment
- Each account typically has 2,000+ records
- ~150 accounts per POA = massive volume, currently very manual process

## CRM: Salesforce
- **Account objects** = Client pages
- **Contact records** = Leads tied to accounts

## Contact Classification (DevPhases / DevOutcomes)

### DevPhase → DevOutcome Hierarchy
- **01 Suspect** — Fresh, never called
- **02 Cleansing** — Called, no KDM identified yet. After 8 dials with no KDM → Suspended (Cleansing Max Reached)
- **03 Lead** — Contains the following DevOutcomes:
  - **01 Intro** — KDM identified, not yet spoken to. After 10 dials with no contact → 04 No Response
  - **No Interest** — Spoke to KDM, not interested
  - **02 Lead Wait** — Spoke to KDM, interested but not ready. Very hot, high close rate
  - **Lead Info** — Spoke to KDM, wanted info not a meeting. Auto-emails triggered
  - **04 No Response** — KDM identified but never reached
  - **Appt A** — KDM agreed to meet with client
- **04 Suspended** — Removed from pipeline (Not a Fit, Cleansing Max Reached, Research Dead End, etc.)

## SOP — Ideal Pipeline Counts

| Phase / Outcome | Ideal State | Flag Condition |
|---|---|---|
| **01 Suspect** | 100+ records | Flag if drops **below 100** (pipeline running dry) |
| **02 Cleansing** | Under 100 | Flag at **150+** (clogged — records not progressing) |
| **01 Intro** (in 03 Lead) | ~35 records | Flag if drifts **too far above or below 35** |
| **04 Suspended** | Count doesn't matter | Flag if records move into Suspended **too quickly** (may indicate poor lead quality or rep mismanagement) |

**Why this matters:** Too many records in a phase = clogged pipeline (records stuck, not progressing). Too few = drained pipeline (not enough fuel to generate appointments).

### KDM Identification Rate
- **First-year accounts:** Should identify ~50 KDMs per month (tracked via KDM Identified Date/Time field)
- **Mature accounts (1+ year):** KDM target decreases as the lead pipeline is already built up — exact threshold scales down based on pipeline age (derived from Created Dates)
- Flag if KDM identification rate falls significantly below target for the account's age

### Past Due Next Call Dates
For records in DevOutcomes **02 Wait**, **01 Intro**, and **03 No Interest** — the Next Call Date should not be past due. Past due records mean the pipeline is not being worked.

| Severity | Condition |
|---|---|
| **Yellow** | 1–7 days past due |
| **Red** | 7+ days past due |

Flag accounts with high percentages of past-due records. Company-wide average is ~40% past due — anything above that is a concern, but the goal is to drive this down across the board.

## List Tag Tiers (Internal Historical Data Reuse)
When reusing internal data for different clients, records are tagged based on their previous DevOutcome:

| List Tag Code | DevOutcome | Tier |
|---|---|---|
| A | Appt A / Appt Rescheduled | Tier 1 |
| T | 07 TOC Open | Tier 1 |
| W | 02 Wait | Tier 2 |
| NI | 03 No Interest | Tier 2 |
| I1 | 01 Intro / Intro 2 / Intro 3 | Tier 3 |
| NR | 04 No Response | Untiered (no points) |
| I | Info | Untiered (no points) |
| (blank) | Was Suspect/Cleansing in previous pipeline | No tier (no points) |

## Scoring Factors & Weighting (Relative Priority)

**All contact quality and list tag benchmarks are evaluated per-industry, not company-wide.**
Accounts are compared against their industry peers. Exclude "Abstrakt" from all benchmarks (data quality anomaly).

### 1. List Tag Tier — HIGH weight
- Tier 1 (Appt A, Appt Rescheduled, 07 TOC Open) → highest points
- Tier 2 (02 Wait, 03 No Interest) → medium points
- Tier 3 (01 Intro, 01 Intro 2, 01 Intro 3) → lower points
- Records with historical success data are among the strongest indicators of pipeline quality
- **Note:** Some industries naturally have 0% list tags (Mortgage, etc.) — absence of tags is NOT a penalty for those industries

### 2. Contact Name — HIGH weight
- **Full Name** = First Name filled + real Last Name (not asterisks) → high points
- **Bad Name** = Blank First Name, asterisks in Last Name, or both → penalty / no points
- **Title** = Bonus if filled, but a record with Full Name + no Title is still considered decent
- Salesforce requires Last Name field, so missing names show as blank First / asterisk Last

### 3. Phone Numbers — HIGH weight
- **Both Direct Phone AND Mobile Phone filled** → best score, highest contact rate
- **One of the two filled** → good, still ranks high
- **Neither filled** → significant penalty
- Must be full phone numbers (not partial)

### 4. Email & LinkedIn — LOW weight
- Email filled → small bonus
- LinkedIn Profile URL filled → small bonus
- Nice to have, not critical to score

### 5. Pipeline Composition (DevPhase/Outcome Distribution) — HIGH weight
- Evaluated against SOP thresholds (see SOP section above)
- Suspect, Cleansing, Intro counts vs. ideal targets
- Suspended velocity tracking
- KDM identification rate (see SOP section)
- Past due Next Call Dates for 02 Wait / 01 Intro / 03 No Interest (see SOP section)

### 6. Primary List Source — INFORMATIONAL
- Breakdown of record sources (Internal Salesforce, ZoomInfo, Hoovers, Client Provided, etc.)
- Not directly scored, but provides context on data origin and expected quality patterns

## Industry Benchmarks (from 773K record analysis, excluding Abstrakt)

| Industry | Records | FirstNm% | BadLN% | Title% | DirPh% | Mob% | Both% | Email% | Tags% | Tier1% | Susp% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Audio Visual | 653 | 73 | 30 | 73 | 38 | 35 | 17 | 67 | 37 | 6 | 29 |
| Commercial Cleaning | 35,229 | 85 | 20 | 86 | 45 | 41 | 24 | 77 | 56 | 25 | 34 |
| Commercial Electric | 5,305 | 90 | 14 | 90 | 51 | 57 | 35 | 84 | 71 | 26 | 20 |
| Commercial Fire Protection | 8,651 | 94 | 10 | 94 | 55 | 52 | 33 | 87 | 67 | 32 | 24 |
| Commercial Flooring | 5,255 | 91 | 11 | 91 | 55 | 50 | 32 | 88 | 79 | 36 | 25 |
| Commercial Roofing | 165,127 | 84 | 22 | 84 | 43 | 38 | 23 | 73 | 44 | 14 | 47 |
| Concrete/Asphalt Services | 22,253 | 82 | 21 | 83 | 44 | 43 | 25 | 73 | 54 | 21 | 28 |
| Construction | 53,831 | 88 | 16 | 89 | 46 | 44 | 26 | 79 | 54 | 19 | 34 |
| Copy/Print | 2,088 | 71 | 31 | 71 | 32 | 37 | 17 | 61 | 30 | 13 | 26 |
| EV Charging Stations | 1,410 | 64 | 38 | 60 | 35 | 45 | 17 | 46 | 12 | 6 | 17 |
| Elevators | 3,095 | 92 | 13 | 93 | 45 | 46 | 23 | 84 | 36 | 11 | 52 |
| HVAC | 139,075 | 82 | 21 | 82 | 42 | 42 | 25 | 70 | 36 | 13 | 35 |
| IT/Cyber Security/MSP | 105,016 | 87 | 16 | 87 | 44 | 39 | 21 | 78 | 41 | 11 | 37 |
| LED Lighting | 10,491 | 95 | 10 | 95 | 56 | 45 | 30 | 86 | 51 | 20 | 58 |
| Landscape Services | 5,577 | 94 | 9 | 94 | 57 | 50 | 33 | 88 | 79 | 47 | 24 |
| Material Handling | 276 | 64 | 37 | 63 | 47 | 35 | 27 | 63 | 59 | 49 | 10 |
| Mortgage - LO Recruitment | 2,744 | 100 | 0 | 93 | 26 | 54 | 22 | 97 | 0 | 0 | 13 |
| Mortgage - Realtor Referral | 2,701 | 100 | 0 | 27 | 0 | 99 | 0 | 100 | 1 | 0 | 2 |
| Other | 14,795 | 92 | 13 | 92 | 50 | 35 | 19 | 81 | 37 | 16 | 65 |
| Other (Non-Local) | 138,502 | 88 | 14 | 87 | 42 | 46 | 25 | 74 | 38 | 13 | 27 |
| Painting | 17,119 | 85 | 19 | 86 | 46 | 45 | 26 | 77 | 50 | 17 | 31 |
| Physical Security | 14,944 | 89 | 14 | 89 | 45 | 47 | 26 | 81 | 58 | 25 | 31 |
| Power Washing | 1,251 | 98 | 8 | 99 | 59 | 46 | 31 | 86 | 60 | 22 | 24 |
| Solar | 16,858 | 92 | 12 | 92 | 55 | 52 | 34 | 86 | 65 | 30 | 39 |

**How to read:** An account's metrics are compared against its industry row. Above the benchmark = good. Below = needs attention.

## Project Goal — Three Core Functions

### 1. Pipeline Health Grading
Score each account's pipeline based on DevPhase/DevOutcome distribution, contact info completeness (names, phones), and List Tag Tier mix. Flag pipelines that are set up wrong or poorly managed before they lead to missed fulfillment.

### 2. List Quality Analysis
When a new lead list is built for an account, evaluate whether the data quality (contact info, proper tagging) is strong enough to support a healthy pipeline.

### 3. Pipeline Age Tracking
Calculate the average age of records in a pipeline to surface when an account needs fresh Suspects injected.

### The Payoff
Upload an Excel file → immediately see which pipelines need help and **why** (bad data, stale records, wrong DevPhase mix, missing contact info, etc.). Replaces the current manual process of digging through spreadsheets across 150 accounts.

---

*Status: Initial brief — more details incoming*
