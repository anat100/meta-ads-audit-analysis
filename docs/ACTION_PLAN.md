# Action plan — what to change, in what order

Everything here is applied **manually in Ads Manager**. Work top to bottom. Each step is safe to do on its own.

## This week — stop the waste

- [ ] **Pause ad set:** `DACH | Leads | Audience Split | Roles` → `DE | Interest | Architects & Planners`
  - Why: €2,000 for 2 demo leads (€1,000 CPL), 7.5× the demo average.
  - Note: spend stops immediately. Leave the other two interest ad sets as they are.
- [ ] **Pause ad:** `VID | Customer Story | Generalunternehmer 45s` in `Primary | GC & Developers` → `DE | Broad | Advantage+ Audience`
  - Why: €1,650 for 4 leads (€412), 4.3× the ad set average, and not the top ad in the ad set.
- [ ] **Pause ad:** `IMG | 250k Bidders Network | Stat` in `Primary` → `AT+CH | Broad | Advantage+ Audience`
  - Why: €720 with zero leads, more than 2× the ad set's CPL.
- [ ] **Pause ad:** `VID | Webinar Clip | Kostencontrolling 60s` in `Testing | Creative`
  - Why: €380 with zero leads, and a 19% hook rate.
- [ ] **Turn off ad set:** `Bid Cap Split` → `DE | Broad | Bid Cap EUR 40`
  - Why: 1% of budget spent in 30 days; the cap is below what a demo lead costs.

## This week — back the winner

- [ ] **Add** `VID | UGC | Bauleiter Reaction 20s` to `Primary` → `DE | Broad | Advantage+ Audience` (keep it in Testing too)
  - Why: €60 CPL, 52% hook, 1.41% CTR, the best test result.
  - Note: a new ad can briefly put the ad set back into learning. Judge it after 7 days, not 48 hours.

## Optional, needs a decision

- [ ] **Raise bid cap** on `Bid Cap EUR 90` to about €100
  - Why: €105 CPL but only 54% of budget spent.
  - Warning: changing the bid amount may reset learning.
- [ ] **Subcontractor campaign: daily budget €70 → €84 (+20%)**, *only if* signup quality is confirmed
  - Review after 7 days. Roll back if CPL rises above about €7. Cap spend at €84/day.

## Next two weeks — creative briefs

1. **Demo Walkthrough 30s:** 3 new hooks on the same body, plus a 15s cut.
2. **Motion · AI Error Check:** keep the body (31% hold, the best in the account) and replace the first 3 seconds, for example with the UGC reaction-style opening.
3. **Customer Story:** full rebuild. Open with a concrete customer outcome (a number or time saved) and put the customer on screen in second 1.
4. **Retargeting:** replace `Customer Story 45s` (€590 CPL) with a demo-led cut or the integrations angle.

## Outside Meta — the biggest lever

- [ ] **Landing-page test for demo traffic.** Demo campaigns convert 1.7% of landing-page views; the free signup converts 11%. Ideas: fewer form fields, a calendar picker shown above the fold, proof from the public tender company's bidder network right next to the CTA.

## Data to pull for the next audit

| Export | Unlocks |
|---|---|
| Same ad-level export, **by day** | Creative-fatigue detection; last 7 days vs the 7 before |
| **Audience-segment** breakdown | How much demo spend reaches people who already know the public tender company |
| **Placement** and **country** breakdown | Whether AT+CH or Reels/Stories drive the cost gap |
| **Events Manager → EMQ** for Lead | Whether tracking can be trusted |
| CRM: demo lead → qualified opportunity, by campaign | Judging campaigns on pipeline, not on raw leads |

## Not doing (and why)

- **Scaling Primary DE:** already at 89% of budget, and there's no daily or segment data to confirm it can take more.
- **Building lookalike audiences:** the skill never recommends them.
- **Moving budget "to an ad", a placement or an age group:** those aren't real controls. Only campaign or ad set budgets, bid caps and on/off are.
