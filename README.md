# FlowRadar

FlowRadar is a data-driven framework for analyzing organizational flow and structural dependencies across squads, clusters, and tribes.

It transforms raw operational data into a systemic view of bottlenecks, structural criticality, organizational risk, and simulated disruption scenarios.

---

## What is FlowRadar?

FlowRadar is designed to answer questions that traditional agile metrics alone cannot:

- Where are the real bottlenecks in the organization?
- Which squads concentrate structural risk?
- How do dependencies affect systemic resilience?
- What happens if a critical squad is removed from the network?
- Why is a squad structurally critical?
- Which simulated scenario is more disruptive?

Instead of focusing only on delivery metrics such as lead time or throughput, FlowRadar models the organization as a dependency network and analyzes it from a systemic perspective.

---

## What FlowRadar does

FlowRadar can:

- build a dependency graph from raw CSV data
- validate the integrity of input data before execution
- calculate structural metrics for squads
- rank squads by structural criticality
- generate dependency heatmaps and executive graphs
- calculate organizational risk
- simulate the removal of a squad
- explain why a squad is critical
- compare multiple simulation scenarios
- generate executive HTML reports

---

## Core Concepts

### Dependency Graph
Squads are modeled as nodes, and dependencies are modeled as directed edges.

### Structural Criticality
A synthetic score that combines:
- in-degree
- betweenness centrality
- PageRank

This score identifies squads that concentrate structural influence and bottleneck potential.

### Organizational Risk
A complementary score that highlights squads with high systemic exposure.

### Impact Simulation
Simulates the structural effect of removing a squad from the dependency graph.

### Explain Impact
Generates a human-readable explanation for why a squad is considered critical.

### Simulation Comparison
Compares multiple simulated removals and ranks which scenarios generate greater systemic disruption.

---

## Current Features

- Build dependency networks from raw data
- Validate input model integrity
- Calculate:
  - In-degree / Out-degree
  - Betweenness Centrality
  - PageRank
  - Structural Criticality Score
  - Organizational Risk Score
- Generate:
  - Dependency matrix
  - Heatmap
  - Executive dependency graph
  - Criticality ranking chart
  - Executive HTML report
- Simulate removal of a squad
- Explain impact of a simulated squad
- Compare multiple simulation scenarios
- Export outputs in:
  - CSV
  - JSON
  - PNG
  - HTML

---

## Project Structure

```bash
flowradar/
├── run_flowradar.py
├── compare_simulations.py
├── requirements.txt
├── src/
│   ├── graph_builder/
│   ├── metrics/
│   ├── pipeline/
│   ├── reports/
│   ├── simulations/
│   └── visualizations/
├── data/
│   ├── raw/
│   │   ├── example/
│   │   └── prod/
│   └── outputs/
└── tests/
```

---

## Installation

1. Clone the repository
```bash
git clone https://github.com/seu-usuario/flowradar.git
cd flowradar/app
```

2. Create a virtual environment

