import os

base_dir = '/Users/louayzorai/Desktop/4 ARTIC 6/LOUAY/Stage 4eme - FinOps Agent/finops-dashboard'
env_file = os.path.join(base_dir, 'src/environments/environment.prod.ts')

print(f"=== Content of {env_file} ===")
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        print(f.read())
else:
    print("File not found.")

print("\n=== Searching for finops.service.ts ===")
service_file = None
for root, dirs, files in os.walk(base_dir):
    if 'node_modules' in dirs:
        dirs.remove('node_modules')
    for file in files:
        if file.endswith('service.ts') and 'finops' in file.lower():
            service_file = os.path.join(root, file)
            print(f"Found: {service_file}")
            break
    if service_file:
        break

if service_file:
    print(f"\n=== Content of {service_file} ===")
    with open(service_file, 'r') as f:
        print(f.read())
else:
    print("finops.service.ts not found.")
