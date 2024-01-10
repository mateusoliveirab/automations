import boto3

def list_certificates():
    client = boto3.client('acm')
    response = client.list_certificates()

    certificate_details = []
    for cert in response['CertificateSummaryList']:
        cert_details = {
            'CertificateArn': cert['CertificateArn'],
            'DomainName': cert['DomainName']
        }
        certificate_details.append(cert_details)

    return certificate_details

def create_cloudwatch_alarm(cert_details, days_threshold, sns_topic_arn):
    client = boto3.client('cloudwatch')

    # Extrai informações do certificado
    cert_arn = cert_details['CertificateArn']
    cert_id = cert_arn.split('/')[-1]
    domain_name = cert_details['DomainName']

    # Define o nome do alarme com o padrão desejado
    alarm_name = f"O certificado {cert_id} está a {days_threshold} dias para expirar ({domain_name})"

    # Define a métrica para o alarme
    metric_name = 'DaysToExpiry'
    namespace = 'AWS/CertificateManager'
    dimensions = [
        {
            'Name': 'CertificateArn',
            'Value': cert_arn
        }
    ]

    # Define a configuração do alarme
    alarm_actions = [sns_topic_arn]  # Substitua pelo ARN do seu tópico SNS

    # Criação do alarme
    response = client.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmDescription=f"O certificado {cert_id} está a {days_threshold} dias para expirar",
        ActionsEnabled=True,
        AlarmActions=alarm_actions,
        MetricName=metric_name,
        Namespace=namespace,
        Statistic='Minimum',
        Dimensions=dimensions,
        Period=300,
        EvaluationPeriods=1,
        Threshold=days_threshold,
        ComparisonOperator='LessThanThreshold',
        TreatMissingData='notBreaching'  # Define como tratar dados ausentes como 'good'
    )

    return response

def main():
    # Substitua com o ARN do seu tópico SNS
    sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:your-sns-topic'

    # Defina o limite de dias para o alarme (ex: 30 dias)
    threshold_days = 30

    # Lista todos os detalhes dos certificados ativos
    certificate_details = list_certificates()

    # Cria alarmes para cada certificado
    for cert in certificate_details:
        response = create_cloudwatch_alarm(cert, threshold_days, sns_topic_arn)
        print(f"Alarme criado para {cert['CertificateArn']}: {response}")

if __name__ == "__main__":
    main()
