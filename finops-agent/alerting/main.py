import os
import yaml
import logging
from alerting.slack_notifier import SlackNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load config.yaml from finops-agent directory."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run(config: dict = None) -> dict:
    """
    Main entry point for the Alerting Agent.
    Called by the LangGraph pipeline.
    """
    if config is None:
        config = load_config()
        
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    
    if not slack_webhook_url:
        logger.warning("SLACK_WEBHOOK_URL environment variable is not set. Skipping Slack notifications.")
        return {"alerts_sent": 0, "status": "skipped"}
        
    bucket_name = config.get('storage', {}).get('bucket', 'finops-cur-data-louay')
    region = config.get('aws', {}).get('region', 'eu-north-1')
    
    logger.info("Starting Alerting Agent...")
    notifier = SlackNotifier(bucket_name=bucket_name, webhook_url=slack_webhook_url, region=region)
    
    alerts_count = notifier.notify()
    
    logger.info(f"Alerting Agent completed. Total alerts sent: {alerts_count}")
    return {"alerts_sent": alerts_count, "status": "success"}

if __name__ == "__main__":
    result = run()
    print(f"Result: {result}")
