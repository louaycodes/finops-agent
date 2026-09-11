import boto3
import json
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReportDataLoader:
    """Loads latest JSON data from S3 for the PDF report."""
    
    def __init__(self, bucket_name: str, region: str = "eu-north-1"):
        self.bucket = bucket_name
        self.client = boto3.client("s3", region_name=region)
        
    def _get_latest_json(self, prefix: str) -> Dict[str, Any]:
        """Gets the most recently modified JSON file in a given prefix."""
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            if 'Contents' not in response:
                return {}
                
            # Filter json files and sort by LastModified desc
            json_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.json')]
            if not json_files:
                return {}
                
            json_files.sort(key=lambda x: x['LastModified'], reverse=True)
            latest_key = json_files[0]['Key']
            
            logger.info(f"Loading latest data from s3://{self.bucket}/{latest_key}")
            
            obj_response = self.client.get_object(Bucket=self.bucket, Key=latest_key)
            return json.loads(obj_response['Body'].read().decode('utf-8'))
            
        except ClientError as e:
            logger.error(f"Error loading {prefix} from S3: {str(e)}")
            return {}

    def load_all_data(self) -> Dict[str, Any]:
        """Loads anomalies, forecasts, and recommendations."""
        data = {
            "anomalies": self._get_latest_json("anomalies/"),
            "forecasts": self._get_latest_json("forecasts/"),
            "recommendations": self._get_latest_json("recommendations/")
        }
        return data
