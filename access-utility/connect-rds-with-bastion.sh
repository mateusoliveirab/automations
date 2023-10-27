#!/bin/bash
# Pergunta o caminho para a chave SSH
read -p "Caminho para a chave SSH: " KEY_PATH

# Pergunta o nome de usuário do bastion
read -p "Nome de usuário do bastion: " USER

# Pergunta o endpoint do bastion
read -p "Endpoint do bastion: " BASTION_ENDPOINT

# Pergunta o endpoint do RDS
read -p "Endpoint do RDS: " ENDPOINT_RDS

# Cria o comando SSH
CMD="ssh -i $KEY_PATH $USER@$BASTION_ENDPOINT -L 9090:$ENDPOINT_RDS:3306"

# Inicia o processo SSH em segundo plano usando screen
screen -dmS ssh $CMD

# Captura o pid do processo SSH
pid=$(screen -ls | grep ssh | awk '{print $1}')

# Registra o pid no arquivo /tmp/ssh_monitor.pid
echo $pid > /tmp/ssh_monitor.pid

# Sai do shell, mas não finaliza a sessão SSH
exit
