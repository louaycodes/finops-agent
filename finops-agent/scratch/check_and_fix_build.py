import json
import os

base_dir = '/Users/louayzorai/Desktop/4 ARTIC 6/LOUAY/Stage 4eme - FinOps Agent/finops-dashboard'
angular_json_path = os.path.join(base_dir, 'angular.json')
env_ts = os.path.join(base_dir, 'src/environments/environment.ts')
env_prod_ts = os.path.join(base_dir, 'src/environments/environment.prod.ts')

print("Checking environment files...")
if not os.path.exists(env_ts):
    print(f"Creating missing {env_ts}")
    with open(env_ts, 'w') as f:
        f.write("export const environment = {\n  production: false,\n  apiUrl: 'http://localhost:5001'\n};\n")
else:
    print(f"{env_ts} exists.")

if not os.path.exists(env_prod_ts):
    print(f"Creating missing {env_prod_ts}")
    with open(env_prod_ts, 'w') as f:
        f.write("export const environment = {\n  production: true,\n  apiUrl: 'http://16.170.203.207:5001'\n};\n")
else:
    print(f"{env_prod_ts} exists.")

print("\nChecking angular.json fileReplacements...")
with open(angular_json_path, 'r') as f:
    data = json.load(f)

# Navigate to production build config. Project name can be dynamic, so let's find it.
projects = data.get('projects', {})
for project_name, project_config in projects.items():
    try:
        build_config = project_config['architect']['build']
        prod_config = build_config['configurations']['production']
        
        replacements = prod_config.get('fileReplacements', [])
        
        # Check if environment replacement exists
        has_env_replacement = False
        for rep in replacements:
            if rep.get('replace') == 'src/environments/environment.ts':
                has_env_replacement = True
                break
                
        if not has_env_replacement:
            print(f"Adding fileReplacements for {project_name}")
            replacements.append({
                "replace": "src/environments/environment.ts",
                "with": "src/environments/environment.prod.ts"
            })
            prod_config['fileReplacements'] = replacements
            with open(angular_json_path, 'w') as f:
                json.dump(data, f, indent=2)
            print("angular.json updated.")
        else:
            print(f"fileReplacements already exists for {project_name}.")
    except KeyError:
        print(f"Could not find build configurations for {project_name}.")

print("Done.")
