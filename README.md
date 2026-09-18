# CarbIQ — Industrial Carbon Intelligence

Transforming passive operational emission measurement into a budget-constrained optimization engine using Mixed-Integer Linear Programming (MILP).

## Mathematical Formulation
CarbIQ models decarbonization project allocation as a **0/1 Knapsack Problem** solved via PuLP Branch-and-Bound:

* **Objective Function:**
  $$\max \sum_{i=1}^{n} \Delta E_i \cdot x_i, \quad x_i \in \{0, 1\}$$
* **Budget Constraint:**
  $$\sum_{i=1}^{n} C_i \cdot x_i \le B$$

## Setup & Execution
1. Install dependencies:
   ```bash
   pip install -r requirements.txt