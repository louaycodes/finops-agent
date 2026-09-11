import os

api_py_path = '../finops-rag-api/routes/api.py'
with open(api_py_path, 'r') as f:
    content = f.read()

# Make sure we don't append twice
if "report/generate" not in content:
    imports = "from flask import send_file\nimport io\nimport os\nimport sys\nimport boto3\n"
    content = imports + content
    
    endpoints = """

# ─────────────────────────────────────────────────────────────────────────────
# GET /api/report/generate
# ─────────────────────────────────────────────────────────────────────────────

finops_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../finops-agent'))
if finops_agent_dir not in sys.path:
    sys.path.insert(0, finops_agent_dir)

from reporter.main import generate_report_pipeline

@api_bp.route('/report/generate', methods=['GET'])
def generate_report():
    try:
        s3_key, pdf_bytes = generate_report_pipeline()
        filename = s3_key.split('/')[-1]
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/report/list', methods=['GET'])
def list_reports():
    try:
        s3 = boto3.client('s3')
        bucket = "finops-cur-data-louay"
        prefix = "reports/"
        
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        reports = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.pdf'):
                    filename = obj['Key'].split('/')[-1]
                    generated_at = obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
                    size_kb = int(obj['Size'] / 1024)
                    reports.append({
                        "filename": filename,
                        "generated_at": generated_at,
                        "size_kb": size_kb
                    })
                    
        reports = sorted(reports, key=lambda x: x['generated_at'], reverse=True)
        return jsonify({"reports": reports})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/report/download/<filename>', methods=['GET'])
def download_report(filename):
    try:
        s3 = boto3.client('s3')
        bucket = "finops-cur-data-louay"
        key = f"reports/{filename}"
        
        response = s3.get_object(Bucket=bucket, Key=key)
        pdf_bytes = response['Body'].read()
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""
    with open(api_py_path, 'w') as f:
        f.write(content + endpoints)
    print("Successfully patched api.py")
else:
    print("api.py already patched")
