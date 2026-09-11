import os

api_py_path = '../finops-rag-api/routes/api.py'
with open(api_py_path, 'r') as f:
    content = f.read()

if "alert/test" not in content:
    endpoints = """
# ─────────────────────────────────────────────────────────────────────────────
# POST /api/alert/test
# ─────────────────────────────────────────────────────────────────────────────

from alerting.main import run as alerting_run

@api_bp.route('/alert/test', methods=['POST'])
def test_alert():
    try:
        config = current_app.finops_config
        result = alerting_run(config=config)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""
    with open(api_py_path, 'w') as f:
        f.write(content + endpoints)
    print("Successfully patched api.py with alert endpoint")
else:
    print("api.py already patched with alert endpoint")
