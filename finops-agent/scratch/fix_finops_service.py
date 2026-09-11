import os

service_file = '/Users/louayzorai/Desktop/4 ARTIC 6/LOUAY/Stage 4eme - FinOps Agent/finops-dashboard/src/app/core/services/finops.service.ts'

with open(service_file, 'r') as f:
    content = f.read()

# Add import
import_statement = "import { environment } from '../../../environments/environment';\n"
if 'import { environment }' not in content:
    content = content.replace("import { Observable } from 'rxjs';", "import { Observable } from 'rxjs';\n" + import_statement)

# Replace hardcoded apiUrl
content = content.replace("private apiUrl = 'http://localhost:5001';", "private apiUrl = environment.apiUrl;")

with open(service_file, 'w') as f:
    f.write(content)

print("Updated finops.service.ts")
