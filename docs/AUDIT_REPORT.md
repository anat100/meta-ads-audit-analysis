# Full audit report — Public Tender Company Meta Ads, 17 Sep – 16 Oct 2026

The real cost of a demo lead is **€134**, not the €48 the account shows. About **€4,800 of demo spend (19%) bought 6 leads** and can be paused. The next gain sits on the landing page, not in the feed.

*Dummy data. Method: `meta-ads-audit` skill. Every figure is reproduced by `analysis/audit.py`.*

---

## Step 0 — Data inventory

The source is an ad-level Ads Manager CSV: 30 active ads, 6 campaigns, EUR, with bid strategy, bid amount, ad set budget, attribution and video columns. That's enough for performance, bid-split and video analysis.

| Missing signal | Effect |
|---|---|
| EMQ score | Manual check in Events Manager |
| Audience-segment breakdown | Separate export needed |
| Placement / age breakdowns | Separate export needed |
| Daily rows | Can't detect creative fatigue; all verdicts use 30-day totals |
| Targeting setup | Audiences inferred from ad set names |

## Skill 1 — Health check

- **EMQ:** check Events Manager → Pixel → Lead → Event Match Quality. Below 8.5, fix tracking first.
- **Audience segments:** not in the file, so setup can't be confirmed.
- **Attribution:** every ad set uses 7-day click or 1-day view. View-through credit matters most for Retargeting.

## Skill 2 — Conversion metric

| Group | Spend | Leads | CPL |
|---|---|---|---|
| Demo leads (5 campaigns) | €25,140 | 188 | **€134** |
| Subcontractor signups | €2,100 | 376 | **€5.59** |
| Blended (misleading) | €27,240 | 564 | €48 |

The main metric for every judgment below is **cost per demo lead**, with €134 as the reference.

## Skill 3 — Campaign structure

- **Primary vs Testing:** Primary takes 48% of demo spend and Testing 9% with 5 ads. No Testing winner has been moved into Primary.
- **Bid limit split:** DE Broad with bid caps of €90, €60 and €40.
- **Audience split:** three role-based interest ad sets on a €110 cost-per-result goal.
- **Retargeting:** website visitors 30d + 50% video viewers, kept out of the comparison.
- **Overlap risk:** Primary DE, the Bid Cap Split and Testing all target broad Germany and likely bid against each other.

## Skill 4 — Ad set analysis

| Ad set | Spend | Share of campaign | Budget used | CPM | CPL | Verdict |
|---|---|---|---|---|---|---|
| Primary · DE Advantage+ | €9,320 | 77% | 89% | €15.4 | **€95** | Keep |
| Primary · AT+CH Advantage+ | €2,820 | 23% | 78% | €19.0 | €217 | Watch |
| Bid cap €90 | €2,410 | 79% | 54% | €16.0 | €105 | Keep, underspending |
| Bid cap €60 | €600 | 20% | 13% | €15.5 | €100 (6 leads) | Too little data |
| Bid cap €40 | €50 | 2% | 1% | €14.9 | no leads | Turn off |
| Interest · General Contractors | €2,020 | 34% | 67% | €20.9 | €168 | Watch |
| Interest · Project Developers | €1,980 | 33% | 66% | €26.4 | €220 | Watch |
| Interest · Architects & Planners | €2,000 | 33% | 67% | €24.4 | **€1,000** | **Pause** |
| Retargeting 30d | €1,790 | 100% | 99% | €38.9 | €179 | Replace weak creative |
| Testing · Creative Test Sep | €2,150 | 100% | 90% | €14.0 | €143 | Promote winner |
| Subcontractor · Trades | €2,100 | 100% | **100%** | €8.6 | €5.59 | Limited by budget |

**Bid Cap Split.** The €40 cap sits far below what a demo lead costs, so it barely delivers. Turn it off rather than raise it, since raising it would duplicate the €60 ad set. The €90 cap converts well but uses only 54% of its budget. Raising it to about €100 lets it spend more. Even so, capping (€105) doesn't beat uncapped Primary DE (€95).

**Audience Split.** All three ad sets miss the €110 goal by 50–800%. The goal holds delivery back (67% of budget used) without bringing CPL close to it. Interest CPM is about €24 vs €15 for broad. Architects & Planners is the clear loser.

## Skill 5 — Pareto analysis (19 ads = 90% of demo spend)

Benchmarks across those 19 ads: CPM €21.1, CTR 0.93%, pooled CPL €129.

