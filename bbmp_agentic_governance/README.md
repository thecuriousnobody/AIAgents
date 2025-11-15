# BBMP Agentic Governance System

**Automating Transparent Governance with AI Agents**

## 🎯 Mission

Eliminate corruption in BBMP's Public Works Department by replacing discretionary human decision-making at vulnerable nodes with AI agents operating on transparent, immutable rules.

## 🤖 The Agents

### Phase 0 (Current Demo)

1. **Budget Sentinel** - Validates budgets against Karnataka PWD Schedule of Rates
2. **DPR Integrity Agent** - Verifies project proposals have legitimate need and proper documentation
3. **Tender Integrity Monitor** - Detects bid rigging and contractor cartels

### Future Phases

4. Contractor Background Investigator
5. Quality Verification Sentinel (with IoT sensors)
6. Payment Processing Agent (blockchain-based)
7. Blockchain Ledger Keeper
8. Public Dashboard Generator
9. Anomaly Detection Watchdog
10. Citizen Feedback Aggregator

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Required: Claude Sonnet 4.5 for agent intelligence
export ANTHROPIC_API_KEY='your-anthropic-api-key'

# Optional: For web search capability
export SERPER_API_KEY='your-serper-api-key'
```

### Run the Demo

```bash
cd bbmp_agentic_governance
python demo.py
```

## 📊 Demo Scenarios

The demo includes 5 scenarios showcasing different corruption detection capabilities:

1. **Legitimate Project** - Agents approve well-documented project with citizen demand
2. **Suspicious Project** - Agents reject project with inflated budget and missing docs
3. **Duplicate Detection** - Agents catch duplicate project proposals
4. **Cartel Detection** - Agents expose contractor networks with shared directors
5. **Good Tender** - Agents approve competitive tender with reputable bidders

## 🎤 For Podcast Demo

**Quick Demo (Best for podcast - 5-10 minutes):**

Run option 7 which shows:
- Scenario 2: Suspicious project with 35% budget inflation → REJECTED
- Scenario 4: Cartel detection with shell companies → REJECTED

This demonstrates the corruption-catching capabilities!

## 💡 System Architecture

```
[DPR Submission]
      ↓
[DPR Integrity Agent] → Validates documentation, checks duplicates
      ↓
[Budget Sentinel] → Validates against Schedule of Rates
      ↓
[Tender Integrity Monitor] → Analyzes contractors, detects cartels
      ↓
[Decision: APPROVE / REJECT / FLAG]
```

## 📁 Project Structure

```
bbmp_agentic_governance/
├── agents/              # CrewAI agent definitions
│   ├── budget_sentinel.py
│   ├── dpr_integrity_agent.py
│   └── tender_monitor.py
├── data/                # Mock BBMP data
│   ├── schedule_of_rates.json
│   ├── contractors.json
│   └── sample_dprs.json
├── tools/               # Custom tools for agents
│   └── bbmp_tools.py
├── config/              # Configuration files
│   └── config.yaml
├── demo.py             # Main demo script
└── README.md
```

## 🎯 Impact Potential

### Current BBMP Problem
- Annual PWD budget: ₹6,000 crores
- Estimated leakage: 20-30% (₹1,200-1,800 crores)
- Corruption vulnerabilities: Budget approval, tendering, quality checks, payments

### Solution Impact
- **Automated validation** against Schedule of Rates → Eliminate budget inflation
- **Cartel detection** → Force genuine competition → 10-15% cost savings
- **Quality monitoring** (Phase 1: IoT) → Reduce substandard work
- **Blockchain payments** → Eliminate ghost contractors

**Projected Savings: ₹1,200-1,800 crores per year**

## 🔧 Technology Stack

- **Agent Framework:** CrewAI + LangChain
- **LLM:** Claude Sonnet 4.5 (Anthropic)
- **Data:** Mock JSON databases (PostgreSQL in production)
- **Search:** Serper API (optional)

### Future Stack (Phase 1+)
- **Blockchain:** Hyperledger Fabric / Ethereum
- **IoT:** Concrete sensors, drones, GPS trackers
- **Frontend:** React + D3.js dashboards
- **Mobile:** React Native app for citizen feedback

## 📈 Next Steps

### Phase 1: Pilot (Months 1-6)
- 10 projects in Bommanahalli zone (₹100-200 crore)
- Integrate real BBMP data
- Add blockchain ledger
- Basic public dashboard

### Phase 2: Expansion (Months 7-12)
- All 8 BBMP zones
- IoT quality sensors
- Complete agent suite (all 10 agents)
- Mobile app for citizens

### Phase 3: Full Deployment (Year 2)
- 100% of BBMP projects
- Real-time public dashboard
- Automated payments via smart contracts
- Integration with State Treasury (Khajane-2)

## 🤝 Contributing

This is an open-source civic tech project. Contributions welcome!

Areas needing help:
- Integration with real BBMP/Karnataka govt APIs
- Blockchain smart contract development
- IoT sensor integration
- Dashboard UI/UX design
- Mobile app development

## 📜 License

MIT License - Build it, fork it, deploy it anywhere!

## 📧 Contact

**GitHub:** [thecuriousnobody/AIAgents](https://github.com/thecuriousnobody/AIAgents)

**Purpose:** Restore citizen trust in government through radical transparency and automation.

---

*"Sunlight is the best disinfectant. AI agents shine sunlight on every rupee."*
