import boto3

def lambda_list():
    # Get a list of all Lambda functions
    client = boto3.client("lambda")
    response = client.list_functions()
    return [function["FunctionName"] for function in response["Functions"]]

def create_alarm(lambda_name):
    # Create a CloudWatch alarm using Anomaly Detection
    client = boto3.client("cloudwatch")
    response = client.put_metric_alarm(
        AlarmName=f"lambda execution anomaly detected :: {lambda_name}",
        AlarmDescription=f"Alarm for Lambda function {lambda_name}",
        Metrics=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/Lambda",
                        "MetricName": "Invocations",
                        "Dimensions": [{"Name": "FunctionName", "Value": lambda_name}],
                    },
                    "Period": 60,
                    "Stat": "Average",
                },
                "ReturnData": True,
            },
            {
                "Id": "ad1",
                "Expression": "ANOMALY_DETECTION_BAND(m1, 2)",
                "Label": "Invocations (expected)",
                "ReturnData": True,
            },
        ],
        ThresholdMetricId="ad1",
        ComparisonOperator="GreaterThanUpperThreshold",
        EvaluationPeriods=1,
        DatapointsToAlarm=1,
        TreatMissingData="missing",
        AlarmActions=["arn:aws:sns:us-east-1:123456789012:my-alarm-topic"],
    )

    # Print a message to the terminal
    print(f"Alarm created for lambda {lambda_name}")

if __name__ == "__main__":
    # Get a list of Lambda function names
    lambda_names = lambda_list()

    # Create an alarm for each Lambda function
    for lambda_name in lambda_names:
        create_alarm(lambda_name)
