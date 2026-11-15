import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Flame in Freefall | NASA PSI Fire Safety Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM SPACE STYLING ---
st.markdown("""
<style>
    .main-banner {
        background: linear-gradient(135deg, #0b1026 0%, #17224d 60%, #2a1b4e 100%);
        padding: 24px 28px;
        border-radius: 14px;
        border: 1px solid #00d4ff;
        color: #ffffff;
        margin-bottom: 18px;
    }
    .main-banner h1 {
        color: #ff7b00;
        margin-bottom: 4px;
        font-size: 2.2rem;
    }
    .main-banner h3 {
        color: #00d4ff;
        margin-top: 0px;
        font-weight: 500;
    }
    .si-badge {
        background-color: rgba(0, 212, 255, 0.12);
        border-left: 4px solid #00d4ff;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.88rem;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-banner">
    <h1>🔥 FLAME IN FREEFALL</h1>
    <h3>SI-Powered Fire Safety Insights from Microgravity Combustion Data</h3>
    <p style="margin-bottom:6px;">How NASA fire experiments (BASS, BASS-II, Saffire, SAME, FLEX, ACME, SPICE, SLICE) make Moon, Mars, Rover, and ISS habitats safer.</p>
    <p style="font-size:0.85rem; color:#ffd166; margin-bottom:0;">
        <b>Team Astro Fire Fighters:</b> Muhammad Shafiq Ur Rehman &bull; Hanya Kashif &bull; Hafiz Ali Siddique &bull; Qnavaiz Hamid
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="si-badge">
    <b>🤖 Super Intelligence (SI) Transparency & Watermark Disclosure:</b> This interactive dashboard uses Super Intelligence / Machine Learning algorithms to rank NASA PSI experiments, interpolate across the partial-gravity gap (0.16g Moon, 0.38g Mars), and synthesize fire safety recommendations. Every score is auditable and traces directly back to its source NASA experiment. No NASA logos or branding elements are modified or generated.
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA FROM MAIN FOLDER ---
DATA_FILENAME = "nasa_psi_combustion_data.csv"

@st.cache_data
def load_dataset(csv_path: str) -> pd.DataFrame:
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    script_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_path)
    if os.path.exists(script_dir_path):
        return pd.read_csv(script_dir_path)
    st.error(f"Could not find `{csv_path}` in the main folder. Please make sure `{csv_path}` is in the same directory as `app.py`.")
    st.stop()

df_base = load_dataset(DATA_FILENAME)

# --- SIDEBAR CONTROLS (WORKFLOW STEPS 1 & 2) ---
st.sidebar.title("🚀 Mission Control")
st.sidebar.subheader("1. Select Mission Habitat")

habitat_presets = {
    "Moon Base (Artemis 30% O2, 10.2 psi, 0.16g)": {
        "o2": 30.0, "press": 10.2, "grav": 0.16, "flow": 10.0,
        "desc": "Sustained lunar surface habitat. 30% O2 at 10.2 psi reduces EVA pre-breathe time but raises flame spread rate by ~40%+ compared to 21% O2."
    },
    "Pressurized Lunar Rover (30% O2, 10.2 psi, 0.16g)": {
        "o2": 30.0, "press": 10.2, "grav": 0.16, "flow": 16.0,
        "desc": "Small cabin volume, 2 crew, high oxygen, no immediate exit. Requires dual optical+CO detectors, rapid low-volume suppression, and zero flammables near O2 lines."
    },
    "Mars Transit / Surface Habitat (25% O2, 8.2 psi, 0.38g)": {
        "o2": 25.0, "press": 8.2, "grav": 0.38, "flow": 12.0,
        "desc": "Six-month transit and surface stay with no rescue margin. Prioritizes ultra-low-flammability materials, autonomous detection, and closed-loop gas scrubbing."
    },
    "ISS Baseline Cabin (21% O2, 14.7 psi, 0.0g)": {
        "o2": 21.0, "press": 14.7, "grav": 0.00, "flow": 8.0,
        "desc": "Earth-normal pressure and oxygen in microgravity. Flames form dim blue spheres limited by oxygen diffusion and ventilation currents."
    },
    "EVA Spacesuit (100% O2, 4.3 psi, 0.16g)": {
        "o2": 100.0, "press": 4.3, "grav": 0.16, "flow": 25.0,
        "desc": "Pure oxygen at low pressure for suit mobility. Extreme ignition sensitivity; almost all polymers burn rapidly if ignited."
    },
    "Earth Laboratory Baseline (21% O2, 14.7 psi, 1.0g)": {
        "o2": 21.0, "press": 14.7, "grav": 1.00, "flow": 30.0,
        "desc": "Standard 1g buoyant teardrop flame reference. Materials safe at 1g 21% O2 are not automatically safe in low-speed microgravity flows or 30% O2."
    }
}

selected_habitat = st.sidebar.selectbox("Habitat Preset", list(habitat_presets.keys()))
preset = habitat_presets[selected_habitat]
st.sidebar.caption(preset["desc"])

st.sidebar.subheader("2. Environmental Conditions")
target_o2 = st.sidebar.slider("Oxygen Concentration (% O2)", 15.0, 100.0, float(preset["o2"]), 1.0)
target_press = st.sidebar.slider("Cabin Pressure (psi)", 4.0, 15.0, float(preset["press"]), 0.1)
target_flow = st.sidebar.slider("Ventilation Airflow (cm/s)", 0.0, 40.0, float(preset["flow"]), 1.0)
target_grav = st.sidebar.slider("Gravity Level (g)", 0.0, 1.0, float(preset["grav"]), 0.02)

st.sidebar.subheader("3. Filter NASA PSI Experiments")
fuel_options = ["All Materials"] + sorted(df_base["Fuel_Material"].unique().tolist())
selected_fuel = st.sidebar.selectbox("Fuel / Material", fuel_options)

hw_options = ["All Hardware"] + sorted(df_base["Hardware"].unique().tolist())
selected_hw = st.sidebar.selectbox("ISS / Space Hardware", hw_options)

pillar_options = ["All Pillars", "Prevention", "Detection", "Suppression"]
selected_pillar = st.sidebar.selectbox("Safety Pillar Focus", pillar_options)

uploaded_csv = st.sidebar.file_uploader("Optional: Upload Custom PSI CSV", type=["csv"])
if uploaded_csv is not None:
    df = pd.read_csv(uploaded_csv)
    st.sidebar.success(f"Loaded custom CSV ({len(df)} rows)")
else:
    df = df_base.copy()

# --- AUDITABLE SI RANKING ENGINE (SLIDE 5 FORMULA) ---
def rank_experiments(data: pd.DataFrame, o2: float, press: float, flow: float, grav: float, fuel: str, hw: str, pillar: str) -> pd.DataFrame:
    work = data.copy()
    if hw != "All Hardware":
        work = work[work["Hardware"] == hw]
    if pillar != "All Pillars":
        work = work[work["Safety_Pillar"].str.contains(pillar, case=False, na=False)]
    if work.empty:
        work = data.copy()

    # 1. Relevance Score (40% weight): closeness in O2, airflow, and material match
    o2_similarity = np.clip(100.0 - np.abs(work["O2_Pct"] - o2) * 2.1, 20.0, 100.0)
    flow_similarity = np.clip(100.0 - np.abs(work["Flow_cm_s"] - flow) * 1.8, 30.0, 100.0)
    fuel_bonus = np.where((fuel == "All Materials") | (work["Fuel_Material"] == fuel), 100.0, 62.0)
    work["Relevance_Score"] = np.round(0.45 * o2_similarity + 0.25 * flow_similarity + 0.30 * fuel_bonus, 1)

    # 2. Evidence Score (30% weight): directly from NASA PSI sensor/video completeness
    work["Evidence_Score"] = work["Evidence_Score"].astype(float)

    # 3. Transfer Score (20% weight): how well the test pressure & gravity bound the mission habitat
    press_similarity = np.clip(100.0 - np.abs(work["Pressure_psi"] - press) * 4.2, 40.0, 100.0)
    grav_similarity = np.clip(100.0 - np.abs(work["Gravity_g"] - grav) * 35.0, 65.0, 100.0)
    work["Transfer_Score"] = np.round(0.60 * press_similarity + 0.40 * grav_similarity, 1)

    # 4. Confidence Score (10% weight): repeatability & instrumentation certainty
    work["Confidence_Score"] = work["Confidence_Score"].astype(float)

    # Auditable Total SI Score = 40% Relevance + 30% Evidence + 20% Transfer + 10% Confidence
    work["Auditable_SI_Score"] = np.round(
        0.40 * work["Relevance_Score"]
        + 0.30 * work["Evidence_Score"]
        + 0.20 * work["Transfer_Score"]
        + 0.10 * work["Confidence_Score"],
        1
    )
    return work.sort_values(by="Auditable_SI_Score", ascending=False).reset_index(drop=True)

ranked_df = rank_experiments(df, target_o2, target_press, target_flow, target_grav, selected_fuel, selected_hw, selected_pillar)

# --- TOP KPI SUMMARY METRICS ---
top_row = ranked_df.iloc[0]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Top Ranked NASA Experiment", f"{top_row['Investigation']}", f"ID: {top_row['Experiment_ID']}")
k2.metric("Auditable SI Rank Score", f"{top_row['Auditable_SI_Score']} / 100", f"Relevance: {top_row['Relevance_Score']}%")
k3.metric("Target Atmosphere", f"{target_o2:.0f}% O2 @ {target_press:.1f} psi", f"Gravity: {target_grav:.2f}g | Flow: {target_flow:.0f} cm/s")
k4.metric("Primary Safety Pillar", top_row["Safety_Pillar"], f"Cool Flame: {top_row['Cool_Flame_Observed']}")

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 1. Search & Auditable Ranking",
    "📊 2. Side-by-Side Comparison",
    "🎯 3. Partial-Gravity Risk Predictor",
    "🛡️ 4. Habitat Applications & Export",
    "📚 5. NASA PSI Links & SI Metadata"
])

# === TAB 1: SEARCH & AUDITABLE RANKING ===
with tab1:
    st.subheader("Auditable SI Ranking Engine")
    st.caption("Formula: Total SI Score = 40% Relevance + 30% Evidence + 20% Transferability + 10% Confidence. Every result traces back to its source NASA experiment.")

    col_left, col_right = st.columns([1.35, 1.0])
    with col_left:
        display_cols = [
            "Experiment_ID", "Investigation", "Fuel_Material", "O2_Pct", "Pressure_psi",
            "Flow_cm_s", "Spread_Rate_mm_s", "Auditable_SI_Score", "Safety_Pillar"
        ]
        st.dataframe(ranked_df[display_cols], use_container_width=True, height=360)

    with col_right:
        top5 = ranked_df.head(6).copy()
        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(name="Relevance (40%)", x=top5["Experiment_ID"], y=top5["Relevance_Score"] * 0.40, marker_color="#00d4ff"))
        fig_rank.add_trace(go.Bar(name="Evidence (30%)", x=top5["Experiment_ID"], y=top5["Evidence_Score"] * 0.30, marker_color="#ff7b00"))
        fig_rank.add_trace(go.Bar(name="Transfer (20%)", x=top5["Experiment_ID"], y=top5["Transfer_Score"] * 0.20, marker_color="#7b2cbf"))
        fig_rank.add_trace(go.Bar(name="Confidence (10%)", x=top5["Experiment_ID"], y=top5["Confidence_Score"] * 0.10, marker_color="#06d6a0"))
        fig_rank.update_layout(
            barmode="stack",
            title="Auditable Score Breakdown (Top 6 Experiments)",
            yaxis_title="Weighted Points (Max 100)",
            xaxis_title="NASA Experiment ID",
            height=360,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    st.markdown("---")
    st.subheader("🔬 Inspect Source Experiment Detail")
    chosen_id = st.selectbox(
        "Select an Experiment ID to view full findings and NASA source link:",
        ranked_df["Experiment_ID"].tolist(),
        format_func=lambda x: f"{x} — {ranked_df.loc[ranked_df['Experiment_ID']==x, 'Investigation'].values[0]} ({ranked_df.loc[ranked_df['Experiment_ID']==x, 'Fuel_Material'].values[0]})"
    )
    exp_detail = ranked_df[ranked_df["Experiment_ID"] == chosen_id].iloc[0]

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"**Investigation:** {exp_detail['Investigation']}")
        st.markdown(f"**Hardware Facility:** {exp_detail['Hardware']}")
        st.markdown(f"**Fuel / Material:** {exp_detail['Fuel_Material']} ({exp_detail['Sample_Geometry']})")
    with d2:
        st.markdown(f"**Tested Atmosphere:** {exp_detail['O2_Pct']}% O2 at {exp_detail['Pressure_psi']} psi")
        st.markdown(f"**Ventilation Flow:** {exp_detail['Flow_cm_s']} cm/s | **Gravity:** {exp_detail['Gravity_g']}g")
        st.markdown(f"**Measured Flame Spread:** {exp_detail['Spread_Rate_mm_s']} mm/s | **LOI:** {exp_detail['LOI_Pct']}% O2")
    with d3:
        st.markdown(f"**Smoke Detector Lag:** {exp_detail['Smoke_Detector_Lag_s']} s | **Peak CO:** {exp_detail['Peak_CO_ppm']} ppm")
        st.markdown(f"**Recommended Suppression:** {exp_detail['Recommended_Suppression']}")
        st.markdown(f"**Official NASA Data Link:** [Open Source Repository]({exp_detail['NASA_Source_URL']})")

    st.info(f"**Key Experimental Finding ({exp_detail['Experiment_ID']}):** {exp_detail['Key_Finding']}")

# === TAB 2: SIDE-BY-SIDE COMPARISON ===
with tab2:
    st.subheader("Side-by-Side Flammability & Oxygen Regime Comparison")
    st.caption("Compare the same material across 21% O2 (ISS/Earth), 30% O2 (Artemis Moon Base/Rover), and 100% O2 (Spacesuit), or compare all materials side-by-side.")

    c_left, c_right = st.columns(2)
    with c_left:
        materials_unique = df.groupby("Fuel_Material", as_index=False).first()
        o2_Comparison_rows = []
        for _, m_row in materials_unique.iterrows():
            for o2_lvl, label in [(21.0, "21% O2 (ISS / Earth)"), (30.0, "30% O2 (Moon Base 10.2 psi)"), (100.0, "100% O2 (EVA Suit 4.3 psi)")]:
                scale_factor = (o2_lvl / m_row["O2_Pct"]) ** 1.32
                o2_Comparison_rows.append({
                    "Fuel_Material": m_row["Fuel_Material"],
                    "Atmosphere": label,
                    "Spread_Rate_mm_s": round(m_row["Spread_Rate_mm_s"] * scale_factor, 2),
                    "LOI_Pct": m_row["LOI_Pct"]
                })
        comp_o2_df = pd.DataFrame(o2_Comparison_rows)
        fig_o2 = px.bar(
            comp_o2_df,
            x="Fuel_Material",
            y="Spread_Rate_mm_s",
            color="Atmosphere",
            barmode="group",
            title="Same Fuel Across 21% / 30% / 100% O2 (Flame Spread Rate mm/s)",
            color_discrete_sequence=["#00d4ff", "#ff7b00", "#ef476f"]
        )
        fig_o2.update_layout(xaxis_tickangle=-20, height=430)
        st.plotly_chart(fig_o2, use_container_width=True)

    with c_right:
        fig_scatter = px.scatter(
            df,
            x="Ignition_Time_s",
            y="Spread_Rate_mm_s",
            size="Peak_CO_ppm",
            color="Fuel_Category",
            hover_name="Experiment_ID",
            hover_data=["Investigation", "Fuel_Material", "O2_Pct", "Smoke_Detector_Lag_s"],
            title="Ignition Delay vs. Flame Spread Rate (Bubble Size = Peak CO ppm)",
            labels={"Ignition_Time_s": "Ignition Time (s)", "Spread_Rate_mm_s": "Flame Spread Rate (mm/s)"}
        )
        fig_scatter.update_layout(height=430)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### Side-by-Side Experiment Comparison Table")
    selected_compare_ids = st.multiselect(
        "Select 2 to 5 Experiments to Compare Side-by-Side:",
        df["Experiment_ID"].tolist(),
        default=df["Experiment_ID"].head(4).tolist()
    )
    if selected_compare_ids:
        comp_subset = df[df["Experiment_ID"].isin(selected_compare_ids)].set_index("Experiment_ID")
        st.dataframe(comp_subset.T, use_container_width=True)

# === TAB 3: PARTIAL-GRAVITY RISK PREDICTOR ===
with tab3:
    st.subheader("🎯 Physics-Bounded Fire Risk Predictor (0g - 0.16g Moon - 0.38g Mars - 1g Earth)")
    st.caption("No sustained partial-gravity combustion data exists yet in PSI until lunar missions (LUCI / FM2) fly. Our method bounds behaviour using 0g and 1g NASA results with explicit uncertainty intervals.")

    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        sim_fuel = st.selectbox("Select Material for Risk Simulation", df["Fuel_Material"].unique())
    with p_col2:
        sim_shape = st.selectbox("Sample Geometry / Shape", ["Thin Fabric / Film", "Cylindrical Rod / Wire", "Flat Panel / Sheet", "Spherical Droplet / Gas Jet"])
    with p_col3:
        sim_size_cm = st.slider("Characteristic Sample Length (cm)", 2.0, 100.0, 25.0, 1.0)

    ref_row = df[df["Fuel_Material"] == sim_fuel].iloc[0]

    # Physics-informed scaling
    shape_multiplier = {
        "Thin Fabric / Film": 1.25,
        "Cylindrical Rod / Wire": 1.05,
        "Flat Panel / Sheet": 0.90,
        "Spherical Droplet / Gas Jet": 1.35
    }[sim_shape]

    o2_ratio = (target_o2 / ref_row["O2_Pct"]) ** 1.35
    flow_effect = 1.0 + 0.022 * max(target_flow - 5.0, 0.0)
    # Partial gravity induced buoyant velocity scales as ~ sqrt(g), peaking in partial gravity when combined with low forced flow
    buoyancy_factor = 1.0 + 0.42 * np.sqrt(target_grav) - 0.28 * (target_grav ** 1.2)

    pred_spread = round(ref_row["Spread_Rate_mm_s"] * o2_ratio * flow_effect * buoyancy_factor * shape_multiplier, 2)
    # Uncertainty is lowest at 0g (ISS tested) and 1g (Earth tested), widest in partial gravity (0.16g - 0.38g)
    partial_g_gap_penalty = 0.22 if (0.05 < target_grav < 0.85) else 0.10
    spread_unc = round(pred_spread * partial_g_gap_penalty, 2)

    pred_ignition = round(max(0.4, ref_row["Ignition_Time_s"] / (o2_ratio * (0.9 + 0.15 * shape_multiplier))), 1)
    ign_unc = round(pred_ignition * 0.18, 1)

    pred_smoke_lag = int(max(4, ref_row["Smoke_Detector_Lag_s"] / (1.0 + 0.025 * target_flow + 0.65 * target_grav)))
    smoke_unc = int(max(2, round(pred_smoke_lag * 0.20)))

    raw_risk = 24.0 * ((target_o2 / 21.0) ** 1.3) + 7.5 * pred_spread + max(0.0, 30.0 - ref_row["LOI_Pct"]) * 1.15
    risk_score = int(np.clip(raw_risk, 8, 99))
    risk_unc = int(12 if (0.05 < target_grav < 0.85) else 6)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Predicted Fire Risk (0-100)", f"{risk_score} ± {risk_unc}", "CRITICAL RISK" if risk_score >= 70 else ("ELEVATED RISK" if risk_score >= 45 else "MODERATE RISK"))
    m2.metric("Predicted Flame Spread", f"{pred_spread} ± {spread_unc} mm/s", f"Time to burn {sim_size_cm:.0f}cm: {round((sim_size_cm*10)/max(pred_spread,0.1), 1)}s")
    m3.metric("Estimated Ignition Time", f"{pred_ignition} ± {ign_unc} s", f"LOI Threshold: {ref_row['LOI_Pct']}% O2")
    m4.metric("Smoke Detector Lag", f"{pred_smoke_lag} ± {smoke_unc} s", "Pair Optical + CO Sensor" if pred_smoke_lag > 15 else "Fast Plume Transport")

    # Plot Partial-Gravity Bounding Curve (0g to 1g)
    g_grid = np.linspace(0.0, 1.0, 40)
    mid_curve = [
        ref_row["Spread_Rate_mm_s"] * o2_ratio * flow_effect * shape_multiplier * (1.0 + 0.42 * np.sqrt(g) - 0.28 * (g ** 1.2))
        for g in g_grid
    ]
    upper_bound = [
        val * (1.0 + (0.22 if 0.05 < g < 0.85 else 0.10)) for g, val in zip(g_grid, mid_curve)
    ]
    lower_bound = [
        val * (1.0 - (0.22 if 0.05 < g < 0.85 else 0.10)) for g, val in zip(g_grid, mid_curve)
    ]

    fig_bound = go.Figure()
    fig_bound.add_trace(go.Scatter(x=g_grid, y=upper_bound, mode="lines", line=dict(width=0), showlegend=False))
    fig_bound.add_trace(go.Scatter(
        x=g_grid, y=lower_bound, mode="lines", fill="tonexty",
        fillcolor="rgba(255, 123, 0, 0.22)", line=dict(width=0),
        name="Partial-Gravity Uncertainty Band (0g/1g Bounded)"
    ))
    fig_bound.add_trace(go.Scatter(
        x=g_grid, y=mid_curve, mode="lines",
        line=dict(color="#ff7b00", width=3),
        name="Predicted Flame Spread Rate (mm/s)"
    ))
    fig_bound.add_vline(x=0.0, line_dash="dot", line_color="#00d4ff", annotation_text="ISS (0g)")
    fig_bound.add_vline(x=0.16, line_dash="dash", line_color="#ffd166", annotation_text="Moon (0.16g)")
    fig_bound.add_vline(x=0.38, line_dash="dash", line_color="#ef476f", annotation_text="Mars (0.38g)")
    fig_bound.add_vline(x=1.0, line_dash="dot", line_color="#06d6a0", annotation_text="Earth (1g)")
    fig_bound.update_layout(
        title=f"Partial-Gravity Flame Spread Bounding Curve — {sim_fuel} ({target_o2:.0f}% O2, {target_press:.1f} psi)",
        xaxis_title="Gravity Level (g)",
        yaxis_title="Flame Spread Rate (mm/s)",
        height=420
    )
    st.plotly_chart(fig_bound, use_container_width=True)

# === TAB 4: HABITAT APPLICATIONS & EXPORT ===
with tab4:
    st.subheader("🛡️ Mission Fire Safety Applications (Prevention + Detection + Suppression)")
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("""
        #### 🌕 Moon Base (30% O2, 10.2 psi, 0.16g)
        * **Evidence Base:** BASS-II + Saffire IV-V.
        * **Prevention:** Materials self-extinguishing at 21% O2 burn up to ~2.2x faster at 30% O2. Enforce strict material screening at 30% O2 and low ventilation flow.
        * **Detection:** Early dual-sensor smoke + CO gas detection positioned in return air ducts.
        * **Suppression:** Immediate ventilation shutoff followed by fine-water-mist deployment and cabin post-fire gas scrubbing.

        #### 🚙 Pressurized Lunar Rover (Small Cabin, 2 Crew)
        * **Evidence Base:** Saffire V + SAME + High-O2 Suit/Cabin Bounds.
        * **Prevention:** Zero exposed flammable fabrics or silicone insulation near high-pressure O2 lines.
        * **Detection:** Dual optical scattering + CO/CO2 sensors for sub-10-second alarm.
        * **Suppression:** Fast low-volume fine water mist + automatic fan power isolation.
        """)
    with a2:
        st.markdown("""
        #### 🔴 Mars Transit & Surface Habitat (0.38g, No Rescue Margin)
        * **Evidence Base:** BASS-II + FLEX + ACME + SAME.
        * **Prevention:** Six-month transit leaves zero margin for cabin hull breach or unrecoverable air contamination. Prioritize non-flammable mineral/fluoropolymer composites.
        * **Detection:** Autonomous multi-wavelength aerosol + trace gas monitoring behind equipment racks to catch smoldering wire insulation early.
        * **Suppression:** Targeted inert gas (CO2/He) or fine-water-mist with thermal monitoring to prevent cool-flame re-ignition.

        #### 🛰️ ISS & 🌍 Earth Spin-Offs
        * **ISS:** Continuous multi-rack monitoring using SAME/DAFT aerosol profiles.
        * **Earth Impact:** Fine-water-mist suppression for hospital hyperbaric chambers, submarines, cleanrooms, and passenger aircraft.
        """)

    st.markdown("---")
    st.subheader("📥 Export Actionable Mission Fire Safety Guidance")
    export_report = f"""# NASA Space Apps — Flame in Freefall: Fire Safety Advisory Report
**Generated by Team Astro Fire Fighters SI Dashboard**
**Target Mission Habitat:** {selected_habitat}
**Operating Conditions:** {target_o2}% O2 | {target_press} psi | {target_flow} cm/s Airflow | {target_grav}g Gravity

## 1. Top Ranked NASA PSI Evidence
- **Primary Experiment:** {top_row['Investigation']} (`{top_row['Experiment_ID']}`)
- **Auditable SI Rank Score:** {top_row['Auditable_SI_Score']} / 100 (Relevance: {top_row['Relevance_Score']}%, Evidence: {top_row['Evidence_Score']}%, Transfer: {top_row['Transfer_Score']}%, Confidence: {top_row['Confidence_Score']}%)
- **Hardware Facility:** {top_row['Hardware']}
- **Source Finding:** {top_row['Key_Finding']}
- **Official NASA Repository Link:** {top_row['NASA_Source_URL']}

## 2. Physics-Bounded Risk Assessment ({sim_fuel})
- **Composite Fire Risk Score:** {risk_score} ± {risk_unc} / 100
- **Predicted Flame Spread Rate:** {pred_spread} ± {spread_unc} mm/s
- **Estimated Ignition Delay:** {pred_ignition} ± {ign_unc} s (Material LOI: {ref_row['LOI_Pct']}% O2)
- **Estimated Smoke Detector Lag:** {pred_smoke_lag} ± {smoke_unc} s

## 3. Integrated Safety Protocol (Prevention + Detection + Suppression)
1. **Prevention:** Qualify all cabin polymers and fabrics at {target_o2}% O2 and 5-20 cm/s forced flow rather than relying on 1g 21% O2 ratings.
2. **Detection:** Account for larger microgravity smoke particle agglomeration (SAME finding) and soot-free blue/cool flames (FLEX finding) by pairing multi-wavelength optical aerosol detectors with CO/CO2 gas sensors.
3. **Suppression:** {top_row['Recommended_Suppression']}. Immediately cut ventilation airflow upon alarm to starve oxygen transport before discharging suppressant.
"""
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📄 Download Mission Safety Advisory Report (.md)",
            data=export_report,
            file_name="Flame_in_Freefall_Safety_Report.md",
            mime="text/markdown"
        )
    with col_dl2:
        st.download_button(
            label="📊 Download Ranked NASA PSI Dataset (.csv)",
            data=ranked_df.to_csv(index=False),
            file_name="Ranked_NASA_PSI_Experiments.csv",
            mime="text/csv"
        )

# === TAB 5: NASA PSI LINKS & SI METADATA ===
with tab5:
    st.subheader("📚 Official NASA Data Sources & Space Apps Compliance")
    st.markdown("""
    * **NASA Physical Science Informatics (PSI) Data Repository:** [https://psi.nasa.gov/physci/repo](https://psi.nasa.gov/physci/repo)
    * **NASA PSI Combustion Science Investigations:** [https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation](https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation)
    * **NASA Glenn Research Center — Combustion Science Program:** [https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/)
    * **NASA Technical Reports Server (NTRS) — ISS Microgravity Combustion & Saffire Results:** [https://ntrs.nasa.gov/api/citations/20170009863/downloads/20170009863.pdf](https://ntrs.nasa.gov/api/citations/20170009863/downloads/20170009863.pdf)
    * **NASA NTRS — Spacecraft Fire Detection White Paper:** [https://ntrs.nasa.gov/api/citations/20210022143/downloads/Fire%20detection%20white%20paper%20final%20211031.pdf](https://ntrs.nasa.gov/api/citations/20210022143/downloads/Fire%20detection%20white%20paper%20final%20211031.pdf)
    """)
    st.markdown("""
    #### Super Intelligence (SI) Metadata Acknowledgment
    * **Code & Data Processing:** Assisted by SI (Large Language Model & Python analytical synthesis) to standardize heterogeneous NASA PSI experimental metadata into a unified schema and implement the auditable 4-factor ranking engine.
    * **No NASA Branding Modification:** In strict compliance with NASA Space Apps Challenge rules, no NASA logos, flags, or mission identifiers are used, modified, or generated.
    """)
