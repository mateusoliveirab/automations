import boto3

def create_rds_alarms():
    # Inicialize o cliente do boto3 para o CloudWatch
    cloudwatch = boto3.client('cloudwatch')
    
    # Inicialize o cliente do boto3 para o RDS
    rds = boto3.client('rds')

    # Liste todos os bancos de dados RDS na sua conta
    rds_instances = rds.describe_db_instances()

    # Para cada instância RDS, crie os alarmes conforme as condições
    for instance in rds_instances['DBInstances']:
        instance_identifier = instance['DBInstanceIdentifier']
        engine = instance['Engine']

        # Alarme para CPUUtilization
        cloudwatch.put_metric_alarm(
            AlarmName=f"RDS-{engine}-{instance_identifier}-CPUUtilization",
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='CPUUtilization',
            Namespace='AWS/RDS',
            Period=300,
            Statistic='Average',
            Threshold=80.0,
            ActionsEnabled=True,
            AlarmDescription='Alarm when CPUUtilization exceeds 80%',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_identifier}],
            Unit='Percent'
        )

        # Alarme para FreeableMemory
        cloudwatch.put_metric_alarm(
            AlarmName=f"RDS-{engine}-{instance_identifier}-FreeableMemory",
            ComparisonOperator='LessThanThreshold',
            EvaluationPeriods=1,
            MetricName='FreeableMemory',
            Namespace='AWS/RDS',
            Period=300,
            Statistic='Average',
            Threshold=2 * 1024 * 1024 * 1024,  # Convertendo para bytes
            ActionsEnabled=True,
            AlarmDescription='Alarm when FreeableMemory is less than 2GB',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_identifier}],
            Unit='Bytes'
        )

        # Alarme para FreeStorageSpace
        cloudwatch.put_metric_alarm(
            AlarmName=f"RDS-{engine}-{instance_identifier}-FreeStorageSpace",
            ComparisonOperator='LessThanThreshold',
            EvaluationPeriods=1,
            MetricName='FreeStorageSpace',
            Namespace='AWS/RDS',
            Period=300,
            Statistic='Average',
            Threshold=10 * 1024 * 1024 * 1024,  # Convertendo para bytes
            ActionsEnabled=True,
            AlarmDescription='Alarm when FreeStorageSpace is less than 10GB',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_identifier}],
            Unit='Bytes'
        )

if __name__ == "__main__":
    create_rds_alarms()
