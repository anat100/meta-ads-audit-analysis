"""
Meta Ads audit — reproducible analysis of a 30-day Ads Manager export.

Applies the meta-ads-audit skill framework:
  Step 0  Data inventory
  Skill 1 Health check (manual items flagged)
  Skill 2 Conversion metric focus (split demo leads vs subcontractor signups)
  Skill 3 Campaign structure
  Skill 4 Ad set analysis (bid split + audience split rules)
  Skill 5 Pareto performance analysis (90% of spend)
  Skill 6 Creative analysis (hook rate / hold rate)

Usage:
    python analysis/audit.py                 # uses data/public_tender_company_meta_ads_export_30d_dummy.csv
    python analysis/audit.py path/to/export.csv

Outputs:
    output/*.csv   computed tables
    assets/*.png   charts used in the README
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "public_tender_company_meta_ads_export_30d_dummy.csv"
OUT = ROOT / "output"
ASSETS = ROOT / "assets"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

# --------------------------------------------------------------------------- style
INK = "#1B2A41"
MUTED = "#6B7785"
GRID = "#E6E9ED"
KEEP = "#0E9F8A"
WATCH = "#E3A21A"
PAUSE = "#D64545"
NEUTRAL = "#9AA5B1"
ACCENT = "#3B6FD8"
VERDICT_COLOR = {"Keep": KEEP, "Promote": ACCENT, "Watch": WATCH, "Pause": PAUSE, "Low data": NEUTRAL}

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"],
    "font.size": 11,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "axes.titlecolor": INK,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlepad": 30,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
})


def subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, color=MUTED, fontsize=10.5, va="bottom")


def footnote(fig, text="Source: Meta Ads Manager export, 17 Sep – 16 Oct 2026 (dummy data). Analysis: meta-ads-audit skill."):
    fig.text(0.01, -0.02, text, color=MUTED, fontsize=8.5, ha="left", va="top")


def eur(x, dec=0):
    return f"€{x:,.{dec}f}"


# --------------------------------------------------------------------------- load
raw = pd.read_csv(DATA)
cols = {
    "Campaign name": "campaign", "Ad set name": "adset", "Ad name": "ad", "Ad format": "format",
    "Bid strategy": "bid_strategy", "Bid amount": "bid_amount", "Ad set budget": "daily_budget",
    "Attribution setting": "attribution", "Amount spent (EUR)": "spend", "Impressions": "impressions",
    "Reach": "reach", "Frequency": "frequency", "CPM (cost per 1,000 impressions) (EUR)": "cpm",
    "Link clicks": "clicks", "CTR (link click-through rate)": "ctr_str", "Leads": "leads",
    "Landing page views": "lpv", "Video plays": "video_plays", "3-second video plays": "v3s",
    "ThruPlays": "thruplays", "Video average play time": "avg_play",
}
df = raw.rename(columns=cols)
df["ctr"] = df["ctr_str"].str.rstrip("%").astype(float)
df["camp"] = df["campaign"].str.replace("DACH | Leads | ", "", regex=False)
df["adset_short"] = df["adset"].str.replace(r"^(DE|AT\+CH|DE\+AT\+CH) \| ", r"\1 · ", regex=True)
df["ad_short"] = df["ad"].str.replace(r"^(VID|IMG|CAR) \| ", "", regex=True).str.replace(" | ", " · ", regex=False)
df["cpl"] = df["spend"] / df["leads"].replace(0, np.nan)
df["hook_rate"] = df["v3s"] / df["video_plays"] * 100
df["hold_rate"] = df["thruplays"] / df["v3s"] * 100
period_days = (pd.to_datetime(raw["Reporting ends"].iloc[0]) - pd.to_datetime(raw["Reporting starts"].iloc[0])).days + 1

# Skill 2: two conversion groups. The subcontractor signup is a free profile, not a demo request.
df["group"] = np.where(df["camp"].str.contains("Subcontractor"), "Subcontractor signups", "Demo leads")
demo = df[df["group"] == "Demo leads"].copy()


def agg(frame, by):
    g = frame.groupby(by, sort=False).agg(
        spend=("spend", "sum"), leads=("leads", "sum"), impressions=("impressions", "sum"),
        clicks=("clicks", "sum"), lpv=("lpv", "sum"), reach=("reach", "sum"),
        daily_budget=("daily_budget", "first"), bid_amount=("bid_amount", "first"),
        bid_strategy=("bid_strategy", "first"), ads=("ad", "count"),
    )
    g["cpl"] = g["spend"] / g["leads"].replace(0, np.nan)
    g["cpm"] = g["spend"] / g["impressions"] * 1000
    g["ctr"] = g["clicks"] / g["impressions"] * 100
    g["lpv_to_lead"] = g["leads"] / g["lpv"] * 100
    return g


# --------------------------------------------------------------------------- Skill 2: groups
groups = agg(df, "group")
groups.loc["Blended (misleading)"] = [
    df.spend.sum(), df.leads.sum(), df.impressions.sum(), df.clicks.sum(), df.lpv.sum(), df.reach.sum(),
    np.nan, np.nan, "", len(df), df.spend.sum() / df.leads.sum(), df.spend.sum() / df.impressions.sum() * 1000,
    df.clicks.sum() / df.impressions.sum() * 100, df.leads.sum() / df.lpv.sum() * 100,
]
groups.to_csv(OUT / "conversion_groups.csv")
DEMO_CPL = demo.spend.sum() / demo.leads.sum()

# --------------------------------------------------------------------------- campaigns
campaigns = agg(df, "camp").sort_values("spend", ascending=False)
campaigns["share_of_account"] = campaigns["spend"] / df.spend.sum() * 100
campaigns.to_csv(OUT / "campaigns.csv")

# --------------------------------------------------------------------------- Skill 4: ad sets
adsets = agg(df, ["camp", "adset_short"])
adsets["budget_utilization"] = adsets["spend"] / (adsets["daily_budget"] * period_days) * 100
adsets["campaign_share"] = adsets["spend"] / adsets.groupby(level=0)["spend"].transform("sum") * 100
ADSET_VERDICT = {
    "DE · Broad | Advantage+ Audience": "Keep",
    "AT+CH · Broad | Advantage+ Audience": "Watch",
    "DE · Broad | Bid Cap EUR 90": "Keep",
    "DE · Broad | Bid Cap EUR 60": "Low data",
    "DE · Broad | Bid Cap EUR 40": "Pause",
    "DE · Interest | General Contractors": "Watch",
    "DE · Interest | Project Developers & Real Estate": "Watch",
    "DE · Interest | Architects & Planners": "Pause",
    "DE+AT+CH · Website Visitors 30d + Video Viewers 50%": "Watch",
    "DE · Broad | Creative Test Sep": "Keep",
    "DE · Broad | Trades (Handwerk)": "Keep",
}
adsets["verdict"] = [ADSET_VERDICT.get(i[1], "Watch") for i in adsets.index]
adsets.to_csv(OUT / "adsets.csv")

# --------------------------------------------------------------------------- Skill 5: Pareto
p = demo.sort_values("spend", ascending=False).copy()
p["cum_spend_pct"] = p["spend"].cumsum() / p["spend"].sum() * 100
p["in_pareto"] = p["cum_spend_pct"] <= 90
pareto = p[p["in_pareto"]]
BENCH = {
    "cpm": pareto["cpm"].mean(),
    "ctr": pareto["ctr"].mean(),
    "cpl_pooled": pareto["spend"].sum() / pareto["leads"].sum(),
}
adset_cpl = demo.groupby("adset")["spend"].sum() / demo.groupby("adset")["leads"].sum()
top_ad_in_adset = demo.loc[demo.groupby("adset")["leads"].idxmax(), ["adset", "ad"]]
top_pairs = set(zip(top_ad_in_adset.adset, top_ad_in_adset.ad))


def ad_verdict(r):
    """Top Performer Protection + pause decision matrix from the skill."""
    if (r.adset, r.ad) in top_pairs:
        return "Keep" if r.leads > 0 else "Low data"
    a_cpl = adset_cpl[r.adset]
    if r.leads == 0 and r.spend > 2 * a_cpl:
        return "Pause"
    if r.leads >= 3 and r.cpl > 3 * a_cpl:
        return "Pause"
    if r.leads in (1, 2) or (r.leads >= 3 and r.cpl > 1.5 * a_cpl):
        return "Watch"
    if r.leads == 0:
        return "Low data"
    return "Keep"


p["verdict"] = p.apply(ad_verdict, axis=1)
# Ads living in an ad set that is recommended for pause follow the ad set.
p.loc[p["adset_short"] == "DE · Interest | Architects & Planners", "verdict"] = "Pause"
p.loc[p["adset_short"] == "DE · Broad | Bid Cap EUR 40", "verdict"] = "Pause"
p.loc[p["ad_short"].str.startswith("UGC"), "verdict"] = "Promote"
p.to_csv(OUT / "ads_demo_pareto.csv", index=False)

# --------------------------------------------------------------------------- Skill 6: creative
video = df[df["video_plays"].notna()].copy()
ACCOUNT_HOLD = video["thruplays"].sum() / video["v3s"].sum() * 100
creatives = demo.groupby("ad_short").agg(
    spend=("spend", "sum"), leads=("leads", "sum"), ad_sets=("adset", "nunique"), format=("format", "first"),
    plays=("video_plays", "sum"), v3s=("v3s", "sum"), thru=("thruplays", "sum"),
    clicks=("clicks", "sum"), impressions=("impressions", "sum"),
)
creatives["cpl"] = creatives["spend"] / creatives["leads"].replace(0, np.nan)
creatives["hook_rate"] = np.where(creatives.plays > 0, creatives.v3s / creatives.plays * 100, np.nan)
creatives["hold_rate"] = np.where(creatives.v3s > 0, creatives.thru / creatives.v3s * 100, np.nan)
creatives["ctr"] = creatives.clicks / creatives.impressions * 100
creatives = creatives.sort_values("spend", ascending=False)
creatives.to_csv(OUT / "creatives.csv")

# Flagged spend: everything recommended for pause.
flagged = p[p["verdict"] == "Pause"]
FLAG_SPEND, FLAG_LEADS = flagged.spend.sum(), flagged.leads.sum()
REST_CPL = (demo.spend.sum() - FLAG_SPEND) / (demo.leads.sum() - FLAG_LEADS)
flagged.to_csv(OUT / "flagged_spend.csv", index=False)

# =========================================================================== CHARTS

# 00 — scorecard -------------------------------------------------------------
fig = plt.figure(figsize=(13, 2.6))
tiles = [
    (eur(df.spend.sum()), "Total spend, 30 days", INK),
    (eur(DEMO_CPL), "Real cost per demo lead", PAUSE),
    (eur(groups.loc["Subcontractor signups", "cpl"], 2), "Cost per subcontractor\nsignup", KEEP),
    (eur(FLAG_SPEND), f"Flagged for pause\n({FLAG_SPEND / demo.spend.sum():.0%} of demo spend)", WATCH),
    (eur(creatives.loc["AI Price Assistant · Demo Walkthrough 30s", "cpl"]), "CPL of the best creative\n(across 5 ad sets)", ACCENT),
]
for i, (big, small, color) in enumerate(tiles):
    ax = fig.add_axes([0.01 + i * 0.198, 0.05, 0.185, 0.72])
    ax.set_axis_off()
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#F5F7F9", zorder=0))
    ax.add_patch(plt.Rectangle((0, 0), 0.025, 1, transform=ax.transAxes, color=color, zorder=1))
    ax.text(0.1, 0.52, big, fontsize=26, fontweight="bold", color=INK, transform=ax.transAxes)
    ax.text(0.1, 0.38, small, fontsize=10, color=MUTED, transform=ax.transAxes, va="top")
fig.text(0.01, 0.97, "Public Tender Company Meta Ads — 30-day audit at a glance", fontsize=16, fontweight="bold", color=INK, va="top")
footnote(fig)
fig.savefig(ASSETS / "00_scorecard.png")
plt.close(fig)

# 01 — lead-type split -------------------------------------------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.3, 1]})
g = groups.loc[["Demo leads", "Subcontractor signups"]]
for i, (metric, label) in enumerate([("spend", "Share of spend"), ("leads", "Share of leads")]):
    shares = g[metric] / g[metric].sum() * 100
    left = 0
    for name, color in [("Demo leads", INK), ("Subcontractor signups", KEEP)]:
        a1.barh(i, shares[name], left=left, color=color, height=0.55)
        a1.text(left + shares[name] / 2, i, f"{shares[name]:.0f}%", ha="center", va="center",
                color="white", fontweight="bold", fontsize=12)
        left += shares[name]
a1.set_yticks([0, 1], ["Share of spend", "Share of leads"])
a1.invert_yaxis()
a1.set_xlim(0, 100)
a1.xaxis.set_major_formatter(mtick.PercentFormatter())
a1.grid(axis="y", visible=False)
a1.set_title("Two different leads hide in one 'Leads' column")
subtitle(a1, "Subcontractor signups are 8% of spend but two thirds of all leads")
a1.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=INK), plt.Rectangle((0, 0), 1, 1, color=KEEP)],
          labels=["Demo leads (buyers)", "Subcontractor signups (free profiles)"],
          loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)

vals = [groups.loc["Blended (misleading)", "cpl"], DEMO_CPL, groups.loc["Subcontractor signups", "cpl"]]
labels = ["Blended\n(account view)", "Demo leads", "Subcontractor\nsignups"]
bars = a2.bar(labels, vals, color=[NEUTRAL, INK, KEEP], width=0.6)
for b, v in zip(bars, vals):
    a2.text(b.get_x() + b.get_width() / 2, v + 3, eur(v, 2 if v < 10 else 0), ha="center", fontweight="bold", color=INK)
a2.set_ylabel("Cost per lead (€)")
a2.set_ylim(0, max(vals) * 1.2)
a2.grid(axis="x", visible=False)
a2.set_title("Real demo CPL is 2.8× the blended number")
subtitle(a2, "Blending makes demo leads look far cheaper than they are")
footnote(fig)
fig.tight_layout(w_pad=4)
fig.savefig(ASSETS / "01_lead_type_split.png")
plt.close(fig)

# 02 — CPL by ad set ---------------------------------------------------------
a = adsets.reset_index()
a = a[a["camp"] != "Subcontractor Network Signup"].copy()
a["label"] = a["camp"].str.split(" \\| ").str[0] + " — " + a["adset_short"].str.replace(r"^\S+ · ", "", regex=True)
a.loc[a.adset_short.str.startswith("AT+CH"), "label"] = "Primary — AT+CH Advantage+"
a.loc[a.adset_short.str.startswith("DE · Broad | Advantage"), "label"] = "Primary — DE Advantage+"
a["label"] = a["label"].str.replace("Broad | ", "", regex=False).str.replace("Interest | ", "", regex=False)
a["plot_cpl"] = a["cpl"].fillna(0)
a = a.sort_values("plot_cpl", ascending=True)
CAP = 420
fig, ax = plt.subplots(figsize=(12, 6.4))
y = np.arange(len(a))
colors = [VERDICT_COLOR[v] for v in a["verdict"]]
ax.barh(y, a["plot_cpl"].clip(upper=CAP), color=colors, height=0.62)
for yi, (_, r) in zip(y, a.iterrows()):
    if np.isnan(r.cpl):
        ax.text(4, yi, f"no leads · {eur(r.spend)} spent", va="center", color=MUTED, fontsize=10)
        continue
    txt = f"{eur(r.cpl)}   ({int(r.leads)} leads · {eur(r.spend)})"
    x = min(r.cpl, CAP)
    if r.cpl > CAP:
        ax.text(CAP - 6, yi, f"{eur(r.cpl)} ▸", va="center", ha="right", color="white", fontweight="bold")
        ax.text(CAP + 6, yi, f"({int(r.leads)} leads · {eur(r.spend)})", va="center", color=INK, fontsize=10)
    else:
        ax.text(x + 6, yi, txt, va="center", color=INK, fontsize=10, bbox=dict(fc="white", ec="none", pad=1))
ax.axvline(DEMO_CPL, color=INK, ls="--", lw=1)
ax.text(DEMO_CPL + 3, len(a) - 0.35, f"Demo average {eur(DEMO_CPL)}", color=INK, fontsize=9.5)
ax.set_yticks(y, a["label"])
ax.set_xlim(0, CAP + 140)
ax.set_xlabel("Cost per demo lead (€)")
ax.grid(axis="y", visible=False)
ax.set_title("Broad Germany wins; interest targeting and AT+CH cost 2–10× more")
subtitle(ax, "Cost per demo lead by ad set, colored by audit verdict (bar for Architects capped at €420)")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in [KEEP, WATCH, PAUSE, NEUTRAL]],
          labels=["Keep", "Watch", "Pause", "Too little data"], loc="lower right", frameon=False)
footnote(fig)
fig.savefig(ASSETS / "02_cpl_by_adset.png")
plt.close(fig)

# 03 — concentration curve ---------------------------------------------------
c = demo.sort_values("cpl", na_position="last").copy()
c["cum_spend"] = c.spend.cumsum() / c.spend.sum() * 100
c["cum_leads"] = c.leads.cumsum() / c.leads.sum() * 100
xs = np.r_[0, c.cum_spend.values]
ys = np.r_[0, c.cum_leads.values]
best4 = c.head(4)
s4, l4 = best4.cum_spend.iloc[-1], best4.cum_leads.iloc[-1]
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.plot([0, 100], [0, 100], color=NEUTRAL, ls="--", lw=1)
ax.text(70, 64, "if every ad converted equally", color=MUTED, fontsize=9.5, rotation=31)
ax.fill_between(xs, ys, xs, color=ACCENT, alpha=0.08)
ax.plot(xs, ys, color=ACCENT, lw=2.6, marker="o", ms=4)
ax.scatter([s4], [l4], s=90, color=KEEP, zorder=5)
ax.annotate(f"The 4 cheapest ads: {s4:.0f}% of spend → {l4:.0f}% of demo leads",
            (s4, l4), xytext=(3, 90), color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
zero = c[c.leads == 0]
z_start = 100 - zero.spend.sum() / c.spend.sum() * 100
ax.axvspan(z_start, 100, color=PAUSE, alpha=0.08)
ax.text((z_start + 100) / 2, 8, f"{len(zero)} ads, {eur(zero.spend.sum())}\nzero leads",
        ha="center", color=PAUSE, fontsize=9.5, fontweight="bold")
ax.set_xlim(0, 100); ax.set_ylim(0, 103)
ax.xaxis.set_major_formatter(mtick.PercentFormatter()); ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlabel("Cumulative share of demo spend (ads sorted cheapest CPL first)")
ax.set_ylabel("Cumulative share of demo leads")
ax.set_title("Demo leads are concentrated in a handful of ads")
subtitle(ax, f"{len(c)} demo ads across 5 campaigns, last 30 days")
footnote(fig)
fig.savefig(ASSETS / "03_lead_concentration.png")
plt.close(fig)

# 04 — waste map --------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7))
xmax = 3400
for cpl_line, lab in [(60, "€60 CPL"), (DEMO_CPL, f"{eur(DEMO_CPL)} avg"), (300, "€300 CPL")]:
    xx = np.linspace(0, xmax, 50)
    ax.plot(xx, xx / cpl_line, color=NEUTRAL, lw=0.9, ls=":")
    xe = min(xmax * 0.97, 55 * cpl_line)
    ax.text(xe, xe / cpl_line + 1, lab, color=MUTED, fontsize=9, ha="right")
for v in ["Keep", "Promote", "Watch", "Pause", "Low data"]:
    s = p[p.verdict == v]
    if s.empty:
        continue
    ax.scatter(s.spend, s.leads, s=110, color=VERDICT_COLOR[v], alpha=0.9, edgecolor="white", lw=1.2,
               label={"Low data": "Too little data"}.get(v, v), zorder=3)
callouts = {
    ("VID | AI Price Assistant | Demo Walkthrough 30s", "DE | Broad | Advantage+ Audience"): (-30, 0, "right", "Demo Walkthrough (Primary DE)"),
    ("VID | Founder POV | 'Tendering in 2 hours'", "DE | Broad | Advantage+ Audience"): (12, 4, "left", "Founder POV (Primary DE)"),
    ("VID | Customer Story | Generalunternehmer 45s", "DE | Broad | Advantage+ Audience"): (14, 12, "left", "Customer Story 45s — €412 CPL"),
    ("VID | Founder POV | 'Tendering in 2 hours'", "DE | Interest | Architects & Planners"): (8, -17, "left", "Founder POV in Architects — €645"),
    ("IMG | 250k Bidders Network | Stat", "AT+CH | Broad | Advantage+ Audience"): (10, -17, "left", "250k Stat AT+CH — 0 leads"),
    ("VID | UGC | Bauleiter Reaction 20s", "DE | Broad | Creative Test Sep"): (10, 4, "left", "UGC Bauleiter (test) — €60 CPL"),
}
for (ad, adset), (dx, dy, ha, lab) in callouts.items():
    r = p[(p.ad == ad) & (p.adset == adset)].iloc[0]
    ax.annotate(lab, (r.spend, r.leads), xytext=(dx, dy), textcoords="offset points", ha=ha,
                fontsize=9.5, color=INK)
ax.set_xlim(0, xmax); ax.set_ylim(-4, 58)
ax.set_xlabel("Spend, 30 days (€)"); ax.set_ylabel("Demo leads")
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("€{x:,.0f}"))
ax.set_title("Where the demo budget lands: spend vs. leads per ad")
subtitle(ax, "Above the dotted average line = cheaper than €134 per lead. Bottom-right = money without leads.")
ax.legend(frameon=False, loc="upper left", title="Audit verdict", title_fontsize=10)
footnote(fig)
fig.savefig(ASSETS / "04_waste_map.png")
plt.close(fig)

# 05 — hook vs hold -----------------------------------------------------------
vd = video.copy()
vd = vd[vd.spend >= 100]
fig, ax = plt.subplots(figsize=(12, 7))
ax.axvspan(0, 25, color=PAUSE, alpha=0.06)
ax.axvspan(40, 60, color=KEEP, alpha=0.06)
ax.axhline(ACCOUNT_HOLD, color=INK, ls="--", lw=1)
ax.axhline(ACCOUNT_HOLD * 1.25, color=KEEP, ls=":", lw=1)
ax.text(59.5, ACCOUNT_HOLD + 0.4, f"Account avg hold {ACCOUNT_HOLD:.1f}%", ha="right", color=INK, fontsize=9)
ax.text(59.5, ACCOUNT_HOLD * 1.25 + 0.4, "Good hold (avg +25%)", ha="right", color=KEEP, fontsize=9)
ax.text(12.5, 33.3, "Poor hook <25%", ha="center", color=PAUSE, fontsize=9.5, fontweight="bold")
ax.text(50, 33.3, "Good hook ≥40%", ha="center", color=KEEP, fontsize=9.5, fontweight="bold")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("cpl", [KEEP, WATCH, PAUSE])
norm = matplotlib.colors.Normalize(vmin=50, vmax=450)
cpl_c = vd.cpl.fillna(500).clip(upper=450)
sc = ax.scatter(vd.hook_rate, vd.hold_rate, s=vd.spend / 6, c=cpl_c, cmap=cmap, norm=norm,
                edgecolor="white", lw=1.2, alpha=0.9, zorder=3)
named = {}
for _, r in vd.iterrows():
    key = r.ad_short.split(" · ")[0]
    named.setdefault(key, []).append(r)
arrow_labels = [
    ("Demo Walkthrough 30s (5 ad sets)", (44, 24), (29, 27.5)),
    ("Founder POV (4 ad sets)", (41, 21), (28, 23.5)),
    ("Subcontractor signup video", (47, 26), (48.5, 30)),
    ("UGC Bauleiter Reaction 20s", (52, 15), (47, 11.5)),
    ("Motion · AI Error Check 15s", (23, 31), (27, 32.3)),
    ("Customer Story 45s", (18, 9), (26, 7)),
    ("Webinar Clip 60s", (19, 12), (26, 13.5)),
]
for text, xy, xyt in arrow_labels:
    ax.annotate(text, xy, xytext=xyt, fontsize=9.5, color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkB=6))
cb = fig.colorbar(sc, ax=ax, pad=0.01, shrink=0.8)
cb.set_label("Cost per lead (€, ≥€450 or no leads = red)", color=MUTED)
cb.outline.set_visible(False)
ax.set_xlim(10, 60); ax.set_ylim(5, 34)
ax.xaxis.set_major_formatter(mtick.PercentFormatter()); ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlabel("Hook rate: 3-second plays ÷ video plays")
ax.set_ylabel("Hold rate: ThruPlays ÷ 3-second plays")
ax.set_title("The hook decides the CPL: every video under 25% hook converts poorly")
subtitle(ax, "Each bubble = one video ad in one ad set; bubble size = spend")
footnote(fig)
fig.savefig(ASSETS / "05_creative_hook_hold.png")
plt.close(fig)

# 06 — creative leaderboard ---------------------------------------------------
cr = creatives.copy()
cr["plot_cpl"] = cr.cpl.fillna(0)
cr = cr.sort_values("plot_cpl", ascending=False)
cr = pd.concat([cr[cr.cpl.isna()], cr[cr.cpl.notna()]])
fig, ax = plt.subplots(figsize=(12, 6.6))
y = np.arange(len(cr))
fmt_color = {"Video": ACCENT, "Image": INK, "Carousel": NEUTRAL}
ax.barh(y, cr.plot_cpl.clip(upper=420), color=[fmt_color[f] for f in cr["format"]], height=0.62)
for yi, (name, r) in zip(y, cr.iterrows()):
    if np.isnan(r.cpl):
        ax.text(4, yi, f"no leads · {eur(r.spend)} spent", va="center", color=PAUSE, fontsize=10, fontweight="bold")
    else:
        ax.text(min(r.cpl, 420) + 6, yi, f"{eur(r.cpl)}   {int(r.leads)} leads · {eur(r.spend)} · {r.ad_sets} ad set{'s' if r.ad_sets > 1 else ''}",
                va="center", color=INK, fontsize=10)
ax.axvline(DEMO_CPL, color=INK, ls="--", lw=1)
ax.set_yticks(y, cr.index)
ax.set_xlim(0, 640)
ax.set_xlabel("Cost per demo lead (€), all ad sets combined")
ax.grid(axis="y", visible=False)
ax.set_title("Creative leaderboard: two videos carry the account")
subtitle(ax, "Same creative pooled across every ad set it runs in. Dashed line = demo average €134.")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=fmt_color[k]) for k in fmt_color], labels=list(fmt_color),
          frameon=False, loc="upper right")
footnote(fig)
fig.savefig(ASSETS / "06_creative_leaderboard.png")
plt.close(fig)

# 07 — bid cap ladder ---------------------------------------------------------
bc = adsets.loc["Bid Cap Split"].copy()
bc = bc.loc[["DE · Broad | Bid Cap EUR 40", "DE · Broad | Bid Cap EUR 60", "DE · Broad | Bid Cap EUR 90"]]
ref = adsets.loc[("Primary | GC & Developers", "DE · Broad | Advantage+ Audience")]
labels = ["Bid cap €40", "Bid cap €60", "Bid cap €90", "Primary DE\n(no cap)"]
util = list(bc.budget_utilization) + [ref.budget_utilization]
cpls = list(bc.cpl) + [ref.cpl]
leads = list(bc.leads) + [ref.leads]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.8))
cols_ = [PAUSE, NEUTRAL, KEEP, ACCENT]
b = a1.bar(labels, util, color=cols_, width=0.6)
for bi, v in zip(b, util):
    a1.text(bi.get_x() + bi.get_width() / 2, v + 2, f"{v:.0f}%", ha="center", fontweight="bold", color=INK)
a1.axhline(85, color=INK, ls="--", lw=1); a1.text(-0.45, 87, "85% target", ha="left", fontsize=9, color=INK)
a1.set_ylim(0, 110); a1.yaxis.set_major_formatter(mtick.PercentFormatter())
a1.set_title("Lower caps barely spend"); subtitle(a1, "Budget utilization, 30 days")
a1.grid(axis="x", visible=False)
b = a2.bar(labels, [0 if np.isnan(v) else v for v in cpls], color=cols_, width=0.6)
for bi, v, l in zip(b, cpls, leads):
    t = "no leads" if np.isnan(v) else f"{eur(v)}\n{int(l)} leads"
    a2.text(bi.get_x() + bi.get_width() / 2, (0 if np.isnan(v) else v) + 4, t, ha="center", color=INK, fontsize=10)
a2.set_ylim(0, 140); a2.set_ylabel("Cost per lead (€)")
a2.set_title("…and capping doesn't beat no cap"); subtitle(a2, "Cost per demo lead")
a2.grid(axis="x", visible=False)
footnote(fig)
fig.tight_layout(w_pad=4)
fig.savefig(ASSETS / "07_bid_cap_ladder.png")
plt.close(fig)

# 08 — broad vs interest ------------------------------------------------------
def pool(frame):
    return pd.Series({"cpm": frame.spend.sum() / frame.impressions.sum() * 1000,
                      "ctr": frame.clicks.sum() / frame.impressions.sum() * 100,
                      "cpl": frame.spend.sum() / frame.leads.sum()})
broad = pool(demo[demo.adset.str.contains("DE \\| Broad")])
interest = pool(demo[demo.adset.str.contains("Interest")])
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
for ax, (m, title, f) in zip(axes, [("cpm", "CPM", lambda v: eur(v, 2)), ("ctr", "CTR (link)", lambda v: f"{v:.2f}%"),
                                     ("cpl", "Cost per demo lead", lambda v: eur(v))]):
    vals = [broad[m], interest[m]]
    bb = ax.bar(["Broad DE", "Interest DE"], vals, color=[KEEP, WATCH], width=0.55)
    for bi, v in zip(bb, vals):
        ax.text(bi.get_x() + bi.get_width() / 2, v * 1.02, f(v), ha="center", fontweight="bold", color=INK)
    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_title(title, fontsize=13, pad=10)
    ax.grid(axis="x", visible=False)
fig.suptitle("Interest targeting pays more per view and costs 2.5× more per lead", x=0.01, ha="left",
             fontsize=15, fontweight="bold", color=INK, y=1.08)
fig.text(0.01, 0.955, "Broad = all DE Broad ad sets (Primary, Bid Cap, Testing); Interest = the three role ad sets",
         color=MUTED, fontsize=10.5)
footnote(fig)
fig.tight_layout(w_pad=3)
fig.savefig(ASSETS / "08_broad_vs_interest.png")
plt.close(fig)

# 09 — flagged spend ----------------------------------------------------------
fl = flagged.copy()
fl["name"] = fl.ad_short + "\n" + fl.adset_short.str.replace(r"^\S+ · ", "", regex=True)
fl = fl.sort_values("spend")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw={"width_ratios": [1.5, 1]})
y = np.arange(len(fl))
a1.barh(y, fl.spend, color=PAUSE, height=0.6)
for yi, (_, r) in zip(y, fl.iterrows()):
    a1.text(r.spend + 25, yi, f"{eur(r.spend)} · {int(r.leads)} lead{'s' if r.leads != 1 else ''}", va="center", color=INK, fontsize=10)
a1.set_yticks(y, fl.name, fontsize=9)
a1.set_xlim(0, fl.spend.max() * 1.45)
a1.xaxis.set_major_formatter(mtick.StrMethodFormatter("€{x:,.0f}"))
a1.grid(axis="y", visible=False)
a1.set_title(f"{eur(FLAG_SPEND)} flagged for pause → {int(FLAG_LEADS)} leads")
subtitle(a1, f"Ads recommended for pause (incl. ads inside paused ad sets). CPL {eur(FLAG_SPEND / FLAG_LEADS)}.")
bars = a2.bar(["Demo CPL today", "Demo CPL on the\nremaining spend"], [DEMO_CPL, REST_CPL], color=[NEUTRAL, KEEP], width=0.55)
for bi, v in zip(bars, [DEMO_CPL, REST_CPL]):
    a2.text(bi.get_x() + bi.get_width() / 2, v + 3, eur(v), ha="center", fontweight="bold", color=INK, fontsize=13)
a2.set_ylim(0, 165); a2.set_ylabel("Cost per demo lead (€)")
a2.grid(axis="x", visible=False)
a2.set_title("What the rest of the account delivers")
subtitle(a2, "Illustrative, not a forecast: freed budget won't convert at this rate automatically")
footnote(fig)
fig.tight_layout(w_pad=4)
fig.savefig(ASSETS / "09_flagged_spend.png")
plt.close(fig)

# 10 — funnel by campaign -----------------------------------------------------
fc = campaigns.copy()
fc["click_to_lpv"] = fc.lpv / fc.clicks * 100
order = ["Subcontractor Network Signup", "Retargeting | Website 30d", "Bid Cap Split", "Primary | GC & Developers",
         "Audience Split | Roles", "Testing | Creative"]
fc = fc.loc[order]
fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
for ax, (m, t, f) in zip(axes, [("ctr", "Link CTR", "{:.2f}%"), ("click_to_lpv", "Click → landing page view", "{:.0f}%"),
                               ("lpv_to_lead", "Landing page view → lead", "{:.1f}%")]):
    colors = [KEEP if i == 0 else INK for i in range(len(fc))]
    ax.barh(range(len(fc)), fc[m], color=colors, height=0.6)
    for i, v in enumerate(fc[m]):
        ax.text(v * 1.02, i, f.format(v), va="center", color=INK, fontsize=10)
    ax.set_xlim(0, fc[m].max() * 1.3)
    ax.set_title(t, fontsize=13, pad=10)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
axes[0].xaxis.set_major_locator(mtick.MultipleLocator(0.5))
axes[0].xaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
axes[2].xaxis.set_major_locator(mtick.MultipleLocator(3))
axes[0].set_yticks(range(len(fc)), fc.index)
axes[0].invert_yaxis()
fig.suptitle("The demo funnel breaks on the landing page, not in the feed", x=0.01, ha="left",
             fontsize=15, fontweight="bold", color=INK, y=1.08)
fig.text(0.01, 0.955, "Demo campaigns convert 1.1–2.8% of landing-page visitors; the free signup converts 11%",
         color=MUTED, fontsize=10.5)
footnote(fig)
fig.tight_layout(w_pad=2)
fig.savefig(ASSETS / "10_funnel_by_campaign.png")
plt.close(fig)

# --------------------------------------------------------------------------- console summary
print(f"Period: {period_days} days | rows: {len(df)} | spend {eur(df.spend.sum())} | leads {df.leads.sum()}")
print(groups[["spend", "leads", "cpl"]].round(2).to_string())
print(f"\nPareto set: {len(pareto)} ads | avg CPM {BENCH['cpm']:.2f} | avg CTR {BENCH['ctr']:.2f}% | pooled CPL {BENCH['cpl_pooled']:.2f}")
print(f"Account hold rate (30d): {ACCOUNT_HOLD:.1f}%")
print(f"Flagged spend {eur(FLAG_SPEND)} -> {FLAG_LEADS} leads | demo CPL {DEMO_CPL:.0f} -> rest {REST_CPL:.0f}")
print(f"Broad vs interest: {broad.round(2).to_dict()} | {interest.round(2).to_dict()}")
print(f"4 cheapest ads: {s4:.1f}% spend -> {l4:.1f}% leads | zero-lead ads: {len(zero)}, {zero.spend.sum():.0f}")
print("\nVerdicts:\n", p[["camp", "adset_short", "ad_short", "spend", "leads", "cpl", "verdict"]].round(1).to_string())
