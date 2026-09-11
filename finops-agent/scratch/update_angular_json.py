import json
import os

path = '/Users/louayzorai/Desktop/4 ARTIC 6/LOUAY/Stage 4eme - FinOps Agent/finops-dashboard/angular.json'

new_budgets = [
  {
    "type": "initial",
    "maximumWarning": "1mb",
    "maximumError": "2mb"
  },
  {
    "type": "anyComponentStyle",
    "maximumWarning": "10kb",
    "maximumError": "20kb"
  }
]

with open(path, 'r') as f:
    data = json.load(f)

def update_budgets(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == 'budgets':
                d[k] = new_budgets
            else:
                update_budgets(v)
    elif isinstance(d, list):
        for item in d:
            update_budgets(item)

update_budgets(data)

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print("Updated angular.json")
