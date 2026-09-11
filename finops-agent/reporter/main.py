import os
import yaml
import logging
import datetime
from reporter.data_loader import ReportDataLoader
from reporter.pdf_generator import PDFGenerator
from reporter.storage import ReportStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load config.yaml from finops-agent directory."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_report_pipeline():
    """
    Main orchestration function for PDF generation.
    Returns:
        tuple: (s3_path, pdf_bytes_content)
    """
    logger.info("Starting PDF generation pipeline...")
    
    config = load_config()
    account_id = config.get('aws', {}).get('account_id', 'Unknown Account')
    bucket_name = config.get('storage', {}).get('bucket', 'finops-cur-data-louay')
    
    # Extract discovered services
    discovered_resources = config.get('collector', {}).get('discovered_resources', {})
    services_list = list(discovered_resources.keys())
    
    # 1. Load Data
    loader = ReportDataLoader(bucket_name=bucket_name)
    data = loader.load_all_data()
    
    # 2. Generate PDF
    generator = PDFGenerator(account_id=account_id)
    pdf_buffer = generator.generate(data=data, discovered_services=services_list)
    
    if not pdf_buffer:
        raise ValueError("Failed to generate PDF buffer.")
        
    pdf_bytes_content = pdf_buffer.getvalue()
        
    # 3. Store PDF
    storage = ReportStorage(bucket_name=bucket_name)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"finops_report_{timestamp}.pdf"
    s3_path = storage.save_report(pdf_buffer, filename)
    
    logger.info("PDF generation pipeline completed successfully.")
    
    return s3_path, pdf_bytes_content

if __name__ == "__main__":
    s3_path, _ = generate_report_pipeline()
    print(f"Report generated and saved to: {s3_path}")
