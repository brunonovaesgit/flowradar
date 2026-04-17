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
| Range | Meaning |
|------|--------|
| < 0.3 | Distributed (low fragility) |
| 0.3 – 0.6 | Moderate concentration |
| > 0.6 | High fragility |
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
| Range | Meaning |
|------|--------|
| < 2 | Low coordination |
| 2 – 4 | Moderate |
| > 4 | High coordination overhead |
```
### Insight

Higher CCI means more alignment, more communication, and slower flow.

---

## 🌐 System Behavior

By combining FFI and CCI, we can characterize the system:
```bash
| Scenario | Interpretation |
|--------|---------------|
| High FFI + High CCI | Fragile and overloaded |
| Low FFI + Low CCI | Resilient and autonomous |
| High FFI + Low CCI | Centralized but efficient |
| Low FFI + High CCI | Distributed but complex |
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

👉 (add your Medium / LinkedIn article link here)

---

## 🧠 Final Thought

Organizations don’t struggle because they lack effort.

They struggle because they cannot see the system they operate in.

