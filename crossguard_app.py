"""
CrossGuard — Tokenized Treasury Cross-Chain Router
FNCE313 · Group 2, Team 5 · Singapore Management University

Run with:
    pip install streamlit plotly pandas
    streamlit run crossguard_app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CrossGuard — Tokenized Treasury Router",
    page_icon="⛓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c12;
    color: #e8edf5;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }

/* ── METRIC CARDS ── */
div[data-testid="metric-container"] {
    background: #0e1420;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] label {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #5a6a82 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
}

/* ── SELECTBOX & INPUTS ── */
div[data-baseweb="select"] > div {
    background-color: #141c2b !important;
    border-color: rgba(255,255,255,0.07) !important;
    color: #e8edf5 !important;
    border-radius: 8px !important;
}
div[data-baseweb="input"] > div {
    background-color: #141c2b !important;
    border-color: rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
}
input { color: #e8edf5 !important; }

/* ── BUTTON ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1e8fff, #0057b8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 14px 32px !important;
    width: 100% !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(30,143,255,0.35) !important;
}

/* ── DATAFRAME ── */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.stDataFrame { background: #0e1420 !important; }

/* ── DIVIDER ── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 2rem 0; }

/* ── TABS ── */
button[data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #5a6a82 !important;
    background: transparent !important;
    border: none !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1e8fff !important;
    border-bottom: 2px solid #1e8fff !important;
}

/* ── EXPANDER ── */
div[data-testid="stExpander"] {
    background: #0e1420;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

/* ── LABELS ── */
label[data-testid="stWidgetLabel"] p {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #5a6a82 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────

CHAINS = ["Ethereum", "Avalanche", "Solana", "Polygon", "Base"]

# Latency in minutes: {route: [CCIP, LayerZero, Wormhole]}
LATENCY = {
    ("Ethereum",  "Avalanche"): [22, 4, 8],
    ("Ethereum",  "Solana"):    [25, 6, 12],
    ("Ethereum",  "Polygon"):   [18, 3, 6],
    ("Ethereum",  "Base"):      [20, 3, 7],
    ("Avalanche", "Ethereum"):  [22, 4, 8],
    ("Avalanche", "Solana"):    [28, 7, 13],
    ("Avalanche", "Polygon"):   [24, 5, 9],
    ("Avalanche", "Base"):      [26, 5, 10],
    ("Solana",    "Ethereum"):  [25, 6, 12],
    ("Solana",    "Avalanche"): [28, 7, 13],
    ("Solana",    "Polygon"):   [27, 6, 11],
    ("Solana",    "Base"):      [29, 7, 13],
    ("Polygon",   "Ethereum"):  [18, 3, 6],
    ("Polygon",   "Avalanche"): [24, 5, 9],
    ("Polygon",   "Solana"):    [27, 6, 11],
    ("Polygon",   "Base"):      [19, 3, 6],
    ("Base",      "Ethereum"):  [20, 3, 7],
    ("Base",      "Avalanche"): [26, 5, 10],
    ("Base",      "Solana"):    [29, 7, 13],
    ("Base",      "Polygon"):   [19, 3, 6],
}

COST_PARAMS = {
    "Chainlink CCIP":  {"fixed": 30,  "bps": 0.0002},
    "LayerZero":       {"fixed": 2,   "bps": 0.00005},
    "Wormhole":        {"fixed": 5,   "bps": 0.0001},
}

SECURITY_SCORES = {
    "Chainlink CCIP": 96,
    "LayerZero":      78,
    "Wormhole":       68,
}

INSTITUTION_SCORES = {
    "Chainlink CCIP": 95,
    "LayerZero":      65,
    "Wormhole":       60,
}

PROTOCOL_COLORS = {
    "Chainlink CCIP": "#375bd2",
    "LayerZero":      "#7c3aed",
    "Wormhole":       "#f97316",
}

PROTOCOL_INFO = {
    "Chainlink CCIP": {
        "sec_model": "Dual Oracle + Risk Management Network",
        "chains": "~20 chains",
        "hacks": "None",
        "rwa_adoption": "High (BUIDL, Swift)",
        "notes": "Only protocol with a dedicated Risk Management Network. Preferred by BlackRock BUIDL and Swift pilots. Highest institutional trust."
    },
    "LayerZero": {
        "sec_model": "Decentralized Verifier Network (DVN)",
        "chains": "70+ chains",
        "hacks": "None",
        "rwa_adoption": "Growing",
        "notes": "Highest chain coverage. DVN allows configurable security levels. Best cost-to-speed ratio for non-regulated assets."
    },
    "Wormhole": {
        "sec_model": "Guardian Network (19 nodes)",
        "chains": "35+ chains",
        "hacks": "$320M (Feb 2022, patched)",
        "rwa_adoption": "Moderate",
        "notes": "Strong ecosystem, recovering institutional trust post-hack. Good for Solana-connected routes."
    },
}

BRIDGE_HACKS = [
    {"Protocol": "Ronin Bridge",     "Amount ($M)": 625, "Year": 2022, "Cause": "Validator key compromise (5/9 nodes controlled by one entity)"},
    {"Protocol": "Poly Network",     "Amount ($M)": 611, "Year": 2021, "Cause": "Cross-chain contract exploit — funds eventually returned"},
    {"Protocol": "Wormhole",         "Amount ($M)": 320, "Year": 2022, "Cause": "Signature verification bug — 120K wETH minted without collateral"},
    {"Protocol": "Nomad Bridge",     "Amount ($M)": 190, "Year": 2022, "Cause": "Faulty initialization — anyone could replay valid messages"},
    {"Protocol": "Harmony Horizon",  "Amount ($M)": 100, "Year": 2022, "Cause": "2-of-5 multisig compromise (Lazarus Group)"},
    {"Protocol": "Qubit Finance",    "Amount ($M)": 80,  "Year": 2022, "Cause": "Logic flaw — fake ETH deposited, real tokens claimed on BSC"},
]

PRIORITY_WEIGHTS = {
    "Security First":  {"sec": 0.50, "inst": 0.25, "lat": 0.10, "cost": 0.15},
    "Speed First":     {"sec": 0.20, "inst": 0.10, "lat": 0.55, "cost": 0.15},
    "Cost First":      {"sec": 0.20, "inst": 0.10, "lat": 0.15, "cost": 0.55},
    "Balanced":        {"sec": 0.30, "inst": 0.25, "lat": 0.25, "cost": 0.20},
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def compute_cost(protocol: str, amount: float) -> float:
    p = COST_PARAMS[protocol]
    return round(p["fixed"] + amount * p["bps"], 2)

def compute_score(protocol: str, latency_min: float, cost_usd: float,
                  priority: str, compliance: str) -> int:
    sec_score  = SECURITY_SCORES[protocol]
    inst_score = INSTITUTION_SCORES[protocol]
    lat_score  = max(0, min(100, 100 - (latency_min / 30) * 100))
    cost_score = max(0, min(100, 100 - (cost_usd / 500) * 100))

    w = dict(PRIORITY_WEIGHTS[priority])  # copy
    if compliance == "Institutional (KYC required)":
        w["inst"] += 0.10
        w["lat"]  -= 0.05
        w["cost"] -= 0.05

    return round(
        sec_score  * w["sec"]  +
        inst_score * w["inst"] +
        lat_score  * w["lat"]  +
        cost_score * w["cost"]
    )

def section_label(text: str):
    st.markdown(f"""
    <div style="
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #5a6a82;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        {text}
        <span style="flex:1; height:1px; background:rgba(255,255,255,0.07); display:inline-block; vertical-align:middle;"></span>
    </div>
    """, unsafe_allow_html=True)

def proto_badge(text: str, color: str) -> str:
    return f"""<span style="
        display:inline-block; padding:3px 10px; border-radius:20px;
        font-family:'Space Mono',monospace; font-size:10px; font-weight:700;
        background:rgba(255,255,255,0.04); color:{color};
        border:1px solid {color}44; letter-spacing:0.5px;
    ">{text}</span>"""

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div style="
    display:flex; align-items:center; justify-content:space-between;
    padding:20px 0 32px; border-bottom:1px solid rgba(255,255,255,0.07);
    margin-bottom:40px;
