import streamlit as st
import pandas as pd
from src.state import DraftState

# Page configuration
st.set_page_config(
    page_title="Jayme's ESPN Fantasy Draft Engine",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 15px;
    }
    .clock-banner-on {
        background-color: #DCFCE7;
        border-left: 6px solid #16A34A;
        padding: 14px 20px;
        border-radius: 8px;
        font-size: 1.35rem;
        font-weight: 700;
        color: #15803D;
        margin-bottom: 15px;
    }
    .clock-banner-off {
        background-color: #FEF3C7;
        border-left: 6px solid #D97706;
        padding: 12px 18px;
        border-radius: 6px;
        font-size: 1.15rem;
        font-weight: 600;
        color: #B45309;
        margin-bottom: 15px;
    }
    .roster-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .slot-filled {
        font-weight: 600;
        color: #0F172A;
    }
    .slot-open {
        color: #94A3B8;
        font-style: italic;
    }
    .steal-badge {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .reach-badge {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .tier-alert {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    .chip-out {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 2px 7px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid #F87171;
    }
    .chip-ir {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 2px 7px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid #FDBA74;
    }
    .chip-q {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 2px 7px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #FDE047;
    }
</style>
""", unsafe_allow_html=True)


# Initialize or sync session state
if 'draft_state' not in st.session_state:
    st.session_state.draft_state = DraftState()
else:
    # Auto-sync if disk has newer state
    st.session_state.draft_state.load_from_disk()


state = st.session_state.draft_state

# Ensure player pool has Omarion Hampton (ID 238)
if 238 not in state.all_players_df['player_id'].values:
    state.reload_player_pool()

# Sidebar - Settings, Controls, Custom Player & Draft History
with st.sidebar:
    st.title("🏈 Draft Controls")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        if st.button("↩️ Undo Pick", use_container_width=True):
            undone = state.undo_last_pick()
            if undone:
                st.success(f"Reverted {undone['player_name']}")
                st.rerun()
            else:
                st.info("No picks to undo.")
                
    with col_u2:
        if st.button("🔄 Reset Draft", use_container_width=True):
            # Also remove draft_state.json if reset
            import os
            from src.state import STATE_FILE
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
            st.session_state.draft_state = DraftState()
            st.rerun()

    if st.button("🚨 Sync Live News & Injuries", use_container_width=True):
        from src.injury_news_sync import sync_injuries_and_news
        with st.spinner("Syncing latest ESPN injury reports & news..."):
            sync_injuries_and_news()
            state.reload_player_pool()
            st.success("Synced latest injuries & news!")
            st.rerun()
    st.caption("🟢 **Background Monitor**: Active (Auto-syncs every 60s)")

    st.markdown("---")
    st.subheader("➕ Draft Unlisted / Custom Player")
    st.caption("If a surprise rookie/player is picked by anyone:")
    with st.form("custom_player_form", clear_on_submit=True):
        c_name = st.text_input("Player Name", placeholder="e.g. Omarion Hampton")
        c_pos = st.selectbox("Position", ["RB", "WR", "TE", "QB", "K", "DST"])
        col_ca, col_cb = st.columns(2)
        with col_ca:
            c_taken = st.form_submit_button("Taken by Other")
        with col_cb:
            c_jayme = st.form_submit_button("Draft to Jayme")
            
        if c_taken and c_name:
            state.draft_custom_player(c_name.strip(), pos=c_pos, for_jayme=False)
            st.success(f"Marked {c_name} as taken at pick #{state.current_pick - 1}")
            st.rerun()
        elif c_jayme and c_name:
            state.draft_custom_player(c_name.strip(), pos=c_pos, for_jayme=True)
            st.success(f"Drafted {c_name} to Jayme at pick #{state.current_pick - 1}")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Draft Information")
    st.write(f"**League:** {state.config.get('league_name', 'Fantasy Football 2026')}")
    st.write(f"**Teams:** {state.teams_count} Teams | **Format:** Full PPR (1.0)")
    st.write(f"**Jayme Slot:** #{state.jayme_slot} (Drafting at the Turn)")
    st.write(f"**Current Pick:** #{state.current_pick} (Round {state.current_round})")
    
    jayme_picks_str = ", ".join(str(p) for p in state.jayme_picks[:8]) + "..."
    st.caption(f"**Jayme's Picks:** {jayme_picks_str}")

    st.markdown("---")
    st.subheader("📜 Recent Pick Feed")
    if state.draft_history:
        for p in reversed(state.draft_history[-10:]):
            by_str = "⭐ **JAYME**" if p['drafted_by_jayme'] else f"Team (Pick {p['pick_num']})"
            st.markdown(f"**#{p['pick_num']}**: {p['player_name']} ({p['pos']} - {p['team']}) → {by_str}")
    else:
        st.write("Draft has not started yet. Click players below to record picks!")

# Main Draft Screen Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("<div class='main-header'>Jayme's ESPN Fantasy Draft Command Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>14-Team Full-PPR • Contextual EV & VORP Engine • Role-Adjusted Lineup Optimizer</div>", unsafe_allow_html=True)
with col_h2:
    st.metric("Total Picks Made", f"{len(state.draft_history)} / {state.total_picks}")

# Special Quick Button for Omarion Hampton if at pick 13 or unrecorded
hampton_drafted = any(p['player_name'].lower() == 'omarion hampton' for p in state.draft_history)
if not hampton_drafted:
    st.info("💡 **Pending Pick 13?** Omarion Hampton was drafted at 13. Click below to record it immediately:")
    if st.button("⚡ Record Omarion Hampton as Pick #13 (Advances to Jayme at #14 & #15)", type="primary"):
        state.draft_custom_player("Omarion Hampton", pos="RB", team="FA", for_jayme=False)
        st.success("Recorded Omarion Hampton at Pick 13. Jayme is now ON THE CLOCK at #14 & #15!")
        st.rerun()

# Live NFL Breaking News & Injury Status Banner
import json, os
ALERTS_FILE = os.path.join(os.path.dirname(__file__), "data", "live_news_alerts.json")
if os.path.exists(ALERTS_FILE):
    try:
        with open(ALERTS_FILE, "r") as f:
            live_alerts = json.load(f)
            
        out_players = live_alerts.get('out_players', [])
        ir_players = live_alerts.get('ir_pup_players', [])
        news_items = live_alerts.get('breaking_news', [])
        
        with st.expander(f"🚨 Live NFL News & Injury Radar (Sync: {live_alerts.get('last_updated', 'Active')})", expanded=True):
            cinj1, cinj2 = st.columns(2)
            with cinj1:
                st.markdown(f"**🔴 Ruled OUT / Inactive ({len(out_players)} players - 0 EV / Excluded):**")
                for p in out_players:
                    st.markdown(f"• **{p['name']}** ({p['pos']} - {p['team']}): <small style='color:#DC2626;'>{p['note']}</small>", unsafe_allow_html=True)
            with cinj2:
                st.markdown(f"**🟠 On IR / PUP ({len(ir_players)} players - Reserve Stash Only):**")
                for p in ir_players[:6]:
                    st.markdown(f"• **{p['name']}** ({p['pos']} - {p['team']}): <small style='color:#D97706;'>{p['note']}</small>", unsafe_allow_html=True)
                    
            if news_items:
                st.markdown("---")
                st.markdown("**📰 Recent Breaking NFL Headlines:**")
                for item in news_items[:3]:
                    st.markdown(f"• **{item.get('headline')}** — <small style='color:#6B7280;'>{item.get('description', '')[:90]}...</small>", unsafe_allow_html=True)
    except Exception as e:
        pass

# Dynamic On-The-Clock Banner
if state.is_jayme_turn:
    st.markdown(f"""
    <div class='clock-banner-on'>
        🚨 JAYME IS ON THE CLOCK! • Round {state.current_round}, Pick #{state.current_pick} (Back-to-Back Turn Pick!)
    </div>
    """, unsafe_allow_html=True)
else:
    gap = state.picks_until_next_turn
    next_pick = state.current_pick + gap
    st.markdown(f"""
    <div class='clock-banner-off'>
        ⏳ Currently Drafting: <strong>{state.current_drafter_name}</strong> (Pick #{state.current_pick}) &nbsp;|&nbsp; 
        Jayme picks in <strong>{gap} picks</strong> (at Pick #{next_pick})
    </div>
    """, unsafe_allow_html=True)

# Top Split View: Jayme's Roster vs Top Dynamic Recommendations
col_roster, col_recs = st.columns([1, 1])

slots = state.roster_manager.get_slot_allocations()
drafted_df = state.roster_manager.get_roster_dataframe()

with col_roster:
    st.subheader("🛡️ Jayme's Roster & Starting Needs")
    
    starters = [slots['QB'], slots['RB1'], slots['RB2'], slots['WR1'], slots['WR2'], slots['TE'], slots['FLEX'], slots['DST'], slots['K']]
    starting_pts = sum(p['context_ev'] for p in starters if p is not None)
    
    st.caption(f"Projected Starting Lineup EV: **{starting_pts:.1f} pts / season**")
    
    def render_slot(slot_name, player):
        if player:
            return f"**{slot_name}:** <span class='slot-filled'>{player['name']}</span> ({player['team']}) — <small>{player['context_ev']} pts</small>"
        else:
            return f"**{slot_name}:** <span class='slot-open'>[ OPEN - Needs Starter ]</span>"

    st.markdown(f"""
    <div class='roster-card'>
        {render_slot('QB', slots['QB'])}<br>
        {render_slot('RB1', slots['RB1'])}<br>
        {render_slot('RB2', slots['RB2'])}<br>
        {render_slot('WR1', slots['WR1'])}<br>
        {render_slot('WR2', slots['WR2'])}<br>
        {render_slot('TE', slots['TE'])}<br>
        {render_slot('FLEX', slots['FLEX'])}<br>
        {render_slot('D/ST', slots['DST'])}<br>
        {render_slot('K', slots['K'])}
    </div>
    """, unsafe_allow_html=True)
    
    if slots['BENCH']:
        bench_names = ", ".join([f"{p['name']} ({p['pos']})" for p in slots['BENCH']])
        st.markdown(f"**Bench ({len(slots['BENCH'])}/7):** {bench_names}")
    else:
        st.markdown("**Bench:** 0/7 slots filled")

with col_recs:
    st.subheader("🎯 Optimal Picks for Jayme's Next Selection")
    st.caption("Ranked by Marginal EV Addition to her specific team + 14-team positional urgency.")
    
    avail_df = state.get_available_players_df(exclude_out=True)
    top_5 = avail_df.head(5)
    
    for _, p in top_5.iterrows():
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            st.markdown(f"**{p['name']}** ({p['pos']} - {p['team']})")
            st.caption(f"{p['role_addition']}")
        with c2:
            st.markdown(f"**+{p['marginal_ev']:.1f} EV** <small>(Tot: {p['context_ev']:.0f})</small>", unsafe_allow_html=True)
            if p['espn_value_delta'] >= 5:
                st.markdown(f"<span class='steal-badge'>ESPN Steal (+{p['espn_value_delta']:.0f})</span>", unsafe_allow_html=True)
            elif p['espn_value_delta'] <= -5:
                st.markdown(f"<span class='reach-badge'>ESPN Reach ({p['espn_value_delta']:.0f})</span>", unsafe_allow_html=True)
        with c3:
            if st.button(f"Draft to Jayme", key=f"rec_draft_{p['player_id']}", type="primary"):
                state.draft_player(p['player_id'], for_jayme=True)
                st.rerun()
        st.markdown("<hr style='margin:4px 0px;'>", unsafe_allow_html=True)

    # Scarcity radar
    scarcity = state.get_tier_scarcity_summary()
    st.markdown(f"""
    <div class='tier-alert'>
        <strong>⚠️ 14-Team Scarcity Alert:</strong><br>
        • <strong>RB:</strong> {scarcity['RB']['top_tier_remaining']} elite left (Top: {scarcity['RB']['best_available']})<br>
        • <strong>WR:</strong> {scarcity['WR']['top_tier_remaining']} elite left (Top: {scarcity['WR']['best_available']})<br>
        • <strong>TE:</strong> {scarcity['TE']['top_tier_remaining']} high-end left (Top: {scarcity['TE']['best_available']})
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Interactive Draft Board
st.subheader("📊 Live Draft Board & Search")

col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2.5, 1.8, 1.8])
with col_f1:
    search_query = st.text_input("🔍 Search Player by Name", placeholder="e.g. Barkley, Rice, Kincaid...")
with col_f2:
    pos_filter = st.selectbox("Filter Position", ["All Positions", "RB", "WR", "TE", "QB", "FLEX (RB/WR/TE)", "DST", "K"])
with col_f3:
    steals_only = st.checkbox("Only ESPN Steals", value=False)
with col_f4:
    hide_out = st.checkbox("🚫 Hide OUT / Inactive", value=True)

# Full pool for board
board_avail_df = state.get_available_players_df(exclude_out=False)
display_df = board_avail_df.copy()

if hide_out:
    display_df = display_df[~display_df['injury_risk'].astype(str).str.upper().isin(['OUT']) & (display_df['marginal_ev'] > -500.0)]

if search_query:
    display_df = display_df[display_df['name'].str.contains(search_query, case=False, na=False)]

if pos_filter == "FLEX (RB/WR/TE)":
    display_df = display_df[display_df['pos'].isin(['RB', 'WR', 'TE'])]
elif pos_filter != "All Positions":
    display_df = display_df[display_df['pos'] == pos_filter]

if steals_only:
    display_df = display_df[display_df['espn_value_delta'] >= 5]

st.caption(f"Showing {len(display_df)} available players. Click buttons below to update draft in real-time.")

items_per_page = 20
total_pages = max(1, (len(display_df) - 1) // items_per_page + 1)
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
start_idx = (page - 1) * items_per_page
end_idx = start_idx + items_per_page

paged_df = display_df.iloc[start_idx:end_idx]

# Header Row
hdr1, hdr2, hdr3, hdr4, hdr5, hdr6, hdr7 = st.columns([1.5, 3.5, 2, 2, 2.5, 2.5, 3.5])
hdr1.markdown("**Pos Rank**")
hdr2.markdown("**Player / Team**")
hdr3.markdown("**Context EV**")
hdr4.markdown("**Marginal EV**")
hdr5.markdown("**ESPN ADP (Delta)**")
hdr6.markdown("**Scout Note**")
hdr7.markdown("**Draft Action**")
st.markdown("<hr style='margin: 0px 0px 8px 0px;'>", unsafe_allow_html=True)

for _, row in paged_df.iterrows():
    p_id = row['player_id']
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 3.5, 2, 2, 2.5, 2.5, 3.5])
    
    with col1:
        st.write(f"**{row['pos']}{row['pos_rank']}** (#{row['true_ev_rank']})")
        
    with col2:
        badge_html = ""
        inj_code = str(row['injury_risk']).upper()
        if inj_code == 'OUT':
            badge_html = " <span class='chip-out'>🔴 OUT</span>"
        elif inj_code in ['IR', 'PUP', 'PUP/IR']:
            badge_html = f" <span class='chip-ir'>🟠 {row['injury_risk']}</span>"
        elif inj_code == 'QUESTIONABLE':
            badge_html = " <span class='chip-q'>🟡 Q</span>"
            
        st.markdown(f"**{row['name']}**{badge_html}", unsafe_allow_html=True)
        st.caption(f"{row['team']} • Risk: {row['injury_risk']}")
        
    with col3:
        st.write(f"**{row['context_ev']:.1f}**")
        
    with col4:
        st.write(f"**+{row['marginal_ev']:.1f}**")
        st.caption(row['role_addition'])
        
    with col5:
        delta = row['espn_value_delta']
        if delta >= 5:
            st.markdown(f"ADP {row['espn_adp']:.1f} <br><span class='steal-badge'>Steal +{delta:.0f}</span>", unsafe_allow_html=True)
        elif delta <= -5:
            st.markdown(f"ADP {row['espn_adp']:.1f} <br><span class='reach-badge'>Fade {delta:.0f}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"ADP {row['espn_adp']:.1f} <br><small>Fair</small>", unsafe_allow_html=True)
            
    with col6:
        st.caption(f"{row['notes'][:65]}..." if len(str(row['notes'])) > 65 else row['notes'])
        
    with col7:
        btn_col_a, btn_col_b = st.columns(2)
        with btn_col_a:
            if st.button("Taken", key=f"taken_{p_id}", help="Mark as picked by another team", use_container_width=True):
                state.draft_player(p_id, for_jayme=False)
                st.rerun()
        with btn_col_b:
            if st.button("Jayme", key=f"jayme_{p_id}", type="primary", help="Draft to Jayme's team", use_container_width=True):
                state.draft_player(p_id, for_jayme=True)
                st.rerun()

    st.markdown("<hr style='margin: 4px 0px;'>", unsafe_allow_html=True)
