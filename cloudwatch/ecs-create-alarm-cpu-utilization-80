import boto3

# Pergunta ao usuário qual é o ARN do tópico SNS
sns_topic_arn = input("Informe o ARN do tópico SNS: ")

# Pergunta ao usuário qual é a região
region = input("Informe a região: ")

# Cria um cliente ECS usando a região informada
ecs_client = boto3.client('ecs', region_name=region)

# Lista todos os clusters
clusters = ecs_client.list_clusters()
cluster_arns = clusters['clusterArns']

# Lista todos os serviços e cria alarmes para CPU Utilization em cada serviço
for cluster_arn in cluster_arns:
    cluster_name = cluster_arn.split('/')[-1]

    # Lista todos os serviços no cluster
    services = ecs_client.list_services(cluster=cluster_name)
    service_arns = services['serviceArns']

    for service_arn in service_arns:
        service_name = service_arn.split('/')[-1]

        # Cria o alarme de CPU Utilization para o serviço
        alarm_name = f"ECS-{cluster_name}-{service_name}-CPU-Utilization"
        cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=alarm_name,
            MetricName="CPUUtilization",
            Namespace="AWS/ECS",
            Statistic="Average",
            Dimensions=[{'Name': 'ClusterName', 'Value': cluster_name}, {'Name': 'ServiceName', 'Value': service_name}],
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            Period=300,
            Threshold=80,
            EvaluationPeriods=2,
            AlarmActions=[sns_topic_arn]
        )
