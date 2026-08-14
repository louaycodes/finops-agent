import sys
sys.path.insert(0, '/var/task')

from collector.main import run

def handler(event, context):
    run()
    return {"statusCode": 200, "body": "Collector Agent terminé"}
