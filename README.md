# ESPN Fantasy Draft & Roster Optimization Engine

[![CI](https://github.com/kaushalbalagurusamy/espn-fantasy-draft/actions/workflows/ci.yml/badge.svg)](https://github.com/kaushalbalagurusamy/espn-fantasy-draft/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

Quantitative draft optimization engine, real-time value arbitrage solver, and dynamic roster manager tailored for 14-team full-PPR ESPN snake drafts. Integrates context-adjusted statistical projections, value over replacement player (VORP) metrics, turn-based tier scarcity modeling, and live ESPN injury/news telemetry to optimize back-to-back draft execution and in-season lineup configuration.

---

## Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                         Data Ingestion & Telemetry Pipeline                       |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | ESPN Injury API    |  | ESPN News Endpoint   |  | League Config & ADP CSVs  |  |
|  | (/nfl/injuries)    |  | (/nfl/news)          |  | (14-Team Full-PPR Rules)  |  |
|  +---------+----------+  +----------+-----------+  +-------------+-------------+  |
|            |                        |                            |                |
+------------|------------------------|----------------------------|----------------+
             |                        |                            |
             v                        v                            v
+-----------------------------------------------------------------------------------+
|                     Background Monitoring Daemon (60s Polling)                    |
|  - Real-time injury status updates (OUT, IR, Questionable, Settlement Detection)  |
|  - Automatic Expected Value (EV) zeroing for unrosterable/released players        |
|  - Cache persistence to data/live_news_alerts.json                                |
+-------------------------------------+---------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
|                       Valuation & Arbitrage Engine (src/engine.py)                |
|                                                                                   |
|  +--------------------------------+       +------------------------------------+  |
|  | Context Multipliers            |       | Value Over Replacement (VORP)      |  |
|  | - O-Line Run/Pass Grades       | ----> | - Baseline dynamic cutoff indices  |  |
|  | - Vegas Implied Team Totals    |       | - Cross-positional value delta     |  |
|  | - Pace & Pass Rate Over Exp.   |       | - ESPN ADP vs. True EV Arbitrage   |  |
|  +--------------------------------+       +------------------------------------+  |
+-------------------------------------+---------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
|                   Dynamic Roster Optimization Core (src/roster.py)                 |
|                                                                                   |
|  - State-aware Marginal EV solver: dynamically weights remaining open slots       |
|  - Turn-based scarcity radar: simulates 26-pick voids between drafting intervals  |
|  - Correlated stacking engine (Chiefs quad-stack optimization)                    |
+-------------------------------------+---------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
|                     Execution & Interface Layer (app.py, Streamlit)               |
|  - Interactive draft board with live clock, pick recommendations, and undo stack  |
|  - Real-time roster allocations across starters, flex, and bench                  |
|  - Dual-mode storage sync between memory session and data/draft_state.json        |
+-----------------------------------------------------------------------------------+
```

---

## Mathematical & Algorithmic Formulations

### 1. Base Expected Value (EV) Calculation
Player scoring projections are grounded in verified 14-team full-PPR ESPN league parameters:

$$\text{Base EV} = 0.04 \cdot \text{PassYds} + 4.0 \cdot \text{PassTD} - 2.0 \cdot \text{PassInt} + 0.10 \cdot \text{RushYds} + 6.0 \cdot \text{RushTD} + 1.0 \cdot \text{Rec} + 0.10 \cdot \text{RecYds} + 6.0 \cdot \text{RecTD} - 2.0 \cdot \text{FumblesLost}$$

### 2. Contextual Multipliers
Raw volume projections are adjusted using situational team environment coefficients:

$$M_{\text{context}} = 1.0 + w_{\text{vegas}} \left(\frac{\text{VegasPts} - \bar{V}}{\bar{V}}\right) + w_{\text{oline}} \left(\frac{\text{OLGrade} - \bar{G}}{\bar{G}}\right) + w_{\text{pace}} \left(\frac{\bar{P} - \text{Pace}}{\bar{P}}\right) + w_{\text{proe}} \cdot \text{PROE}$$

$$\text{Context EV} = \text{Base EV} \cdot M_{\text{context}}$$

Where:
* $\text{VegasPts}$: Implied team scoring total derived from sportsbooks.
* $\text{OLGrade}$: Offensive line run- and pass-blocking composite grades (0 to 100).
* $\text{Pace}$: Seconds elapsed per offensive snap (lower values indicate faster pace).
* $\text{PROE}$: Pass Rate Over Expected relative to league-wide down-and-distance baselines.

### 3. Value Over Replacement Player (VORP)
Replacement thresholds are established dynamically based on 14-team league roster demand:
* **Quarterback (QB)**: Rank 14 replacement baseline ($B_{\text{QB}}$).
* **Running Back (RB)**: Rank 35 replacement baseline ($B_{\text{RB}}$).
* **Wide Receiver (WR)**: Rank 35 replacement baseline ($B_{\text{WR}}$).
* **Tight End (TE)**: Rank 14 replacement baseline ($B_{\text{TE}}$).

$$\text{VORP}_i = \text{Context EV}_i - B_{\text{pos}(i)}$$

### 4. Dynamic Marginal Expected Value (MEV)
During live drafts, static VORP degrades in utility once specific positional slots are filled. The marginal value optimizer assigns value based on incremental roster contribution:

$$\text{MEV}(p) = \begin{cases} 
\text{Context EV}(p) - B_{\text{starter}}, & \text{if position slot is open} \\
\text{Context EV}(p) - B_{\text{flex}}, & \text{if flex slot is open and } p \in \{\text{RB}, \text{WR}, \text{TE}\} \\
\text{ContingentValue}(p) \cdot P(\text{Usage}) - B_{\text{bench}}, & \text{if depth slot}
\end{cases}$$

### 5. Turn-Based Snake Void Modeling
In a 14-team snake draft, picking from the turn (Slot #14) introduces an asymmetric 26-pick interval between selection clusters:
* **Selection Pairs**: Picks $(14, 15), (42, 43), (70, 71), (98, 99), \dots$
* **Void Length**: Exactly 26 selections elapse while competitors draft.
* **Scarcity Horizon**: The engine scans forward over a 26-pick window to identify positional cliffs where remaining tier density drops below 20%, forcing critical position runs before rivals deplete the talent tier.

---

## Core Capabilities

* **Real-Time Turn Clock & State Tracker**: Automatically models turn intervals, drafting order, and on-deck status for 14-team snake structures.
* **Live Injury & Inactivity Telemetry**: Background worker queries official ESPN injury and news endpoints every 60 seconds, dynamically zeroing out unrosterable players, free agents, and injured reserves.
* **Arbitrage Detection**: Compares ESPN default Average Draft Position (ADP) against proprietary Context EV to flag undervalued players buried in the draft client.
* **Chiefs Quad-Stack Optimization**: Leveraged high-correlation compounding by pairing Patrick Mahomes with Travis Kelce, Xavier Worthy, and Harrison Butker.
* **Dual-TE Flex Integration**: Capitalized on full-PPR scoring efficiency by pairing Travis Kelce with Mark Andrews in the starting lineup.
* **Full Audit Trail & Undo Stack**: Every transaction is committed atomically to `data/draft_state.json` with multi-level undo capabilities.

---

## Repository Structure

```text
.
├── app.py                     # Streamlit real-time interactive draft dashboard
├── run.sh                     # Execution launch wrapper
├── requirements.txt           # Project dependencies
├── LICENSE                    # MIT License
├── README.md                  # System documentation
├── config/
│   └── league_rules.yaml      # League rules, roster slots, and scoring weights
├── data/
│   ├── draft_state.json       # Live draft state, pick history, and team rosters
│   ├── live_news_alerts.json  # Cached telemetry from ESPN injury/news daemon
│   ├── players.csv            # Comprehensive player database with baseline stats
│   └── team_context.csv       # Team-level pace, O-line, and Vegas metrics
├── picks/                     # Screenshot repository documenting draft progression
├── scripts/
│   ├── background_news_monitor.py # Background daemon polling ESPN injury API
│   ├── build_dataset.py       # Player pool dataset generation and enrichment
│   ├── expand_players.py      # Extension utilities for supplemental player tracking
│   ├── fix_state.py           # State schema sanitization utility
│   ├── generate_cheatsheet.py # Static turn cheat sheet generator
│   ├── init_draft_state.py    # State initialization script
│   └── sync_picks_round6.py   # Historical pick reconciliation utility
└── src/
    ├── __init__.py
    ├── config.py              # Configuration parser and pick index generator
    ├── engine.py              # EV, VORP, and contextual multiplier algorithms
    ├── roster.py              # Dynamic roster tracker and marginal EV optimizer
    └── state.py               # Draft state manager and disk persistence layer
```

---

## Installation & Setup

### Prerequisites
* Python 3.11 or higher
* pip or uv package manager

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/kaushalbalagurusamy/espn-fantasy-draft.git
cd espn-fantasy-draft

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage Guide

### 1. Launching the Interactive Web Dashboard
Run the provided shell script or start Streamlit directly:

```bash
./run.sh
```

Or execute via the active virtual environment:

```bash
streamlit run app.py --server.port 8501 --server.headless true
```

Navigate to `http://localhost:8501` to view the live dashboard.

### 2. Running the Live News & Injury Monitor Daemon
Start the autonomous background process to poll ESPN APIs for breaking injury designations:

```bash
python scripts/background_news_monitor.py 60
```

Where `60` specifies the polling frequency in seconds.

### 3. Rebuilding Player Projections
To regenerate player projections from raw context metrics:

```bash
python scripts/build_dataset.py
```

---

## Verification & Testing

Verify state integrity and test recommendation generation via the Python shell:

```python
from src.state import DraftState

state = DraftState()
print(f"Current Draft Pick: #{state.current_pick}")
print(f"Active Drafter: {state.current_drafter_name}")

# Fetch top available players sorted by marginal EV
available = state.get_available_players_df(exclude_out=True)
print(available[['name', 'pos', 'team', 'context_ev', 'marginal_ev']].head(10))
```

Execute unit tests:

```bash
pytest tests/
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
