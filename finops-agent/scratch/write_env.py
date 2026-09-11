import os

content = """export const environment = {
  production: true,
  apiUrl: 'http://16.170.203.207:5001'
};
"""

path = '/Users/louayzorai/Desktop/4 ARTIC 6/LOUAY/Stage 4eme - FinOps Agent/finops-dashboard/src/environments/environment.prod.ts'

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    f.write(content)

print("Successfully written environment.prod.ts")
