import boto3

def get_ec2_instances():
    ec2_client = boto3.client('ec2')
    instances = ec2_client.describe_instances()

    return instances['Reservations']

def is_windows_instance(instance):
    return instance.get('Platform', '').startswith('windows')

def create_memory_alarm(instance_id, instance_name, sns_topic_arn, memory_threshold=80):
    ec2_client = boto3.client('ec2')
    instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])

    if not is_windows_instance(instance_info['Reservations'][0]['Instances'][0]):
        print(f"Instance '{instance_id}' is not a Windows instance. Skipping memory alarm creation.")
        return

    cloudwatch_client = boto3.client('cloudwatch')

    alarm_name = f"EC2-{instance_name}-Memory"
    namespace = "CWAgent"
    metric_name = "Memory % Committed Bytes In Use"
    dimensions = [
        {
            "Name": "InstanceId",
            "Value": instance_id
        },
        {
            "Name": "objectname",
            "Value": "Memory"
        },
        {
            "Name": "InstanceType",
            "Value": instance_info['Reservations'][0]['Instances'][0]['InstanceType']
        },
        {
            "Name": "ImageId",
            "Value": instance_info['Reservations'][0]['Instances'][0]['ImageId']
        }
    ]
    comparison_operator = "GreaterThanOrEqualToThreshold"
    threshold = memory_threshold
    evaluation_periods = 1
    period = 300
    statistic = "Average"

    response = cloudwatch_client.put_metric_alarm(
        AlarmName=alarm_name,
        ActionsEnabled=True,
        MetricName=metric_name,
        Namespace=namespace,
        Statistic=statistic,
        Dimensions=dimensions,
        Period=period,
        EvaluationPeriods=evaluation_periods,
        DatapointsToAlarm=1,
        Threshold=threshold,
        AlarmActions=[sns_topic_arn],
        ComparisonOperator=comparison_operator,
        TreatMissingData='missing'
    )

    print(f"Memory alarm '{alarm_name}' created for instance '{instance_name}' with ID '{instance_id}'")
    return response

def create_disk_alarm(instance_id, instance_name, sns_topic_arn, disk_threshold=20):
    ec2_client = boto3.client('ec2')
    instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])

    if not is_windows_instance(instance_info['Reservations'][0]['Instances'][0]):
        print(f"Instance '{instance_id}' is not a Windows instance. Skipping disk alarm creation.")
        return

    cloudwatch_client = boto3.client('cloudwatch')

    alarm_name = f"EC2-{instance_name}-FreeSpace"
    namespace = "CWAgent"
    metric_name = "LogicalDisk % Free Space"
    dimensions = [
        {
            "Name": "InstanceId",
            "Value": instance_id
        },
        {
            "Name": "objectname",
            "Value": "LogicalDisk"
        },
        {
            "Name": "instance",
            "Value": "C:"
        },
        {
            "Name": "InstanceType",
            "Value": instance_info['Reservations'][0]['Instances'][0]['InstanceType']
        },
        {
            "Name": "ImageId",
            "Value": instance_info['Reservations'][0]['Instances'][0]['ImageId']
        }
    ]
    comparison_operator = "LessThanOrEqualToThreshold"
    threshold = disk_threshold
    evaluation_periods = 1
    period = 300
    statistic = "Average"

    response = cloudwatch_client.put_metric_alarm(
        AlarmName=alarm_name,
        ActionsEnabled=True,
        MetricName=metric_name,
        Namespace=namespace,
        Statistic=statistic,
        Dimensions=dimensions,
        Period=period,
        EvaluationPeriods=evaluation_periods,
        DatapointsToAlarm=1,
        Threshold=threshold,
        AlarmActions=[sns_topic_arn],
        ComparisonOperator=comparison_operator,
        TreatMissingData='missing'
    )

    print(f"Disk alarm '{alarm_name}' created for instance '{instance_name}' with ID '{instance_id}'")
    return response

def create_cpu_utilization_alarm(instance_name, instance_id, sns_topic_arn):
    ec2_client = boto3.client('ec2')
    instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])

    if not is_windows_instance(instance_info['Reservations'][0]['Instances'][0]):
        print(f"Instance '{instance_id}' is not a Windows instance. Skipping CPU utilization alarm creation.")
        return

    cloudwatch = boto3.client('cloudwatch')

    response = cloudwatch.put_metric_alarm(
        AlarmName=f'EC2-{instance_name}-CPUUtilization',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=300,
        Statistic='Average',
        Threshold=80.0,
        ActionsEnabled=True,
        AlarmActions=[sns_topic_arn],
        AlarmDescription='Alarm when CPU exceeds 80%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        Unit='Percent'
    )

    print(f"CPU Utilization alarm created for instance '{instance_name}' with ID '{instance_id}'")
    return response

if __name__ == "__main__":
    instances = get_ec2_instances()
    sns_topic_arn = input("Digite o ARN do tópico SNS: ")

    for reservation in instances:
        for instance in reservation.get('Instances', []):
            instance_id = instance['InstanceId']
            instance_name = ''
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

            create_memory_alarm(instance_id, instance_name, sns_topic_arn)
            create_disk_alarm(instance_id, instance_name, sns_topic_arn)
            create_cpu_utilization_alarm(instance_name, instance_id, sns_topic_arn)
            
