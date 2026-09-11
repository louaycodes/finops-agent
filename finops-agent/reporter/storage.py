import boto3
import logging
import io
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class ReportStorage:
    """Uploads the generated PDF report to S3."""
    
    def __init__(self, bucket_name: str, region: str = "eu-north-1"):
        self.bucket = bucket_name
        self.client = boto3.client("s3", region_name=region)
        
    def save_report(self, pdf_bytes: io.BytesIO, filename: str) -> str:
        """Saves a PDF in-memory buffer to S3 under reports/ prefix."""
        key = f"reports/{filename}"
        try:
            # Ensure we read from the beginning of the buffer
            pdf_bytes.seek(0)
            
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=pdf_bytes.getvalue(),
                ContentType='application/pdf'
            )
            s3_path = f"s3://{self.bucket}/{key}"
            logger.info(f"PDF report saved successfully to {s3_path}")
            return s3_path
        except ClientError as e:
            logger.error(f"Error saving PDF report to S3: {str(e)}")
            raise
