# How the `meta-ads-audit` skill works

`meta-ads-audit` is a Claude skill: a packaged set of instructions that makes Claude audit a Meta Ads account the way a senior media buyer would. It is adapted from GoMarble's open paid-media skill set. Its value isn't that it knows Meta Ads Manager. Its value is that it runs **the same checks in the same order every time**, applies **fixed numeric thresholds**, and refuses to make **recommendations that would damage a working account**.

It is **read-and-recommend only**. Claude never touches the ad account. Every recommendation is written so a person can find the exact field in Ads Manager and apply it themselves.

---

## Where the data can come from

| Source | How complete | What breaks |
|---|---|---|
| Connected MCP / Meta API | Full | Nothing |
| **Ads Manager CSV export** (used here) | Most rules work | Targeting setup, optimization event, EMQ and breakdowns aren't in the file |
| Screenshots | Spot checks only | Most rules |
| Pasted numbers | Last resort | Treated as unverified |

Every run starts with a **data inventory** (Step 0). Claude states what the data supports, what's missing, and whether each gap blocks a rule, lowers confidence, or simply doesn't apply.

---

## The six steps

```
Step 0  Data inventory      → what can and can't be judged from this source
Skill 1 Health check        → is tracking trustworthy? (EMQ ≥ 8.5, audience segments set up)
Skill 2 Conversion metric   → what does "good" mean? (ROAS vs CPL vs cost per result)
Skill 3 Campaign structure  → which comparisons are valid? (primary/testing, bid split, audience split)
Skill 4 Ad set analysis     → which ad sets earn their budget? (budget use, campaign share, CPL)
Skill 5 Pareto analysis     → which ads drive 90% of spend, and what to keep / pause / test
Skill 6 Creative analysis   → why a video works or doesn't (hook rate, hold rate, CTR scenarios)
```

### Skill 1 — Health check
Bad tracking makes every later step pointless. The skill asks for the **Event Match Quality** score of the main conversion event (manual, from Events Manager). If it's below 8.5, fixing the pixel comes before anything else. It also checks whether **audience segments** (New / Engaged / Existing) are set up, so you can see how much spend goes to people who already know you.

### Skill 2 — Conversion metric
The skill decides the account type from the **actual optimization event**, never from campaign names, and sets one main metric:

| Event | Account type | Main metric |
|---|---|---|
| Purchase | Ecommerce | Purchase ROAS |
| Lead | Lead gen | Cost per lead |
| Complete registration | Registration | Cost per registration |
| Custom | Custom | Cost per result for that event |

**Mixed accounts are split into groups, never averaged.** That rule produced this audit's biggest finding. The public tender company's "Leads" column holds both demo requests (€134 each) and free subcontractor signups (€5.59). Blended, they look like €48.

### Skill 3 — Campaign structure
Different structures need different comparisons. The skill matches the account against four patterns:
- **Primary vs Testing:** a small testing campaign with many ads feeds a large primary campaign.
- **Bid limit split:** same audience, different bid caps.
- **Audience split:** same setup, different audiences.
- **Custom:** anything else, explained by looking at the creatives.

Retargeting is labelled and kept out of the comparison.

### Skill 4 — Ad set analysis
- **Budget utilization** = spend ÷ (daily budget × days). Below 85% means delivery is restricted.
- **Campaign spend share** must be **≥ 25%** before two ad sets are compared. Smaller ones are too noisy.
- **Bid-split rules:** if an ad set barely spends under a cap, ease the cap. A clear winner justifies pausing the loser. A high CPM is fine as long as the CPL is good.
- **Audience-split rules:** a clear winner justifies pausing the loser. An ad set with good CPL that underspends needs a wider audience. Lookalike audiences are never suggested.

### Skill 5 — Pareto analysis
Sort ads by spend and keep those that make up the first **90%**. Averages from that group (CPM, CTR, CPL) become the benchmarks. Each ad is then diagnosed:

| Profile | Diagnosis | Action |
|---|---|---|
| CPM ≥ 30% above average and CPL ≥ 30% worse | Expensive audience, not converting | Pause or retarget |
| CTR ≥ 30% below average and CPL worse | Not resonating | Check comments, then test a stronger CTA |
| Good numbers, falling trend | Creative fatigue | New variations, not budget |
| Good numbers, stable | Working | Make variations |

### Skill 6 — Creative analysis
- **Hook rate** = 3-second plays ÷ video plays. Good is 40% or more; poor is below 25%.
- **Hold rate** = ThruPlays ÷ 3-second plays. Compared to the account average; good is average +25%.
- **CTR:** good is 1.25% or more; poor is below 0.65%.

| Scenario | Profile | Fix |
|---|---|---|
| 1 | Good hook, poor hold | Keep the opening, rebuild from second 3 onward |
| 2 | Everything average | Fix the hook first, then the body |
| 3 | Poor hook | Rebuild the opening completely; nothing else matters yet |
| 4 | Great hook and hold, poor CTR | Strengthen the CTA and match it to the landing page |

---

## The guardrails (the part that protects the account)

These run before **every** recommendation:

- **Top Performer Protection.** The ad with the most conversions in an ad set is never recommended for pause, whatever share of budget it takes. Meta concentrating spend on a winner is the algorithm working.
- **Pause decision matrix.** Pause only if (a) zero conversions **and** spend above 2× the ad set's CPL, or (b) 3 or more conversions **and** CPL above 3× the ad set average. One or two conversions means *watch*. Ads younger than 7 days mean *watch*.
- **Only three budget levers exist:** campaign or ad set budget, bid caps or cost caps, and turning things on or off. "Shift budget to this ad, placement or age group" is not a real action and gets rewritten.
- **Scaling limits:** no more than **+20%** at once, only with the target met, and always with a review window and a spend cap.
- **Minimum signal:** 3–5 conversions per ad set per week before judging performance.
- **Learning-phase warnings:** any bid strategy, bid amount or significant targeting change is flagged as a possible reset.
- **Consistent method:** once a metric and benchmark are set in a conversation, they don't change unless the user asks.

---

## How it ran on this account

| Step | Result here |
|---|---|
| Data inventory | Ad-level CSV with bid, budget, attribution and video columns. Missing: daily rows, breakdowns, targeting, EMQ |
| Health check | EMQ and segments flagged as manual checks |
| Conversion metric | **Split into demo leads (€134) and subcontractor signups (€5.59)** |
| Structure | Primary vs Testing + Bid limit split + Audience split + Retargeting; overlap risk on broad Germany |
| Ad sets | Architects & Planners paused; €40 bid cap off; €90 bid cap underspending |
| Pareto | 19 ads make up 90% of demo spend; 3 ads paused under the matrix; UGC test promoted |
| Creative | Hook rate separates winners from losers; Motion = great body, weak hook |

The skill file itself lives in your Claude skills list as `meta-ads-audit`. Run it with `/meta-ads-audit` and attach an export.
