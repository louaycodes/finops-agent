import boto3
import json
import logging
import requests
from botocore.exceptions import ClientError
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SlackNotifier:
    """Slack webhook notifier for High severity anomalies."""

    def __init__(self, bucket_name: str, webhook_url: str, region: str = "eu-north-1"):
        self.bucket = bucket_name
        self.webhook_url = webhook_url
        self.client = boto3.client("s3", region_name=region)

    def _get_latest_anomalies(self) -> List[Dict[str, Any]]:
        """Gets the latest anomalies JSON from S3."""
        prefix = "anomalies/"
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            if 'Contents' not in response:
                return []
                
            json_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.json')]
            if not json_files:
                return []
                
            json_files.sort(key=lambda x: x['LastModified'], reverse=True)
            latest_key = json_files[0]['Key']
            
            logger.info(f"Loading anomalies from s3://{self.bucket}/{latest_key}")
            
            obj_response = self.client.get_object(Bucket=self.bucket, Key=latest_key)
            data = json.loads(obj_response['Body'].read().decode('utf-8'))
            return data.get('anomalies', [])
            
        except ClientError as e:
            logger.error(f"Error loading anomalies from S3: {str(e)}")
            return []
            
    def _send_slack_message(self, payload: dict) -> bool:
        """Sends the payload to the Slack webhook."""
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False

    def notify(self) -> int:
        """Reads anomalies, filters High severity, and sends Slack notifications."""
        anomalies = self._get_latest_anomalies()
        high_anomalies = [a for a in anomalies if a.get('severity') == 'High']
        
        if not high_anomalies:
            logger.info("No High severity anomalies found.")
            # Send positive summary
            payload = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "✅ *Bilan FinOps* : Aucune anomalie critique détectée aujourd'hui."}
                    }
                ]
            }
            if self._send_slack_message(payload):
                return 1
            return 0
            
        alerts_sent = 0
        for anomaly in high_anomalies:
            service = anomaly.get('service', 'Unknown')
            a_type = anomaly.get('type', 'Unknown')
            cost = anomaly.get('estimated_cost_usd', 0)
            desc = anomaly.get('description', 'No description provided')
            rec = anomaly.get('recommendation', 'No recommendation provided')
            
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "⚠️ FinOps Agent — Anomalie détectée", "emoji": True}
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Service:*\n{service}"},
                            {"type": "mrkdwn", "text": "*Sévérité:*\n🔴 High"},
                            {"type": "mrkdwn", "text": f"*Type:*\n{a_type}"},
                            {"type": "mrkdwn", "text": f"*Économies estimées:*\n${cost:.2f}"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Description:*\n{desc}"}
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Recommandation:*\n{rec}"}
                    },
                    {
                        "type": "divider"
                    }
                ]
            }
            
            if self._send_slack_message(payload):
                alerts_sent += 1
                
        logger.info(f"Sent {alerts_sent} High severity alerts to Slack.")
        return alerts_sent
