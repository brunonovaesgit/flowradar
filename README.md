# FlowRadar — Organizational Flow Diagnostics

## 🧠 Overview

FlowRadar is an analytical model designed to diagnose organizational flow through the lens of **dependencies and system structure**.

Instead of focusing only on execution metrics (like lead time or throughput), FlowRadar reveals:

- where the system actually depends  
- how fragile the structure is  
- how coordination impacts delivery  

It shifts the perspective from managing work to **understanding the system behind it**.

---

## 🔍 What is this?

FlowRadar is not a tool or a dashboard.

It is a model that answers questions such as:

- Where are the real bottlenecks?
- Is the system structurally fragile?
- How much coordination is required to deliver value?

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/brunonovaesgit/flowradar.git
cd flowradar
```

> Before cloning, pick a local folder where you want to store the project.

---

### 2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux / Mac

# ou
venv\Scripts\activate     # Windows
```

---

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

▶️ Running

Run the main analysis:
```bash
python run_flowradar.py
```

Run impact simulations: 
```bash
python compare_simulations.py
```

---

🧪 Testing

Run all tests:
```bash
pytest
```

Run with more detailed output:
```bash
pytest -vv
```

📊 What you get

Depending on your scenario, FlowRadar will generate:

- Dependency network (graph.json)
- Impact ranking (who actually matters in the flow)
- Dependency concentration heatmaps
- Simulations of squad removal or changes
- Structural explanations of system behavior

---

📈 What you start to see

After using FlowRadar, some things become pretty clear:

- Why features get stuck for weeks
- Why splitting stories doesn’t always help
- Why some teams “always seem delayed”
- Why good metrics don’t necessarily mean a healthy flow

---

⚠️ The necessary discomfort

FlowRadar won’t give you comfortable answers.

It might show that:

The problem isn’t the team
The problem isn’t the process
The problem is how the work is structured

---

📊 Project structure

```bash
.
├── src/
│   ├── analysis/
│   ├── graph_builder/
│   ├── metrics/
│   ├── pipeline/
│   ├── reports/
│   ├── simulations/
│   └── visualizations/
│
├── tests/
├── data/
│
├── run_flowradar.py
├── compare_simulations.py
│
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

---

## 🧩 Core Concept

Organizations can be modeled as a **network of dependencies**:

- Nodes → squads / teams  
- Edges → dependencies between them  

```bash
G = (V,E)
```

Where:

- `V` = set of nodes  
- `E` = set of dependencies  

This allows us to move from isolated metrics to **system-level analysis**.

---

## ⚠️ Criticality

Each node can be evaluated based on its structural importance.

A simplified formulation:
```bash
Cᵢ = α · InDegreeᵢ + β · BetweennessCentralityᵢ
```

Where:

- `InDegree` captures how many depend on the node  
- `Betweenness` captures how much flow passes through it  

High criticality indicates potential bottlenecks.

---

## 🔥 Flow Fragility Index (FFI)
```bash
FFI = Σ(Cᵢ²) / Σ(Cᵢ)
```

### What it measures

The concentration of critical dependencies in the system.

### Interpretation
```bash
| Range      | Meaning                      |
|------------|------------------------------|
| < 0.3      | Distributed (low fragility)  |
| 0.3 – 0.6  | Moderate concentration       |
| > 0.6      | High fragility               |
```
### Insight

A high FFI means the system depends heavily on a few nodes, increasing systemic risk.

---

## 🔄 Coordination Cost Index (CCI)
```bash
CCI = Σ(dependencies) / N
```

Where:

- `N` = number of squads  

### What it measures

The average coordination effort required per squad.

### Interpretation
```bash
| Range  | Meaning                     |
|--------|-----------------------------|
| < 2    | Low coordination            |
| 2 – 4  | Moderate                    |
| > 4    | High coordination overhead  |
```
### Insight

Higher CCI means more alignment, more communication, and slower flow.

---

## 🌐 System Behavior

By combining FFI and CCI, we can characterize the system:
```bash
| Scenario             | Interpretation             |
|----------------------|----------------------------|
| High FFI + High CCI  | Fragile and overloaded     |
| Low FFI + Low CCI    | Resilient and autonomous   |
| High FFI + Low CCI   | Centralized but efficient  |
| Low FFI + High CCI   | Distributed but complex    |
```
---

## 📊 Example Output

FlowRadar transforms operational data (e.g., Jira) into:

- dependency graphs  
- heatmaps  
- criticality rankings  
- system-level indicators  

These outputs make invisible structures visible.

---

## 🎯 Why This Matters

Traditional metrics answer:

> “How fast are we delivering?”

FlowRadar answers:

> “Why are we slow — structurally?”

---

## 🧭 Positioning

FlowRadar is not:

- a project management tool  
- a dashboard  
- a reporting layer  

It is:

> a model for diagnosing organizational flow as a system.

---

## 📖 Article

For a deeper explanation and narrative context:

👉 [(https://medium.com/@brunonovaesbr/flowradar-hidden-architecture-of-flow-461e96d42ddd)](https://medium.com/@brunonovaesbr/flowradar-hidden-architecture-of-flow-461e96d42ddd)

---

## 🧠 Final Thought

Organizations don’t struggle because they lack effort.

They struggle because they cannot see the system they operate in.

---

## ☕ Support FlowRadar

If FlowRadar helps you understand flow, dependencies, and bottlenecks in real-world systems, consider supporting its evolution:

👉 https://buymeacoffee.com/brunonovaes