Linux / Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```
---

## Canonical Input Model

FlowRadar expects three CSV files.

They must be placed in one of these directories:

data/raw/example/

or

data/raw/prod/
Example mode file names

Inside data/raw/example/, use:

example_work_items.csv
example_relationships.csv
example_team_mapping.csv

Production mode file names

Inside data/raw/prod/, use:

work_items.csv
relationships.csv
team_mapping.csv

---

## Required Files

## 1. work_items.csv

Required columns:

item_id, team

Rules:

item_id must be unique
team must exist in team_mapping.csv
null values are not allowed

---

## 2. relationships.csv

Required columns:

source_item, target_item

Rules:

both items must exist in work_items.csv
null values are not allowed

---

## 3. team_mapping.csv

Required columns:

team, cluster, tribe

Rules:

team must be unique
all teams must match the teams referenced in work_items.csv

---

## Data Validation

Before execution, FlowRadar validates:

Structural validation
required columns
empty files
null values
Referential integrity
relationships.source_item → work_items.item_id
relationships.target_item → work_items.item_id
work_items.team → team_mapping.team
Non-blocking warnings
duplicate relationships
self-dependencies
unused teams

If validation fails, execution is interrupted.

---

## How to Run
1. Run with example data
python run_flowradar.py --mode example
2. Run with production data
python run_flowradar.py --mode prod
3. Run with a custom directory
python run_flowradar.py --input ./data/raw/prod

---

## How to Run a Simulation

To simulate the removal of a squad:

python run_flowradar.py --mode example --simulate-squad SQD-DAD

Replace SQD-DAD with the squad you want to simulate.

Example:

python run_flowradar.py --mode example --simulate-squad SQD-APP

---

## How to Run Multiple Simulations

Example:

python run_flowradar.py --mode example --simulate-squad SQD-DAD
python run_flowradar.py --mode example --simulate-squad SQD-APP
python run_flowradar.py --mode example --simulate-squad SQD-AUTH

Each simulation generates its own files, without overwriting the others.

---

## How to Compare Simulations

After generating two or more simulations, run:

python compare_simulations.py

This will compare all files that match:

impact_simulation_*.json

and generate a consolidated comparison.

---

Output Files

All outputs are generated in:

data/outputs/

---

## Baseline Outputs

Generated in normal execution:

structural_metrics.csv
Ranking of squads by structural criticality
risk_analysis.csv
Ranking of squads by organizational risk
squad_relationships.csv
Expanded table of squad-to-squad relationships
dependency_matrix.csv
Matrix of dependencies between squads
dependency_heatmap.png
Heatmap of dependencies
dependency_graph.png
Executive dependency graph
criticality_ranking.png
Visual ranking of structural criticality
summary.json
Executive summary
flowradar_report.html
Executive HTML report for the baseline scenario

---

## Simulation Outputs

Generated only when --simulate-squad is used.

Example for SQD-DAD:

impact_simulation_SQD-DAD.json
Raw result of the simulation
dependency_graph_impact_SQD-DAD.png
Graph showing the structural effect of the simulated removal
impact_explanation_SQD-DAD.json
Explain Impact output
flowradar_report_simulation_SQD-DAD.html
Executive HTML report for that simulated scenario

---

## Simulation Comparison Outputs

Generated by compare_simulations.py:

simulation_comparison.csv
Table comparing all simulated scenarios
simulation_comparison_summary.json
Summary of the comparison
simulation_comparison.png
Visual ranking of the most disruptive simulated removals

---

How to Read the Results
## 1. structural_metrics.csv

Use this file to identify which squads are structurally critical.

Main columns:

dependencies_received_in_degree
dependencies_generated_out_degree
betweenness_centrality
pagerank
structural_criticality_score

Interpretation:

higher structural_criticality_score means higher structural relevance
squads at the top are likely bottlenecks or critical hubs

---

## 2. risk_analysis.csv

Use this file to identify systemic exposure and concentration of risk.

Main columns:

risk_score
risk_category

Interpretation:

bottleneck = very high systemic concentration
hub = highly connected and relevant
fragile = vulnerable or structurally exposed
peripheral = lower systemic importance

---

## 3. dependency_heatmap.png

Use this chart to visualize concentration of dependencies.

Interpretation:

darker cells indicate stronger dependency volume
rows = dependent squads
columns = provider squads

---

## 4. dependency_graph.png

Use this graph to understand the executive structural view of the network.

Interpretation:

larger nodes = more structurally critical
thicker edges = stronger dependency volume
highlighted nodes = most relevant squads

---

## 5. criticality_ranking.png

Use this chart to quickly identify the most critical squads.

Interpretation:

top bar = strongest structural bottleneck
top 3 usually deserve special attention

---


## 6. impact_simulation_<SQUAD>.json

Use this file to inspect the result of a simulation.

Main fields:

removed_squad
impact_score
original_metrics
simulated_metrics
delta

Interpretation:

higher impact_score means stronger systemic disruption
useful for scenario analysis and resilience discussion

---

## 7. impact_explanation_<SQUAD>.json

Use this file to understand why a simulated squad matters.

Main fields:

direct_dependents
direct_dependencies
in_degree
out_degree
betweenness_centrality
cascade_impact
summary

Interpretation:

explains structural influence in plain language
useful for leadership discussion

---

## 8. flowradar_report.html

This is the easiest way to consume the baseline results.

It consolidates:

KPIs
ranking
risk table
heatmap
dependency graph

Recommended for:

quick review
presentations
sharing results with non-technical stakeholders

---

## 9. flowradar_report_simulation_<SQUAD>.html

This is the easiest way to consume a simulation.

It consolidates:

baseline KPIs
simulation graph
Explain Impact section
executive interpretation

Recommended for:

scenario analysis
resilience discussion
leadership meetings

---

## 10. simulation_comparison.png

Use this when you want to compare multiple simulated removals.

Interpretation:

higher bar = more disruptive scenario
useful to answer:
which squad is riskier to lose?
which scenario generates more disruption?

---

## Recommended Execution Flow

Basic analysis
python run_flowradar.py --mode example

Then open:

data/outputs/flowradar_report.html

---

## Single simulation analysis
python run_flowradar.py --mode example --simulate-squad SQD-DAD

Then open:

data/outputs/flowradar_report_simulation_SQD-DAD.html

---

## Comparative simulation analysis
python run_flowradar.py --mode example --simulate-squad SQD-DAD
python run_flowradar.py --mode example --simulate-squad SQD-APP
python run_flowradar.py --mode example --simulate-squad SQD-AUTH
python compare_simulations.py

Then inspect:

data/outputs/simulation_comparison.png
data/outputs/simulation_comparison.csv
data/outputs/simulation_comparison_summary.json

---

## Example Use Cases
Identify hidden bottlenecks in large organizations
Support architectural and organizational decisions
Understand dependency concentration
Improve systemic resilience
Support QBR and leadership discussions with evidence
Detect critical squads before organizational redesign
Simulate fragility and cascading disruption

---

## Data Sources

FlowRadar is tool-agnostic.

Data can originate from:

Jira
Azure DevOps
SwiftKanban
CSV exports
internal APIs

Important:
all data must be converted to the canonical input model before execution.

---

## Important Notes
Do not upload sensitive production data
Prefer anonymized or synthetic datasets when sharing
Ensure consistency between datasets before running
Regenerate simulations after changing impact logic
compare_simulations.py does not recalculate simulations — it only reads files already generated

---

## Roadmap
 Interactive graph visualization
 Native integration with Jira / Azure DevOps
 Dependency explanation directly inside comparison reports
 Simulation portfolio view
 Organizational digital twin simulation
 Automated data adapters

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

It is about making invisible organizational dynamics visible.