"""
CrossGuard — Tokenized Treasury Cross-Chain Router
FNCE313 · Group 2, Team 5 · Singapore Management University
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import time
import random

st.set_page_config(
    page_title="CrossGuard — Tokenized Treasury Router",
    page_icon="⛓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #080c12; color: #e8edf5; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
div[data-testid="metric-container"] { background: #0e1420; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px; }
div[data-testid="metric-container"] label { font-family: 'Space Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: #5a6a82 !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 800 !important; letter-spacing: -1px !important; }
div[data-baseweb="select"] > div { background-color: #141c2b !important; border-color: rgba(255,255,255,0.07) !important; color: #e8edf5 !important; border-radius: 8px !important; }
div[data-baseweb="input"] > div { background-color: #141c2b !important; border-color: rgba(255,255,255,0.07) !important; border-radius: 8px !important; }
input { color: #e8edf5 !important; }
div[data-testid="stButton"] > button { background: linear-gradient(135deg, #1e8fff, #0057b8) !important; color: white !important; border: none !important; border-radius: 10px !important; font-family: 'Syne', sans-serif !important; font-size: 15px !important; font-weight: 700 !important; padding: 14px 32px !important; width: 100% !important; letter-spacing: 0.5px !important; transition: all 0.2s !important; }
div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(30,143,255,0.35) !important; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
hr { border-color: rgba(255,255,255,0.07) !important; margin: 2rem 0; }
button[data-baseweb="tab"] { font-family: 'Space Mono', monospace !important; font-size: 11px !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: #5a6a82 !important; background: transparent !important; border: none !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #1e8fff !important; border-bottom: 2px solid #1e8fff !important; }
div[data-testid="stExpander"] { background: #0e1420; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; }
label[data-testid="stWidgetLabel"] p { font-family: 'Space Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: #5a6a82 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────
CHAINS = ["Ethereum", "Avalanche", "Solana", "Polygon", "Base"]

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
    "Chainlink CCIP": {"fixed": 30,  "bps": 0.0002},
    "LayerZero":      {"fixed": 2,   "bps": 0.00005},
    "Wormhole":       {"fixed": 5,   "bps": 0.0001},
}

SECURITY_SCORES    = {"Chainlink CCIP": 96, "LayerZero": 78, "Wormhole": 68}
INSTITUTION_SCORES = {"Chainlink CCIP": 95, "LayerZero": 65, "Wormhole": 60}

PROTOCOL_COLORS = {
    "Chainlink CCIP": "#375bd2",
    "LayerZero":      "#7c3aed",
    "Wormhole":       "#f97316",
}

PROTOCOL_INFO = {
    "Chainlink CCIP": {
        "sec_model": "Dual Oracle + Risk Management Network",
        "chains": "~20 chains", "hacks": "None", "rwa_adoption": "High (BUIDL, Swift)",
        "notes": "Only protocol with a dedicated Risk Management Network. Preferred by BlackRock BUIDL and Swift pilots. Highest institutional trust."
    },
    "LayerZero": {
        "sec_model": "Decentralized Verifier Network (DVN)",
        "chains": "70+ chains", "hacks": "None", "rwa_adoption": "Growing",
        "notes": "Highest chain coverage. DVN allows configurable security levels. Best cost-to-speed ratio for non-regulated assets."
    },
    "Wormhole": {
        "sec_model": "Guardian Network (19 nodes)",
        "chains": "35+ chains", "hacks": "$320M (Feb 2022, patched)", "rwa_adoption": "Moderate",
        "notes": "Strong ecosystem, recovering institutional trust post-hack. Good for Solana-connected routes."
    },
}

BRIDGE_HACKS = [
    {"Protocol": "Ronin Bridge",    "Amount ($M)": 625, "Year": 2022, "Cause": "Validator key compromise (5/9 nodes controlled by one entity)"},
    {"Protocol": "Poly Network",    "Amount ($M)": 611, "Year": 2021, "Cause": "Cross-chain contract exploit — funds eventually returned"},
    {"Protocol": "Wormhole",        "Amount ($M)": 320, "Year": 2022, "Cause": "Signature verification bug — 120K wETH minted without collateral"},
    {"Protocol": "Nomad Bridge",    "Amount ($M)": 190, "Year": 2022, "Cause": "Faulty initialization — anyone could replay valid messages"},
    {"Protocol": "Harmony Horizon", "Amount ($M)": 100, "Year": 2022, "Cause": "2-of-5 multisig compromise (Lazarus Group)"},
    {"Protocol": "Qubit Finance",   "Amount ($M)": 80,  "Year": 2022, "Cause": "Logic flaw — fake ETH deposited, real tokens claimed on BSC"},
]

PRIORITY_WEIGHTS = {
    "Security First": {"sec": 0.50, "inst": 0.25, "lat": 0.10, "cost": 0.15},
    "Speed First":    {"sec": 0.20, "inst": 0.10, "lat": 0.55, "cost": 0.15},
    "Cost First":     {"sec": 0.20, "inst": 0.10, "lat": 0.15, "cost": 0.55},
    "Balanced":       {"sec": 0.30, "inst": 0.25, "lat": 0.25, "cost": 0.20},
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def compute_cost(protocol, amount):
    p = COST_PARAMS[protocol]
    return round(p["fixed"] + amount * p["bps"], 2)

def compute_score(protocol, latency_min, cost_usd, priority, compliance):
    sec_score  = SECURITY_SCORES[protocol]
    inst_score = INSTITUTION_SCORES[protocol]
    lat_score  = max(0, min(100, 100 - (latency_min / 30) * 100))
    cost_score = max(0, min(100, 100 - (cost_usd / 500) * 100))
    w = dict(PRIORITY_WEIGHTS[priority])
    if compliance == "Institutional (KYC required)":
        w["inst"] += 0.10; w["lat"] -= 0.05; w["cost"] -= 0.05
    return round(sec_score*w["sec"] + inst_score*w["inst"] + lat_score*w["lat"] + cost_score*w["cost"])

def section_label(text):
    st.markdown(f"""
    <div style="font-size:10px; letter-spacing:3px; text-transform:uppercase; color:#5a6a82;
                margin-bottom:20px; display:flex; align-items:center; gap:12px;">
        {text}
        <span style="flex:1; height:1px; background:rgba(255,255,255,0.07); display:inline-block;"></span>
    </div>""", unsafe_allow_html=True)

def hex_to_rgba(hex_color, alpha=0.13):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

# ─────────────────────────────────────────────────────────────
# SESSION STATE  — persist results across Streamlit reruns
# ─────────────────────────────────────────────────────────────
_defaults = {
    "sim_done": False,
    "sim_from": None, "sim_to": None, "sim_amount": None,
    "sim_asset": None, "sim_priority": None, "sim_compliance": None,
    "sim_latencies": None, "sim_protocols": None,
    "sim_costs": None, "sim_scores": None, "sim_winner_idx": None,
    "exec_done": False, "exec_tx": None,
    "split_done": False, "split_data": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; justify-content:space-between;
            padding:20px 0 32px; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:40px;">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="width:42px; height:42px; background:linear-gradient(135deg,#1e8fff,#00e5a0);
                    border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:22px;">⛓</div>
        <div>
            <div style="font-size:24px; font-weight:800; letter-spacing:-0.5px;">CrossGuard</div>
            <div style="font-size:10px; color:#5a6a82; letter-spacing:2px; margin-top:2px;">TOKENIZED TREASURY ROUTER</div>
        </div>
    </div>
    <div style="font-size:11px; color:#00e5a0; border:1px solid rgba(0,229,160,0.3);
                padding:6px 14px; border-radius:4px; letter-spacing:1px;">FNCE313 · G2–5 · SMU</div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom:48px;">
    <h1 style="font-size:clamp(28px,4vw,48px); font-weight:800; letter-spacing:-1.5px;
               background:linear-gradient(135deg,#fff 30%,#1e8fff 100%);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;
               background-clip:text; margin-bottom:16px; line-height:1.1;">
        The $10 Trillion<br>Interoperability Problem</h1>
    <p style="color:#5a6a82; font-size:15px; max-width:580px; margin:0 auto 24px; line-height:1.6;">
        Tokenized assets are fragmenting across chains. Find the optimal cross-chain route
        for institutional-grade assets like U.S. Treasuries.</p>
    <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
        <span style="background:rgba(255,59,92,0.1); border:1px solid rgba(255,59,92,0.3); color:#ff3b5c;
                     padding:5px 14px; border-radius:20px; font-size:11px;">$2.8B hacked in bridges since 2021</span>
        <span style="background:rgba(30,143,255,0.1); border:1px solid rgba(30,143,255,0.3); color:#1e8fff;
                     padding:5px 14px; border-radius:20px; font-size:11px;">$10T tokenization market potential</span>
        <span style="background:rgba(0,229,160,0.1); border:1px solid rgba(0,229,160,0.3); color:#00e5a0;
                     padding:5px 14px; border-radius:20px; font-size:11px;">3 protocols compared live</span>
    </div>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["01 — ROUTING SIMULATOR", "02 — PROTOCOL COMPARISON", "03 — BRIDGE HACK HISTORY"])

# ═════════════════════════════════════════════════════════════
# TAB 1 — SIMULATOR
# ═════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Cross-Chain Routing Simulator")

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
        asset = st.selectbox("Asset Type", ["BlackRock BUIDL (T-Bill)", "Franklin BENJI", "Ondo USDY", "USDC (Stablecoin ref.)"])
    with col5:
        priority = st.selectbox("Priority", list(PRIORITY_WEIGHTS.keys()), index=0)
    with col6:
        compliance = st.selectbox("Compliance Level", ["Institutional (KYC required)", "Permissioned DeFi", "Public DeFi"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RUN SIMULATION button ──
    if st.button("⚡ Run Simulation", use_container_width=True, key="btn_run"):
        if from_chain == to_chain:
            st.error("Please select different source and destination chains.")
        else:
            _lats   = LATENCY.get((from_chain, to_chain), [22, 5, 10])
            _protos = list(COST_PARAMS.keys())
            _costs  = [compute_cost(p, amount) for p in _protos]
            _scores = [compute_score(p, _lats[i], _costs[i], priority, compliance) for i, p in enumerate(_protos)]
            st.session_state.update({
                "sim_done": True,
                "sim_from": from_chain, "sim_to": to_chain,
                "sim_amount": amount,   "sim_asset": asset,
                "sim_priority": priority, "sim_compliance": compliance,
                "sim_latencies": _lats, "sim_protocols": _protos,
                "sim_costs": _costs,    "sim_scores": _scores,
                "sim_winner_idx": _scores.index(max(_scores)),
                "exec_done": False, "exec_tx": None,
                "split_done": False, "split_data": None,
            })

    # ── RESULTS (shown whenever sim_done is True in session state) ──
    if st.session_state.sim_done:
        S          = st.session_state
        latencies  = S.sim_latencies
        protocols  = S.sim_protocols
        costs      = S.sim_costs
        scores     = S.sim_scores
        winner_idx = S.sim_winner_idx
        winner     = protocols[winner_idx]
        wc         = PROTOCOL_COLORS[winner]
        winner_latency = latencies[winner_idx]
        winner_cost    = costs[winner_idx]
        winner_score   = max(scores)
        winner_notes   = PROTOCOL_INFO[winner]["notes"]

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:10px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:20px;'>— Simulation Output</div>", unsafe_allow_html=True)

        # Route visualization
        st.markdown(f"""
        <div style="background:#141c2b; border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:24px 28px; margin-bottom:24px;">
            <div style="font-size:10px; letter-spacing:2px; color:#5a6a82; text-transform:uppercase; margin-bottom:20px;">Transfer Route</div>
            <div style="display:flex; align-items:center; overflow-x:auto;">
                <div style="text-align:center; flex-shrink:0;">
                    <div style="background:#0e1420; border:1px solid {wc}33; border-radius:8px; padding:10px 18px; font-weight:600; color:{wc}88;">{S.sim_from}</div>
                    <div style="font-size:9px; color:#5a6a82; margin-top:6px; letter-spacing:1px;">SOURCE</div>
                </div>
                <div style="flex:1; min-width:60px; height:2px; position:relative; background:linear-gradient(90deg,{wc}44,{wc},{wc}44);">
                    <div style="position:absolute; top:-22px; left:50%; transform:translateX(-50%); font-size:9px; color:{wc}; white-space:nowrap;">{winner}</div>
                </div>
                <div style="text-align:center; flex-shrink:0;">
                    <div style="background:#0e1420; border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:10px 18px; font-weight:600;">🔒 Protocol Relay</div>
                    <div style="font-size:9px; color:#5a6a82; margin-top:6px; letter-spacing:1px;">VALIDATION</div>
                </div>
                <div style="flex:1; min-width:60px; height:2px; background:linear-gradient(90deg,{wc}44,{wc},{wc}44);"></div>
                <div style="text-align:center; flex-shrink:0;">
                    <div style="background:#0e1420; border:1px solid {wc}33; border-radius:8px; padding:10px 18px; font-weight:600; color:{wc}88;">{S.sim_to}</div>
                    <div style="font-size:9px; color:#5a6a82; margin-top:6px; letter-spacing:1px;">DESTINATION</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Protocol cards
        def build_card(i, proto):
            is_w      = (i == winner_idx)
            color     = PROTOCOL_COLORS[proto]
            bps_cost  = (costs[i] / S.sim_amount) * 10_000
            lat_color = "#00e5a0" if latencies[i] < 8 else ("#1e8fff" if latencies[i] < 15 else "#5a6a82")
            cost_color= "#00e5a0" if costs[i] < 20 else ("#1e8fff" if costs[i] < 80 else "#f97316")
            border    = f"border:1px solid {color}66; box-shadow:0 0 20px {color}1a;" if is_w else "border:1px solid rgba(255,255,255,0.07);"
            badge     = (f'<div style="font-size:8px; letter-spacing:1.5px; color:{color}; background:{color}1a;'
                         f' border:1px solid {color}44; padding:3px 8px; border-radius:4px;'
                         f' display:inline-block; margin-bottom:12px;">&#9733; RECOMMENDED</div>') if is_w else ""
            return f"""
            <div style="background:#141c2b; {border} border-radius:12px; padding:22px; flex:1; min-width:0;">
                {badge}
                <div style="width:32px; height:4px; background:{color}; border-radius:2px; margin-bottom:14px;"></div>
                <div style="font-size:16px; font-weight:700; margin-bottom:3px; color:#e8edf5;">{proto}</div>
                <div style="font-size:9px; color:#5a6a82; letter-spacing:1px; text-transform:uppercase; margin-bottom:18px;">{PROTOCOL_INFO[proto]['sec_model']}</div>
                <div style="border-bottom:1px solid rgba(255,255,255,0.05); padding:7px 0; display:flex; justify-content:space-between;">
                    <span style="font-size:12px; color:#5a6a82;">Latency</span>
                    <span style="font-size:13px; font-weight:700; color:{lat_color};">~{latencies[i]} min</span>
                </div>
                <div style="border-bottom:1px solid rgba(255,255,255,0.05); padding:7px 0; display:flex; justify-content:space-between;">
                    <span style="font-size:12px; color:#5a6a82;">Transfer Cost</span>
                    <span style="font-size:13px; font-weight:700; color:{cost_color};">${costs[i]:,.0f}</span>
                </div>
                <div style="border-bottom:1px solid rgba(255,255,255,0.05); padding:7px 0; display:flex; justify-content:space-between;">
                    <span style="font-size:12px; color:#5a6a82;">Cost / bps</span>
                    <span style="font-size:13px; color:#5a6a82;">{bps_cost:.2f} bps</span>
                </div>
                <div style="padding:7px 0; display:flex; justify-content:space-between;">
                    <span style="font-size:12px; color:#5a6a82;">Security Score</span>
                    <span style="font-size:13px; font-weight:700; color:#e8edf5;">{SECURITY_SCORES[proto]}/100</span>
                </div>
                <div style="margin-top:16px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="font-size:9px; color:#5a6a82; letter-spacing:1px; text-transform:uppercase;">Composite Score</span>
                        <span style="font-size:10px; color:{color}; font-weight:700;">{scores[i]}</span>
                    </div>
                    <div style="height:6px; background:#0e1420; border-radius:3px; overflow:hidden;">
                        <div style="height:100%; width:{scores[i]}%; background:{color}; border-radius:3px;"></div>
                    </div>
                </div>
            </div>"""

        components.html(f"""
        <div style="display:flex; gap:16px; font-family:Syne,sans-serif; color:#e8edf5;">
            {"".join(build_card(i, p) for i, p in enumerate(protocols))}
        </div>""", height=420)

        st.markdown("<br>", unsafe_allow_html=True)

        # Radar + Bar
        categories      = ["Security", "Institutional", "Speed", "Cost Efficiency", "Chain Coverage"]
        coverage_scores = {"Chainlink CCIP": 40, "LayerZero": 100, "Wormhole": 70}
        speed_scores    = {"Chainlink CCIP": 20, "LayerZero": 95,  "Wormhole": 65}
        cost_eff_scores = {"Chainlink CCIP": 30, "LayerZero": 95,  "Wormhole": 70}

        fig_radar = go.Figure()
        for proto in protocols:
            vals = [SECURITY_SCORES[proto], INSTITUTION_SCORES[proto], speed_scores[proto], cost_eff_scores[proto], coverage_scores[proto]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=categories+[categories[0]],
                fill='toself', name=proto,
                line_color=PROTOCOL_COLORS[proto], fillcolor=hex_to_rgba(PROTOCOL_COLORS[proto], 0.13), line_width=2,
            ))
        fig_radar.update_layout(
            polar=dict(bgcolor="#141c2b",
                radialaxis=dict(visible=True, range=[0,100], color="#5a6a82", gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=9, color="#5a6a82")),
                angularaxis=dict(color="#e8edf5", gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=11))),
            paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
            font=dict(family="Syne", color="#e8edf5"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=40, b=40), height=420,
            title=dict(text="Protocol Capability Radar", font=dict(size=14, color="#5a6a82"), x=0.5),
        )

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=protocols, y=scores,
            marker_color=[PROTOCOL_COLORS[p] for p in protocols], marker_line_width=0,
            text=[str(s) for s in scores], textposition="outside",
            textfont=dict(size=13, color="#e8edf5"),
        ))
        fig_bar.update_layout(
            paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
            font=dict(family="Syne", color="#e8edf5"),
            yaxis=dict(range=[0,110], gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10, color="#5a6a82"),
                       title=dict(text="Composite Score", font=dict(size=11, color="#5a6a82"))),
            xaxis=dict(tickfont=dict(size=12)),
            margin=dict(t=40, b=20, l=60, r=20), height=320, showlegend=False,
            title=dict(text="Composite Score by Protocol", font=dict(size=14, color="#5a6a82"), x=0.5),
        )

        cc1, cc2 = st.columns([1.1, 1])
        with cc1: st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        with cc2: st.plotly_chart(fig_bar,  use_container_width=True, config={"displayModeBar": False})

        # Summary banner
        st.markdown(f"""
        <div style="background:rgba(0,229,160,0.05); border:1px solid rgba(0,229,160,0.2);
                    border-radius:12px; padding:20px 28px; margin-top:8px;">
            <div style="display:flex; gap:36px; flex-wrap:wrap; align-items:center;">
                <div>
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Recommended</div>
                    <div style="font-size:18px; font-weight:800; color:{wc};">{winner}</div>
                </div>
                <div>
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Best Latency</div>
                    <div style="font-size:22px; font-weight:800; color:#00e5a0; letter-spacing:-1px;">~{winner_latency} min</div>
                </div>
                <div>
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Transfer Cost</div>
                    <div style="font-size:22px; font-weight:800; color:#00e5a0; letter-spacing:-1px;">${winner_cost:,.0f}</div>
                </div>
                <div>
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Composite Score</div>
                    <div style="font-size:22px; font-weight:800; color:#00e5a0; letter-spacing:-1px;">{winner_score}/100</div>
                </div>
                <div style="flex:1; min-width:220px; font-size:12px; color:#5a6a82; line-height:1.6;
                            border-left:1px solid rgba(255,255,255,0.07); padding-left:24px;">
                    <strong style="color:#e8edf5; font-size:13px;">Why this choice?</strong><br>{winner_notes}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════
        # EXECUTE TRANSFER
        # ══════════════════════════════════════════════
        section_label("Execute Transfer")

        st.markdown(f"""
        <div style="background:#0e1420; border:1px solid rgba(255,255,255,0.07);
                    border-radius:12px; padding:20px 28px; margin-bottom:16px;">
            <div style="display:flex; gap:32px; flex-wrap:wrap;">
                <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Route</div>
                     <div style="font-size:15px; font-weight:700; color:#e8edf5;">{S.sim_from} → {S.sim_to}</div></div>
                <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Asset</div>
                     <div style="font-size:15px; font-weight:700; color:#e8edf5;">{S.sim_asset}</div></div>
                <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Amount</div>
                     <div style="font-size:15px; font-weight:700; color:#e8edf5;">${S.sim_amount:,.0f}</div></div>
                <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Via</div>
                     <div style="font-size:15px; font-weight:700; color:{wc};">{winner}</div></div>
                <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Est. Cost</div>
                     <div style="font-size:15px; font-weight:700; color:#00e5a0;">${winner_cost:,.0f}</div></div>
                <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Est. Time</div>
                     <div style="font-size:15px; font-weight:700; color:#00e5a0;">~{winner_latency} min</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("🚀 Execute Transfer (Simulation)", use_container_width=True, key="btn_execute"):
            tx_hash = "0x" + "".join(random.choices("abcdef0123456789", k=64))
            steps = [
                ("🔍 Validating compliance & KYC checks...", 0.6),
                ("📦 Locking tokens on source chain...", 0.8),
                (f"📡 Broadcasting to {winner} relay network...", 0.8),
                ("🔒 Awaiting protocol validation...", 1.0),
                ("✅ Minting tokens on destination chain...", 0.7),
            ]
            pb  = st.progress(0)
            box = st.empty()
            for idx, (msg, wait) in enumerate(steps):
                box.markdown(f'<div style="background:#141c2b; border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 18px; font-size:13px; color:#5a6a82;">{msg}</div>', unsafe_allow_html=True)
                pb.progress((idx + 1) / len(steps))
                time.sleep(wait)
            box.empty(); pb.empty()
            st.session_state.exec_done = True
            st.session_state.exec_tx   = tx_hash

        if st.session_state.exec_done and st.session_state.exec_tx:
            tx   = st.session_state.exec_tx
            recv = S.sim_amount - winner_cost
            st.markdown(f"""
            <div style="background:rgba(0,229,160,0.07); border:1px solid rgba(0,229,160,0.35);
                        border-radius:12px; padding:24px 28px; margin-top:8px;">
                <div style="font-size:22px; font-weight:800; color:#00e5a0; margin-bottom:16px;">✅ Transfer Confirmed</div>
                <div style="display:flex; gap:32px; flex-wrap:wrap; margin-bottom:16px;">
                    <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">From</div>
                         <div style="font-size:14px; font-weight:700; color:#e8edf5;">{S.sim_from}</div></div>
                    <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">To</div>
                         <div style="font-size:14px; font-weight:700; color:#e8edf5;">{S.sim_to}</div></div>
                    <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Amount Sent</div>
                         <div style="font-size:14px; font-weight:700; color:#e8edf5;">${S.sim_amount:,.0f}</div></div>
                    <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Amount Received</div>
                         <div style="font-size:14px; font-weight:700; color:#00e5a0;">${recv:,.0f}</div></div>
                    <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Protocol Fee</div>
                         <div style="font-size:14px; font-weight:700; color:#f97316;">${winner_cost:,.0f}</div></div>
                    <div><div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Protocol Used</div>
                         <div style="font-size:14px; font-weight:700; color:{wc};">{winner}</div></div>
                </div>
                <div style="background:#0e1420; border-radius:8px; padding:12px 16px;">
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">Transaction Hash</div>
                    <div style="font-size:11px; color:#1e8fff; word-break:break-all;">{tx}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════
        # SPLIT ROUTING
        # ══════════════════════════════════════════════
        section_label("Split Routing — Advanced")

        st.markdown("""
        <div style="font-size:13px; color:#5a6a82; margin-bottom:16px; line-height:1.6;">
            Split your transfer across two protocols simultaneously to optimise for
            <strong style="color:#e8edf5;">security + speed</strong> or
            <strong style="color:#e8edf5;">cost efficiency</strong>.
        </div>""", unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            split_strategy = st.selectbox("Split Strategy", [
                "Security + Speed  (70% CCIP / 30% LayerZero)",
                "Cost Optimised    (50% LayerZero / 50% Wormhole)",
                "Balanced          (50% CCIP / 50% LayerZero)",
            ], key="split_select")

        with sc2:
            if st.button("⚡ Run Split Simulation", use_container_width=True, key="btn_split"):
                if "Security + Speed" in split_strategy:
                    p1, p2, r1, r2, label = "Chainlink CCIP", "LayerZero", 0.70, 0.30, "Security + Speed"
                elif "Cost Optimised" in split_strategy:
                    p1, p2, r1, r2, label = "LayerZero", "Wormhole", 0.50, 0.50, "Cost Optimised"
                else:
                    p1, p2, r1, r2, label = "Chainlink CCIP", "LayerZero", 0.50, 0.50, "Balanced"

                amt1  = S.sim_amount * r1
                amt2  = S.sim_amount * r2
                c1v   = compute_cost(p1, amt1)
                c2v   = compute_cost(p2, amt2)
                p1i   = protocols.index(p1)
                p2i   = protocols.index(p2)
                total = c1v + c2v
                slat  = max(latencies[p1i], latencies[p2i])
                sav   = winner_cost - total
                savp  = (sav / winner_cost * 100) if winner_cost > 0 else 0

                st.session_state.split_done = True
                st.session_state.split_data = {
                    "p1": p1, "p2": p2, "r1": r1, "r2": r2, "label": label,
                    "amt1": amt1, "amt2": amt2, "c1": c1v, "c2": c2v,
                    "p1i": p1i, "p2i": p2i,
                    "total": total, "lat": slat,
                    "sav": sav, "savp": savp, "single": winner_cost,
                }

        if st.session_state.split_done and st.session_state.split_data:
            d     = st.session_state.split_data
            c1s   = PROTOCOL_COLORS[d["p1"]]
            c2s   = PROTOCOL_COLORS[d["p2"]]
            pct1  = int(d["r1"] * 100)
            pct2  = int(d["r2"] * 100)
            sc    = "#00e5a0" if d["sav"] >= 0 else "#ff3b5c"
            ssign = "−" if d["sav"] < 0 else "+"

            components.html(f"""
            <div style="font-family:Syne,sans-serif; color:#e8edf5; margin-top:8px;">
                <div style="margin-bottom:20px;">
                    <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">Transfer Allocation</div>
                    <div style="display:flex; border-radius:8px; overflow:hidden; height:36px;">
                        <div style="width:{pct1}%; background:{c1s}; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;">{d['p1']} {pct1}%</div>
                        <div style="width:{pct2}%; background:{c2s}; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;">{d['p2']} {pct2}%</div>
                    </div>
                </div>
                <div style="display:flex; gap:16px; margin-bottom:20px;">
                    <div style="flex:1; background:#141c2b; border:1px solid {c1s}55; border-radius:10px; padding:16px;">
                        <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">Leg 1</div>
                        <div style="font-size:15px; font-weight:700; color:{c1s}; margin-bottom:12px;">{d['p1']}</div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-size:12px; color:#5a6a82;">Amount</span>
                            <span style="font-size:13px; font-weight:700;">${d['amt1']:,.0f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-size:12px; color:#5a6a82;">Fee</span>
                            <span style="font-size:13px; font-weight:700; color:#f97316;">${d['c1']:,.0f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:12px; color:#5a6a82;">Latency</span>
                            <span style="font-size:13px; font-weight:700; color:#00e5a0;">~{latencies[d['p1i']]} min</span>
                        </div>
                    </div>
                    <div style="flex:1; background:#141c2b; border:1px solid {c2s}55; border-radius:10px; padding:16px;">
                        <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">Leg 2</div>
                        <div style="font-size:15px; font-weight:700; color:{c2s}; margin-bottom:12px;">{d['p2']}</div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-size:12px; color:#5a6a82;">Amount</span>
                            <span style="font-size:13px; font-weight:700;">${d['amt2']:,.0f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-size:12px; color:#5a6a82;">Fee</span>
                            <span style="font-size:13px; font-weight:700; color:#f97316;">${d['c2']:,.0f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:12px; color:#5a6a82;">Latency</span>
                            <span style="font-size:13px; font-weight:700; color:#00e5a0;">~{latencies[d['p2i']]} min</span>
                        </div>
                    </div>
                </div>
                <div style="background:rgba(0,229,160,0.06); border:1px solid rgba(0,229,160,0.25); border-radius:10px; padding:16px; display:flex; gap:32px; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Total Split Cost</div>
                        <div style="font-size:20px; font-weight:800; color:#00e5a0;">${d['total']:,.0f}</div>
                    </div>
                    <div>
                        <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">vs Single Protocol</div>
                        <div style="font-size:20px; font-weight:800; color:#e8edf5;">${d['single']:,.0f}</div>
                    </div>
                    <div>
                        <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Saving</div>
                        <div style="font-size:20px; font-weight:800; color:{sc};">{ssign}${abs(d['sav']):,.0f} ({abs(d['savp']):.1f}%)</div>
                    </div>
                    <div>
                        <div style="font-size:9px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px;">Effective Latency</div>
                        <div style="font-size:20px; font-weight:800; color:#1e8fff;">~{d['lat']} min</div>
                    </div>
                    <div style="flex:1; min-width:180px; font-size:12px; color:#5a6a82; line-height:1.6; border-left:1px solid rgba(255,255,255,0.07); padding-left:20px;">
                        <strong style="color:#e8edf5;">Strategy: {d['label']}</strong><br>
                        Both legs execute in parallel. Effective latency = slowest leg.
                        Fixed fees apply per leg — splitting is most beneficial on large transfers.
                    </div>
                </div>
            </div>""", height=420)

# ═════════════════════════════════════════════════════════════
# TAB 2 — PROTOCOL COMPARISON
# ═════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Protocol Comparison — Architecture Deep Dive")

    comparison_data = {
        "Feature": ["Security Model","Avg. Latency","Base Fee","Decentralization","Institutional Grade","Chains Supported","RWA/Treasury Adoption","Risk Management Network","Notable Hacks"],
        "Chainlink CCIP": ["Dual Oracle + RMN","~20 min","$15–50","High","✓ Yes","~20","High (BUIDL, Swift)","✓ Dedicated RMN","None"],
        "LayerZero":      ["DVN (Configurable)","~2–5 min","$0.5–5","Medium","Partial","70+","Growing","✗ None","None"],
        "Wormhole":       ["Guardian Network (19)","~5–15 min","$1–10","Medium-Low","Partial","35+","Moderate","✗ None","$320M (2022, patched)"],
    }
    df_compare = pd.DataFrame(comparison_data)

    def color_cells(val):
        if val in ["High","✓ Yes","✓ Dedicated RMN","None","High (BUIDL, Swift)"]:
            return "background-color:rgba(0,229,160,0.08);color:#00e5a0;"
        elif val in ["Medium","Partial","Growing","Moderate"]:
            return "background-color:rgba(30,143,255,0.08);color:#1e8fff;"
        elif val in ["Medium-Low","✗ None","$320M (2022, patched)"]:
            return "background-color:rgba(255,59,92,0.08);color:#ff3b5c;"
        return ""

    st.dataframe(df_compare.set_index("Feature").style.map(color_cells), use_container_width=True, height=385)
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Static Score Comparison")

    protocols = list(COST_PARAMS.keys())
    colors    = [PROTOCOL_COLORS[p] for p in protocols]
    c1, c2, c3 = st.columns(3)

    with c1:
        f = go.Figure(go.Bar(x=protocols, y=[SECURITY_SCORES[p] for p in protocols],
            marker_color=colors, marker_line_width=0,
            text=[str(SECURITY_SCORES[p]) for p in protocols], textposition="outside", textfont=dict(size=12,color="#e8edf5")))
        f.update_layout(title=dict(text="Security Score /100",font=dict(size=13,color="#5a6a82"),x=0.5),
            paper_bgcolor="#0e1420",plot_bgcolor="#0e1420",
            yaxis=dict(range=[0,115],gridcolor="rgba(255,255,255,0.04)",tickfont=dict(size=9,color="#5a6a82")),
            xaxis=dict(tickfont=dict(size=11)),margin=dict(t=50,b=10,l=10,r=10),height=280,showlegend=False)
        st.plotly_chart(f, use_container_width=True, config={"displayModeBar": False})

    with c2:
        f2 = go.Figure(go.Bar(x=protocols, y=[INSTITUTION_SCORES[p] for p in protocols],
            marker_color=colors, marker_line_width=0,
            text=[str(INSTITUTION_SCORES[p]) for p in protocols], textposition="outside", textfont=dict(size=12,color="#e8edf5")))
        f2.update_layout(title=dict(text="Institutional Score /100",font=dict(size=13,color="#5a6a82"),x=0.5),
            paper_bgcolor="#0e1420",plot_bgcolor="#0e1420",
            yaxis=dict(range=[0,115],gridcolor="rgba(255,255,255,0.04)",tickfont=dict(size=9,color="#5a6a82")),
            xaxis=dict(tickfont=dict(size=11)),margin=dict(t=50,b=10,l=10,r=10),height=280,showlegend=False)
        st.plotly_chart(f2, use_container_width=True, config={"displayModeBar": False})

    with c3:
        lat_avg = {p: round(sum(LATENCY[k][i] for k in LATENCY)/len(LATENCY)) for i,p in enumerate(protocols)}
        f3 = go.Figure(go.Bar(x=protocols, y=list(lat_avg.values()),
            marker_color=colors, marker_line_width=0,
            text=[f"{v} min" for v in lat_avg.values()], textposition="outside", textfont=dict(size=12,color="#e8edf5")))
        f3.update_layout(title=dict(text="Avg. Latency (min)",font=dict(size=13,color="#5a6a82"),x=0.5),
            paper_bgcolor="#0e1420",plot_bgcolor="#0e1420",
            yaxis=dict(range=[0,35],gridcolor="rgba(255,255,255,0.04)",tickfont=dict(size=9,color="#5a6a82"),
                       title=dict(text="minutes",font=dict(size=10,color="#5a6a82"))),
            xaxis=dict(tickfont=dict(size=11)),margin=dict(t=50,b=10,l=40,r=10),height=280,showlegend=False)
        st.plotly_chart(f3, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Deep Dive — Protocol Architecture")

    for proto in protocols:
        color = PROTOCOL_COLORS[proto]
        info  = PROTOCOL_INFO[proto]
        with st.expander(f"  {proto}"):
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown(f"""
                <div style="font-size:10px;color:#5a6a82;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">Security Model</div>
                <div style="font-size:14px;font-weight:600;color:{color};margin-bottom:16px;">{info['sec_model']}</div>
                <div style="font-size:10px;color:#5a6a82;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">Chains Supported</div>
                <div style="font-size:14px;font-weight:600;margin-bottom:16px;">{info['chains']}</div>
                <div style="font-size:10px;color:#5a6a82;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">RWA Adoption</div>
                <div style="font-size:14px;font-weight:600;margin-bottom:16px;">{info['rwa_adoption']}</div>
                """, unsafe_allow_html=True)
            with ec2:
                hc = "#ff3b5c" if info['hacks'] != "None" else "#00e5a0"
                st.markdown(f"""
                <div style="font-size:10px;color:#5a6a82;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">Notable Hacks</div>
                <div style="font-size:14px;font-weight:600;color:{hc};margin-bottom:16px;">{info['hacks']}</div>
                <div style="font-size:10px;color:#5a6a82;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">Analysis</div>
                <div style="font-size:13px;color:#5a6a82;line-height:1.6;">{info['notes']}</div>
                """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# TAB 3 — BRIDGE HACKS
# ═════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    section_label("The Weakest Link — Bridge Hack History (2021–2024)")

    df_hacks = pd.DataFrame(BRIDGE_HACKS)

    k1, k2, k3 = st.columns(3)
    with k1: st.metric("Total Losses", "$2.8B+")
    with k2: st.metric("Incidents Tracked", "20+")
    with k3: st.metric("Peak Year", "2022")

    st.markdown("<br>", unsafe_allow_html=True)

    fig_hacks = go.Figure(go.Bar(
        x=df_hacks["Protocol"], y=df_hacks["Amount ($M)"],
        marker_color=["#ff3b5c","#ff6b35","#f97316","#ff3b5c","#ff6b35","#f97316"],
        marker_line_width=0,
        text=[f"${v}M" for v in df_hacks["Amount ($M)"]],
        textposition="outside", textfont=dict(size=11, color="#e8edf5"),
    ))
    fig_hacks.update_layout(
        paper_bgcolor="#0e1420", plot_bgcolor="#0e1420",
        font=dict(family="Syne", color="#e8edf5"),
        yaxis=dict(title=dict(text="Amount Lost ($M)",font=dict(size=11,color="#5a6a82")),
                   gridcolor="rgba(255,255,255,0.04)",tickfont=dict(size=10,color="#5a6a82"),range=[0,720]),
        xaxis=dict(tickfont=dict(size=12)),
        margin=dict(t=20,b=20,l=60,r=20), height=340, showlegend=False,
    )
    st.plotly_chart(fig_hacks, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Incident Details")

    def color_amount(val):
        if isinstance(val, (int, float)):
            if val >= 500:   return "color:#ff3b5c;font-weight:bold;"
            elif val >= 150: return "color:#f97316;font-weight:bold;"
            else:            return "color:#ffd166;font-weight:bold;"
        return ""

    st.dataframe(df_hacks.set_index("Protocol").style.map(color_amount, subset=["Amount ($M)"]),
                 use_container_width=True, height=270)

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Why Bridges Fail — Root Cause Analysis")

    causes = {"Validator Centralization": 45, "Smart Contract Bugs": 30, "Key Management Failures": 15, "Upgrade Logic Flaws": 10}
    fig_pie = go.Figure(go.Pie(
        labels=list(causes.keys()), values=list(causes.values()), hole=0.55,
        marker=dict(colors=["#ff3b5c","#f97316","#ffd166","#ff6b35"], line=dict(color="#0e1420", width=2)),
        textfont=dict(size=12), textinfo="percent+label",
    ))
    fig_pie.update_layout(
        paper_bgcolor="#0e1420", font=dict(family="Syne", color="#e8edf5"),
        showlegend=False, margin=dict(t=20,b=20,l=20,r=20), height=340,
        annotations=[dict(text="Root<br>Causes", x=0.5, y=0.5, font=dict(size=13, color="#5a6a82"), showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    st.markdown("""
    <div style="background:rgba(255,59,92,0.05); border:1px solid rgba(255,59,92,0.2); border-radius:12px; padding:20px 24px; margin-top:8px;">
        <div style="font-size:10px; color:#5a6a82; letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">Key Takeaway</div>
        <div style="font-size:14px; color:#e8edf5; line-height:1.7;">
            The $2.8B in bridge losses is not random — it follows a clear pattern. Every major exploit
            exploited either <strong style="color:#ff3b5c;">validator centralization</strong> (too few nodes, key leakage),
            <strong style="color:#f97316;">smart contract logic flaws</strong> (signature bypass, replay attacks),
            or <strong style="color:#ffd166;">governance/upgrade failures</strong>.
            Modern protocols like CCIP, LayerZero, and Wormhole each attempt to address these
            — but with different architectural trade-offs in security vs. speed vs. cost.
        </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:24px; border-top:1px solid rgba(255,255,255,0.07);">
    <div style="font-size:10px; color:#5a6a82; letter-spacing:2px;">
        CROSSGUARD · FNCE313 · GROUP 2, TEAM 5 · SINGAPORE MANAGEMENT UNIVERSITY · 2026
    </div>
    <div style="font-size:12px; color:#5a6a82; margin-top:6px;">
        Data is simulated for academic purposes. Sources: Chainlink, LayerZero, Wormhole documentation · RWA.xyz · DeFiLlama
    </div>
</div>""", unsafe_allow_html=True)