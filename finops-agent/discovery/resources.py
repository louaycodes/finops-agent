import boto3

def extract_id_from_arn(arn: str) -> str:
    """
    Extrait l'ID ou le nom depuis l'ARN AWS.
    Sépare par ':' et gère les ressources contenant '/'
    """
    if not arn:
        return ""
        
    parts = arn.split(':', 5)
    if len(parts) < 6:
        return arn.split(':')[-1]
        
    service = parts[2]
    resource_part = parts[5]
    
    # S3: arn:aws:s3:::my-bucket
    if service == 's3':
        return resource_part
    
    # Pour Lambda: function:my-function -> my-function
    # EC2: instance/i-xxx -> i-xxx
    if '/' in resource_part:
        return resource_part.split('/')[-1]
    
    if ':' in resource_part:
        return resource_part.split(':')[-1]
        
    return resource_part


def discover_all(region: str) -> dict:
    """
    Appelle resource-explorer-2.search() pour découvrir toutes les ressources.
    """
    resources_by_type = {}
    
    try:
        client = boto3.client('resource-explorer-2', region_name=region)
        
        paginator = client.get_paginator('search')
        for page in paginator.paginate(QueryString="*", MaxResults=1000):
            for resource in page.get('Resources', []):
                # ResourceType typique: ec2:instance, rds:db, lambda:function
                res_type = resource.get('ResourceType', 'Unknown')
                arn = resource.get('Arn', '')
                
                if not arn:
                    continue
                    
                res_id = extract_id_from_arn(arn)
                
                if res_type not in resources_by_type:
                    resources_by_type[res_type] = []
                    
                resources_by_type[res_type].append(res_id)
                
        return resources_by_type

    except Exception as e:
        print(f"⚠️  [Resource Explorer] API indisponible ou non autorisée: {e}")
        return resources_by_type