">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="
            width:42px; height:42px;
            background:linear-gradient(135deg,#1e8fff,#00e5a0);
            border-radius:10px; display:flex; align-items:center;
            justify-content:center; font-size:22px;
        ">⛓</div>
        <div>
            <div style="font-size:24px; font-weight:800; letter-spacing:-0.5px;">CrossGuard</div>
            <div style="font-family:'Space Mono',monospace; font-size:10px;
                        color:#5a6a82; letter-spacing:2px; margin-top:2px;">
                TOKENIZED TREASURY ROUTER
            </div>
        </div>
    </div>
    <div style="
        font-family:'Space Mono',monospace; font-size:11px; color:#00e5a0;
        border:1px solid rgba(0,229,160,0.3); padding:6px 14px;
        border-radius:4px; letter-spacing:1px;
    ">FNCE313 · G2–5 · SMU</div>
</div>
""", unsafe_allow_html=True)

# ── HERO ──
st.markdown("""
<div style="text-align:center; margin-bottom:48px;">
    <h1 style="
        font-size:clamp(28px,4vw,48px); font-weight:800; letter-spacing:-1.5px;
        background:linear-gradient(135deg,#fff 30%,#1e8fff 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text; margin-bottom:16px; line-height:1.1;
    ">The $10 Trillion<br>Interoperability Problem</h1>
    <p style="color:#5a6a82; font-size:15px; max-width:580px; margin:0 auto 24px; line-height:1.6;">
        Tokenized assets are fragmenting across chains. Find the optimal cross-chain route
        for institutional-grade assets like U.S. Treasuries.
    </p>
    <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
        <span style="background:rgba(255,59,92,0.1); border:1px solid rgba(255,59,92,0.3);
                     color:#ff3b5c; padding:5px 14px; border-radius:20px;
                     font-family:'Space Mono',monospace; font-size:11px;">
            $2.8B hacked in bridges since 2021
        </span>
        <span style="background:rgba(30,143,255,0.1); border:1px solid rgba(30,143,255,0.3);
                     color:#1e8fff; padding:5px 14px; border-radius:20px;
                     font-family:'Space Mono',monospace; font-size:11px;">
            $10T tokenization market potential
        </span>
        <span style="background:rgba(0,229,160,0.1); border:1px solid rgba(0,229,160,0.3);
                     color:#00e5a0; padding:5px 14px; border-radius:20px;
                     font-family:'Space Mono',monospace; font-size:11px;">
            3 protocols compared live
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    "01 — ROUTING SIMULATOR",
    "02 — PROTOCOL COMPARISON",
    "03 — BRIDGE HACK HISTORY",
])