| Ad (ad set) | Spend | CPM | CTR | Leads | CPL | Verdict |
|---|---|---|---|---|---|---|
| Demo Walkthrough 30s (Primary DE) | €3,120 | €14.8 | 1.32% | 52 | €60 | Keep, make variations |
| Founder POV (Primary DE) | €2,410 | €15.6 | 1.18% | 30 | €80 | Keep |
| Demo Walkthrough 30s (Bid €90) | €1,720 | €16.4 | 1.12% | 20 | €86 | Keep (top ad in ad set) |
| Customer Story 45s (Primary DE) | €1,650 | €17.1 | 0.95% | 4 | €412 | **Pause** |
| Demo Walkthrough 30s (AT+CH) | €1,490 | €19.4 | 1.05% | 11 | €135 | Keep (top ad in ad set) |
| Founder POV (Project Developers) | €1,450 | €26.9 | 0.97% | 7 | €207 | Keep (top ad in ad set) |
| Founder POV (General Contractors) | €1,380 | €21.3 | 1.02% | 10 | €138 | Keep (top ad in ad set) |
| Founder POV (Architects) | €1,290 | €24.8 | 0.71% | 2 | €645 | Goes with ad set pause |
| 250k Bidders Stat (Primary DE) | €1,180 | €13.9 | 0.88% | 8 | €148 | Watch |
| Feature Tour Carousel (Primary DE) | €960 | €16.2 | 0.74% | 4 | €240 | Watch |
| Last Chance Slots (Retargeting) | €780 | €38.5 | 1.22% | 7 | €111 | Keep (top ad in ad set) |
| 250k Bidders Stat (AT+CH) | €720 | €18.2 | 0.66% | 0 | — | **Pause** |
| 250k Bidders Stat (Architects) | €710 | €23.6 | 0.52% | 0 | — | Goes with ad set pause |
| Book a Demo UI (Bid €90) | €690 | €15.2 | 0.79% | 3 | €230 | Watch |
| 250k Bidders Stat (General Contractors) | €640 | €20.1 | 0.84% | 2 | €320 | Watch |
| Book a Demo UI (AT+CH) | €610 | €18.9 | 0.71% | 2 | €305 | Watch |
| Customer Story 45s (Retargeting) | €590 | €41.2 | 0.69% | 1 | €590 | Watch, replace |
| UGC Bauleiter Reaction 20s (Testing) | €540 | €13.1 | 1.41% | 9 | €60 | **Promote** |
| Testimonial Projektentwickler (Project Developers) | €530 | €25.2 | 0.89% | 2 | €265 | Watch |

Why each pause qualifies under the skill's matrix:
- **Customer Story 45s (Primary DE):** CPL 4.3× the ad set average, with 4 leads. It's not the top ad in its ad set.
- **250k Bidders Stat (AT+CH):** zero leads on €720, more than 2× the ad set's €217 CPL.
- **Webinar Clip 60s (Testing),** just outside the 90% group: zero leads on €380, more than 2× the ad set's €143 CPL.

**Pattern:** the Demo Walkthrough video brings in 88 leads at €77 across 5 ad sets. The 250k Bidders Stat image brings in 10 leads at €325 across 4.

## Skill 6 — Creative analysis

The benchmark is the 30-day account hold rate of 21.6%; no 90-day data was available.

| Video | Hook | Hold | CTR | Scenario | Action |
|---|---|---|---|---|---|
| Demo Walkthrough 30s | 42–45% | 22–24% | 1.05–1.32% | Working | Variations: new hooks on the same body, a 15s cut, copy versions |
| Founder POV | 37–41% | 17–21% | 0.71–1.18% | Working in broad | Keep. Average watch time is 0:03 in Primary DE vs 0:06–0:09 elsewhere; check it's the same file |
| UGC Bauleiter Reaction 20s | 52% | 15% | 1.41% | Strong hook, weak hold, still converting | Promote, then test a tighter middle section |
| Motion · AI Error Check 15s | 23% | 31% | 0.92% | Poor hook, best hold | New hook on the same body |
| Customer Story 45s | 18–21% | 9–11% | 0.69–0.95% | Scenario 3 | Rebuild: open with the outcome or a number |
| Webinar Clip 60s | 19% | 12% | 0.58% | Scenario 3 | Pause |

Judging copy and visuals needs the creative files themselves; numbers alone give the framework, not the full diagnosis.

## Other signals

- **Retargeting costs more than prospecting:** €179 vs €95, with frequency of 7–8 on a pool of about 6,000. Part of the pool is prospecting video viewers, so pausing prospecting video shrinks retargeting within 1–2 weeks. With 1-day view attribution, retargeting leads may be over-credited.
- **AT+CH costs 2.3× more per lead than DE.** Look at it again once a country breakdown is available.
- **Landing-page conversion:** demo traffic converts 1.7% of landing-page views into leads; the free signup converts 11%. That's the largest lever outside the ad account.

## Open questions

1. Confirm that subcontractor signups and demo requests are different lead types, and give a target CPL for each.
2. How many demo leads become qualified opportunities, by campaign?
3. EMQ score for the Lead event.
