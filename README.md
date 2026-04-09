# FlowRadar

FlowRadar is a data-driven framework for analyzing organizational flow and structural dependencies across squads, clusters, and tribes.

It transforms raw operational data into a systemic view of bottlenecks, structural criticality, and coordination complexity.

---

## What is FlowRadar?

FlowRadar is designed to answer questions that traditional agile metrics cannot:

- Where are the real bottlenecks in the organization?
- Which squads concentrate structural risk?
- How do dependencies impact flow efficiency?
- What happens if a critical node is removed?

Instead of focusing only on delivery metrics (lead time, throughput), FlowRadar models the organization as a *dependency network*.

---

## Core Concepts

- *Dependency Graph*  
  Squads are modeled as nodes, and dependencies as directed edges.

- *Structural Criticality*  
  Combines multiple centrality metrics to identify bottlenecks.

- *Systemic View*  
  Moves beyond local optimization to understand global impact.

- *Impact Simulation*  
  Simulates removal of squads to evaluate structural fragility.

---

## Features

- Build dependency networks from raw data
- Calculate structural metrics:
  - In-degree / Out-degree
  - Betweenness Centrality
  - PageRank
  - Structural Criticality Score
- Generate:
  - Dependency matrix
  - Heatmaps
  - Ranked critical squads
- Simulate impact of removing a squad
- Export results in CSV and JSON

---

## Project Structure

flowradar/ ├── run_flowradar.py ├── requirements.txt ├── src/ │   ├── graph_builder/ │   ├── metrics/ │   ├── visualizations/ │   ├── simulations/ │   └── pipeline/ ├── data/ │   ├── raw/ │   ├── canonical/ │   └── outputs/ ├── docs/ │   └── examples/ └── tests/

---

## Installation

### 1. Clone the repository

git clone https://github.com/seu-usuario/flowradar.git⁠� cd flowradar

### 2. Create virtual environment (recommended)

python -m venv venv source venv/bin/activate  # Linux/Mac venv\Scripts\activate     # Windows

### 3. Install dependencies

pip install -r requirements.txt

---

## Input Data

Place your input files inside:

data/raw/

### Required files:

#### example_work_items.csv

| item_id | team |
|--------|------|
| 1 | Squad A |
| 2 | Squad B |

#### example_relationships.csv

| source_item | target_item |
|------------|-------------|
| 1 | 2 |

#### example_team_mapping.csv

| team | cluster | tribe |
|------|---------|-------|
| Squad A | Cluster 1 | Tribe X |

---

## How to Run

python run_flowradar.py --input ./data/raw

### Optional: simulate impact

python run_flowradar.py --input ./data/raw --simulate-squad "Squad A"

---

## Outputs

Generated in:

data/outputs/

### Files:

- structural_metrics.csv → ranking of squads by criticality
- dependency_matrix.csv → matrix of dependencies
- dependency_heatmap.png → visual heatmap
- summary.json → executive summary
- impact_simulation.json → simulation results (optional)

---

## Example Use Cases

- Identify hidden bottlenecks in large organizations
- Support architectural decisions
- Improve flow efficiency
- Reduce coordination cost
- Provide data for QBR / leadership discussions

---

## Example Data

See:

docs/examples/

---

## Important Notes

- Do not upload sensitive production data
- Use anonymized or synthetic datasets when sharing

---

## Roadmap

- [ ] Interactive graph visualization (network explorer)
- [ ] Integration with Jira / Azure DevOps
- [ ] Flow efficiency metrics (waiting vs work)
- [ ] AI-based pattern detection
- [ ] Organizational digital twin simulation

---

## License

This project is licensed under the MIT License.

---

## Author

Bruno Novaes  
Agile Coach | Systems Thinking | Data-Driven Organizations

---

## Final Thought

FlowRadar is not just about metrics.

It is about making *invisible organizational dynamics visible*.