# ═════════════════════════════════════════════════════════════
# TAB 1 — SIMULATOR
# ═════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Cross-Chain Routing Simulator")

    # ── Controls ──
    col1, col_arrow, col2, col3 = st.columns([3, 0.5, 3, 3])

    with col1:
        from_chain = st.selectbox("Source Chain", CHAINS, index=0)
    with col_arrow:
        st.markdown("<div style='padding-top:28px; text-align:center; font-size:22px; color:#1e8fff; opacity:0.7;'>→</div>", unsafe_allow_html=True)
    with col2:
        to_options = [c for c in CHAINS if c != from_chain]
        to_chain = st.selectbox("Destination Chain", to_options, index=0)
    with col3:
        amount = st.number_input("Transfer Amount (USD)", min_value=1000, max_value=500_000_000,
                                  value=1_000_000, step=100_000, format="%d")

    col4, col5, col6 = st.columns(3)
    with col4:
        asset = st.selectbox("Asset Type", [
            "BlackRock BUIDL (T-Bill)",
            "Franklin BENJI",
            "Ondo USDY",
            "USDC (Stablecoin ref.)"
        ])
    with col5:
        priority = st.selectbox("Priority", list(PRIORITY_WEIGHTS.keys()), index=0)
    with col6:
        compliance = st.selectbox("Compliance Level", [
            "Institutional (KYC required)",
            "Permissioned DeFi",
            "Public DeFi"
        ])

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("⚡ Run Simulation", use_container_width=True)

    if run:
        if from_chain == to_chain:
            st.error("Please select different source and destination chains.")
        else:
            route_key = (from_chain, to_chain)
            latencies = LATENCY.get(route_key, [22, 5, 10])
            protocols = list(COST_PARAMS.keys())

            costs  = [compute_cost(p, amount) for p in protocols]
            scores = [compute_score(p, latencies[i], costs[i], priority, compliance)
                      for i, p in enumerate(protocols)]

            winner_idx = scores.index(max(scores))
            winner     = protocols[winner_idx]

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div style='font-family:Space Mono,monospace; font-size:10px; "
                        "color:#5a6a82; letter-spacing:2px; text-transform:uppercase; "
                        "margin-bottom:20px;'>— Simulation Output</div>", unsafe_allow_html=True)

            # ── Route Visualization ──
            st.markdown(f"""
            <div style="
                background:#141c2b; border:1px solid rgba(255,255,255,0.07);
                border-radius:12px; padding:24px 28px; margin-bottom:24px;
            ">
                <div style="font-family:'Space Mono',monospace; font-size:10px;
                            letter-spacing:2px; color:#5a6a82; text-transform:uppercase;
                            margin-bottom:20px;">Transfer Route</div>
                <div style="display:flex; align-items:center; gap:0; overflow-x:auto;">
                    <div style="text-align:center; flex-shrink:0;">
                        <div style="background:#0e1420; border:1px solid {PROTOCOL_COLORS[winner]}33;
                                    border-radius:8px; padding:10px 18px; font-weight:600;
                                    color:{PROTOCOL_COLORS[winner]}88;">{from_chain}</div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px;
                                    color:#5a6a82; margin-top:6px; letter-spacing:1px;">SOURCE</div>
                    </div>
                    <div style="flex:1; min-width:60px; height:2px; position:relative;
                                background:linear-gradient(90deg,{PROTOCOL_COLORS[winner]}44,
                                {PROTOCOL_COLORS[winner]},{PROTOCOL_COLORS[winner]}44);">
                        <div style="position:absolute; top:-22px; left:50%; transform:translateX(-50%);
                                    font-family:'Space Mono',monospace; font-size:9px;
                                    color:{PROTOCOL_COLORS[winner]}; white-space:nowrap;">
                            {winner}
                        </div>
                    </div>
                    <div style="text-align:center; flex-shrink:0;">
                        <div style="background:#0e1420; border:1px solid rgba(255,255,255,0.07);
                                    border-radius:8px; padding:10px 18px; font-weight:600;">
                            🔒 Protocol Relay
                        </div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px;
                                    color:#5a6a82; margin-top:6px; letter-spacing:1px;">VALIDATION</div>
                    </div>
                    <div style="flex:1; min-width:60px; height:2px;
                                background:linear-gradient(90deg,{PROTOCOL_COLORS[winner]}44,
                                {PROTOCOL_COLORS[winner]},{PROTOCOL_COLORS[winner]}44);"></div>
                    <div style="text-align:center; flex-shrink:0;">
                        <div style="background:#0e1420; border:1px solid {PROTOCOL_COLORS[winner]}33;
                                    border-radius:8px; padding:10px 18px; font-weight:600;
                                    color:{PROTOCOL_COLORS[winner]}88;">{to_chain}</div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px;
                                    color:#5a6a82; margin-top:6px; letter-spacing:1px;">DESTINATION</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Protocol Result Cards ──
            # Rendered as a single st.components.v1.html block to avoid
            # Streamlit's HTML sanitizer breaking apostrophes in font-family names
            import streamlit.components.v1 as components

            def build_card(i, proto):
                is_winner  = (i == winner_idx)
                color      = PROTOCOL_COLORS[proto]
                bps_cost   = (costs[i] / amount) * 10_000 if amount > 0 else 0
                sec_model  = PROTOCOL_INFO[proto]["sec_model"]
                sec_score  = SECURITY_SCORES[proto]
                score_val  = scores[i]
                lat_val    = latencies[i]
                cost_val   = costs[i]

                lat_color  = "#00e5a0" if lat_val < 8 else ("#1e8fff" if lat_val < 15 else "#5a6a82")
                cost_color = "#00e5a0" if cost_val < 20 else ("#1e8fff" if cost_val < 80 else "#f97316")

                if is_winner:
                    border = f"border:1px solid {color}66; box-shadow:0 0 20px {color}1a;"
                    badge  = (f'<div style="font-size:8px; letter-spacing:1.5px; color:{color};'
                              f' background:{color}1a; border:1px solid {color}44;'
                              f' padding:3px 8px; border-radius:4px; display:inline-block;'
                              f' margin-bottom:12px;">&#9733; RECOMMENDED</div>')
                else:
                    border = "border:1px solid rgba(255,255,255,0.07);"
                    badge  = ""

                return f"""
                <div style="background:#141c2b; {border} border-radius:12px; padding:22px; flex:1; min-width:0;">
                    {badge}
                    <div style="width:32px; height:4px; background:{color}; border-radius:2px; margin-bottom:14px;"></div>
                    <div style="font-size:16px; font-weight:700; margin-bottom:3px; color:#e8edf5;">{proto}</div>
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:1px; text-transform:uppercase; margin-bottom:18px;">
                        {sec_model}
                    </div>
                    <div style="border-bottom:1px solid rgba(255,255,255,0.05); padding:7px 0; display:flex; justify-content:space-between;">
                        <span style="font-size:12px; color:#5a6a82;">Latency</span>
                        <span style="font-size:13px; font-weight:700; color:{lat_color};">~{lat_val} min</span>
                    </div>
                    <div style="border-bottom:1px solid rgba(255,255,255,0.05); padding:7px 0; display:flex; justify-content:space-between;">
                        <span style="font-size:12px; color:#5a6a82;">Transfer Cost</span>
                        <span style="font-size:13px; font-weight:700; color:{cost_color};">${cost_val:,.0f}</span>
                    </div>
                    <div style="border-bottom:1px solid rgba(255,255,255,0.05); padding:7px 0; display:flex; justify-content:space-between;">
                        <span style="font-size:12px; color:#5a6a82;">Cost / bps</span>
                        <span style="font-size:13px; color:#5a6a82;">{bps_cost:.2f} bps</span>
                    </div>
                    <div style="padding:7px 0; display:flex; justify-content:space-between;">
                        <span style="font-size:12px; color:#5a6a82;">Security Score</span>
                        <span style="font-size:13px; font-weight:700; color:#e8edf5;">{sec_score}/100</span>
                    </div>
                    <div style="margin-top:16px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-size:9px; color:#5a6a82; letter-spacing:1px; text-transform:uppercase;">Composite Score</span>
                            <span style="font-size:10px; color:{color}; font-weight:700;">{score_val}</span>
                        </div>
                        <div style="height:6px; background:#0e1420; border-radius:3px; overflow:hidden;">
                            <div style="height:100%; width:{score_val}%; background:{color}; border-radius:3px;"></div>
                        </div>
                    </div>
                </div>"""

            cards_html = "".join(build_card(i, p) for i, p in enumerate(protocols))
            components.html(f"""
                <div style="display:flex; gap:16px; font-family:Syne,sans-serif; color:#e8edf5;">
                    {cards_html}
                </div>
            """, height=420)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Spider Chart ──
            categories = ["Security", "Institutional", "Speed", "Cost Efficiency", "Chain Coverage"]
            coverage_scores = {"Chainlink CCIP": 40, "LayerZero": 100, "Wormhole": 70}
            speed_scores    = {"Chainlink CCIP": 20, "LayerZero": 95,  "Wormhole": 65}
            cost_eff_scores = {"Chainlink CCIP": 30, "LayerZero": 95,  "Wormhole": 70}

            def hex_to_rgba(hex_color: str, alpha: float = 0.13) -> str:
                h = hex_color.lstrip("#")
                r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                return f"rgba({r},{g},{b},{alpha})"

            fig_radar = go.Figure()
            for proto in protocols:
                vals = [
                    SECURITY_SCORES[proto],
                    INSTITUTION_SCORES[proto],
                    speed_scores[proto],
                    cost_eff_scores[proto],
                    coverage_scores[proto],
                ]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=proto,
                    line_color=PROTOCOL_COLORS[proto],
                    fillcolor=hex_to_rgba(PROTOCOL_COLORS[proto], 0.13),
                    line_width=2,
                ))

            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#141c2b",
                    radialaxis=dict(visible=True, range=[0, 100],
                                   color="#5a6a82", gridcolor="rgba(255,255,255,0.06)",
                                   tickfont=dict(family="Space Mono", size=9, color="#5a6a82")),
                    angularaxis=dict(color="#e8edf5", gridcolor="rgba(255,255,255,0.06)",
                                     tickfont=dict(family="Syne", size=11)),
                ),
                paper_bgcolor="#0e1420",
                plot_bgcolor="#0e1420",
                font=dict(family="Syne", color="#e8edf5"),
                legend=dict(font=dict(family="Syne", size=12), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=40, b=40),
                height=420,
                title=dict(text="Protocol Capability Radar", font=dict(family="Syne", size=14, color="#5a6a82"), x=0.5),
            )

            # ── Bar Chart ──
            fig_bar = go.Figure()
            bar_colors = [PROTOCOL_COLORS[p] for p in protocols]
            fig_bar.add_trace(go.Bar(
                x=protocols, y=scores,
                marker_color=bar_colors,
                marker_line_width=0,
                text=[f"{s}" for s in scores],
                textposition="outside",
                textfont=dict(family="Space Mono", size=13, color="#e8edf5"),
            ))
            fig_bar.update_layout(
                paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
                font=dict(family="Syne", color="#e8edf5"),
                yaxis=dict(range=[0, 110], gridcolor="rgba(255,255,255,0.05)",
                           tickfont=dict(family="Space Mono", size=10, color="#5a6a82"),
                           title=dict(text="Composite Score", font=dict(size=11, color="#5a6a82"))),
                xaxis=dict(tickfont=dict(family="Syne", size=12)),
                margin=dict(t=40, b=20, l=60, r=20),
                height=320,
                showlegend=False,
                title=dict(text="Composite Score by Protocol", font=dict(family="Syne", size=14, color="#5a6a82"), x=0.5),
            )

            chart_col1, chart_col2 = st.columns([1.1, 1])
            with chart_col1:
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
            with chart_col2:
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

            # ── Summary ──
            winner_latency  = latencies[winner_idx]
            winner_cost     = costs[winner_idx]
            winner_score    = max(scores)
            winner_color    = PROTOCOL_COLORS[winner]
            winner_notes    = PROTOCOL_INFO[winner]["notes"]

            st.markdown(f"""
            <div style="background:rgba(0,229,160,0.05); border:1px solid rgba(0,229,160,0.2);
                        border-radius:12px; padding:20px 28px; margin-top:8px;">
                <div style="display:flex; gap:36px; flex-wrap:wrap; align-items:center;">
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5a6a82;
                                    letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Recommended</div>
                        <div style="font-size:18px; font-weight:800; color:{winner_color};">{winner}</div>
                    </div>
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5a6a82;
                                    letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Best Latency</div>
                        <div style="font-size:22px; font-weight:800; color:#00e5a0; letter-spacing:-1px;">
                            ~{winner_latency} min
                        </div>
                    </div>
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5a6a82;
                                    letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Transfer Cost</div>
                        <div style="font-size:22px; font-weight:800; color:#00e5a0; letter-spacing:-1px;">
                            ${winner_cost:,.0f}
                        </div>
                    </div>
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5a6a82;
                                    letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Composite Score</div>
                        <div style="font-size:22px; font-weight:800; color:#00e5a0; letter-spacing:-1px;">
                            {winner_score}/100
                        </div>
                    </div>
                    <div style="flex:1; min-width:220px; font-size:12px; color:#5a6a82; line-height:1.6;
                                border-left:1px solid rgba(255,255,255,0.07); padding-left:24px;">
                        <strong style="color:#e8edf5; font-size:13px;">Why this choice?</strong><br>
                        {winner_notes}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# TAB 2 — PROTOCOL COMPARISON
# ═════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Protocol Comparison — Architecture Deep Dive")

    # ── Static Comparison Table ──
    comparison_data = {
        "Feature": [
            "Security Model",
            "Avg. Latency",
            "Base Fee",
            "Decentralization",
            "Institutional Grade",
            "Chains Supported",
            "RWA/Treasury Adoption",
            "Risk Management Network",
            "Notable Hacks",
        ],
        "Chainlink CCIP": [
            "Dual Oracle + RMN",
            "~20 min",
            "$15–50",
            "High",
            "✓ Yes",
            "~20",
            "High (BUIDL, Swift)",
            "✓ Dedicated RMN",
            "None",
        ],
        "LayerZero": [
            "DVN (Configurable)",
            "~2–5 min",
            "$0.5–5",
            "Medium",
            "Partial",
            "70+",
            "Growing",
            "✗ None",
            "None",
        ],
        "Wormhole": [
            "Guardian Network (19)",
            "~5–15 min",
            "$1–10",
            "Medium-Low",
            "Partial",
            "35+",
            "Moderate",
            "✗ None",
            "$320M (2022, patched)",
        ],
    }

    df_compare = pd.DataFrame(comparison_data)

    def color_cells(val):
        if val in ["High", "✓ Yes", "✓ Dedicated RMN", "None", "High (BUIDL, Swift)"]:
            return "background-color: rgba(0,229,160,0.08); color: #00e5a0;"
        elif val in ["Medium", "Partial", "Growing", "Moderate"]:
            return "background-color: rgba(30,143,255,0.08); color: #1e8fff;"
        elif val in ["Medium-Low", "✗ None", "$320M (2022, patched)"]:
            return "background-color: rgba(255,59,92,0.08); color: #ff3b5c;"
        return ""

    styled = df_compare.set_index("Feature").style.map(color_cells)

    st.dataframe(
        styled,
        use_container_width=True,
        height=385,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Static Score Comparison")

    protocols = list(COST_PARAMS.keys())
    colors    = [PROTOCOL_COLORS[p] for p in protocols]

    c1, c2, c3 = st.columns(3)

    with c1:
        fig = go.Figure(go.Bar(
            x=protocols, y=[SECURITY_SCORES[p] for p in protocols],
            marker_color=colors, marker_line_width=0,
            text=[str(SECURITY_SCORES[p]) for p in protocols],
            textposition="outside",
            textfont=dict(family="Space Mono", size=12, color="#e8edf5"),
        ))
        fig.update_layout(
            title=dict(text="Security Score /100", font=dict(family="Syne", size=13, color="#5a6a82"), x=0.5),
            paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
            yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,0.04)", tickfont=dict(family="Space Mono", size=9, color="#5a6a82")),
            xaxis=dict(tickfont=dict(family="Syne", size=11)),
            margin=dict(t=50, b=10, l=10, r=10), height=280, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        fig2 = go.Figure(go.Bar(
            x=protocols, y=[INSTITUTION_SCORES[p] for p in protocols],
            marker_color=colors, marker_line_width=0,
            text=[str(INSTITUTION_SCORES[p]) for p in protocols],
            textposition="outside",
            textfont=dict(family="Space Mono", size=12, color="#e8edf5"),
        ))
        fig2.update_layout(
            title=dict(text="Institutional Score /100", font=dict(family="Syne", size=13, color="#5a6a82"), x=0.5),
            paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
            yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,0.04)", tickfont=dict(family="Space Mono", size=9, color="#5a6a82")),
            xaxis=dict(tickfont=dict(family="Syne", size=11)),
            margin=dict(t=50, b=10, l=10, r=10), height=280, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with c3:
        latency_avg = {p: round(sum(LATENCY[k][i] for k in LATENCY) / len(LATENCY))
                       for i, p in enumerate(protocols)}
        fig3 = go.Figure(go.Bar(
            x=protocols, y=list(latency_avg.values()),
            marker_color=colors, marker_line_width=0,
            text=[f"{v} min" for v in latency_avg.values()],
            textposition="outside",
            textfont=dict(family="Space Mono", size=12, color="#e8edf5"),
        ))
        fig3.update_layout(
            title=dict(text="Avg. Latency (min)", font=dict(family="Syne", size=13, color="#5a6a82"), x=0.5),
            paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
            yaxis=dict(range=[0, 35], gridcolor="rgba(255,255,255,0.04)",
                       tickfont=dict(family="Space Mono", size=9, color="#5a6a82"),
                       title=dict(text="minutes", font=dict(size=10, color="#5a6a82"))),
            xaxis=dict(tickfont=dict(family="Syne", size=11)),
            margin=dict(t=50, b=10, l=40, r=10), height=280, showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    # ── Protocol Detail Expanders ──
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Deep Dive — Protocol Architecture")

    for proto in protocols:
        color = PROTOCOL_COLORS[proto]
        info  = PROTOCOL_INFO[proto]
        with st.expander(f"  {proto}"):
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown(f"""
                <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82;
                            letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Security Model</div>
                <div style="font-size:14px; font-weight:600; color:{color}; margin-bottom:16px;">{info['sec_model']}</div>

                <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82;
                            letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Chains Supported</div>
                <div style="font-size:14px; font-weight:600; margin-bottom:16px;">{info['chains']}</div>

                <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82;
                            letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">RWA Adoption</div>
                <div style="font-size:14px; font-weight:600; margin-bottom:16px;">{info['rwa_adoption']}</div>
                """, unsafe_allow_html=True)
            with ec2:
                hack_color = "#ff3b5c" if info['hacks'] != "None" else "#00e5a0"
                st.markdown(f"""
                <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82;
                            letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Notable Hacks</div>
                <div style="font-size:14px; font-weight:600; color:{hack_color}; margin-bottom:16px;">{info['hacks']}</div>

                <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82;
                            letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Analysis</div>
                <div style="font-size:13px; color:#5a6a82; line-height:1.6;">{info['notes']}</div>
                """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# TAB 3 — BRIDGE HACKS
# ═════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("The Weakest Link — Bridge Hack History (2021–2024)")

    df_hacks = pd.DataFrame(BRIDGE_HACKS)

    # ── KPI ──
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Losses", "$2.8B+", delta=None)
    with k2:
        st.metric("Incidents Tracked", "20+", delta=None)
    with k3:
        st.metric("Peak Year", "2022", delta=None)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bar Chart ──
    fig_hacks = go.Figure(go.Bar(
        x=df_hacks["Protocol"],
        y=df_hacks["Amount ($M)"],
        marker_color=[
            "#ff3b5c", "#ff6b35", "#f97316",
            "#ff3b5c", "#ff6b35", "#f97316"
        ],
        marker_line_width=0,
        text=[f"${v}M" for v in df_hacks["Amount ($M)"]],
        textposition="outside",
        textfont=dict(family="Space Mono", size=11, color="#e8edf5"),
    ))
    fig_hacks.update_layout(
        paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
        font=dict(family="Syne", color="#e8edf5"),
        yaxis=dict(
            title=dict(text="Amount Lost ($M)", font=dict(size=11, color="#5a6a82")),
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(family="Space Mono", size=10, color="#5a6a82"),
            range=[0, 720],
        ),
        xaxis=dict(tickfont=dict(family="Syne", size=12)),
        margin=dict(t=20, b=20, l=60, r=20),
        height=340,
        showlegend=False,
    )
    st.plotly_chart(fig_hacks, use_container_width=True, config={"displayModeBar": False})

    # ── Table ──
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Incident Details")

    def color_amount(val):
        if isinstance(val, (int, float)):
            if val >= 500:   return "color: #ff3b5c; font-weight: bold;"
            elif val >= 150: return "color: #f97316; font-weight: bold;"
            else:            return "color: #ffd166; font-weight: bold;"
        return ""

    styled_hacks = df_hacks.set_index("Protocol").style.map(color_amount, subset=["Amount ($M)"])
    st.dataframe(styled_hacks, use_container_width=True, height=270)

    # ── Root Causes ──
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Why Bridges Fail — Root Cause Analysis")

    causes = {
        "Validator Centralization": 45,
        "Smart Contract Bugs":      30,
        "Key Management Failures":  15,
        "Upgrade Logic Flaws":      10,
    }

    fig_pie = go.Figure(go.Pie(
        labels=list(causes.keys()),
        values=list(causes.values()),
        hole=0.55,
        marker=dict(colors=["#ff3b5c", "#f97316", "#ffd166", "#ff6b35"],
                    line=dict(color="#0e1420", width=2)),
        textfont=dict(family="Syne", size=12),
        textinfo="percent+label",
    ))
    fig_pie.update_layout(
        paper_bgcolor="#0e1420",
        font=dict(family="Syne", color="#e8edf5"),
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=340,
        annotations=[dict(text="Root<br>Causes", x=0.5, y=0.5, font=dict(size=13, color="#5a6a82"), showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    st.markdown("""
    <div style="background:rgba(255,59,92,0.05); border:1px solid rgba(255,59,92,0.2);
                border-radius:12px; padding:20px 24px; margin-top:8px;">
        <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82;
                    letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">Key Takeaway</div>
        <div style="font-size:14px; color:#e8edf5; line-height:1.7;">
            The $2.8B in bridge losses is not random — it follows a clear pattern. Every major exploit
            exploited either <strong style="color:#ff3b5c;">validator centralization</strong> (too few nodes, key leakage),
            <strong style="color:#f97316;">smart contract logic flaws</strong> (signature bypass, replay attacks),
            or <strong style="color:#ffd166;">governance/upgrade failures</strong>.
            Modern protocols like CCIP, LayerZero, and Wormhole each attempt to address these
            — but with different architectural trade-offs in security vs. speed vs. cost.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:24px; border-top:1px solid rgba(255,255,255,0.07);">
    <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5a6a82; letter-spacing:2px;">
        CROSSGUARD · FNCE313 · GROUP 2, TEAM 5 · SINGAPORE MANAGEMENT UNIVERSITY · 2026
    </div>
    <div style="font-size:12px; color:#5a6a82; margin-top:6px;">
        Data is simulated for academic purposes. Sources: Chainlink, LayerZero, Wormhole documentation · RWA.xyz · DeFiLlama
    </div>
</div>
""", unsafe_allow_html=True)
