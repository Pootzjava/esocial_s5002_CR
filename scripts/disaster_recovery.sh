#!/bin/bash
# Script de Disaster Recovery para eSocial Rendimentos SaaS
# Este script realiza backup completo do banco de dados e configurações

set -e

# Configurações
BACKUP_DIR="/backups/esocial-rendimentos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
NAMESPACE="esocial-rendimentos"

echo "=== Iniciando Backup de Disaster Recovery ==="
echo "Timestamp: $TIMESTAMP"
echo "Backup Directory: $BACKUP_DIR"

# Criar diretório de backup
mkdir -p $BACKUP_DIR/{database,configs,secrets}

# Backup do PostgreSQL
echo "Realizando backup do PostgreSQL..."
kubectl exec -n $NAMESPACE $(kubectl get pods -n $NAMESPACE -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  pg_dump -U user esocial_db | gzip > $BACKUP_DIR/database/esocial_db_$TIMESTAMP.sql.gz

# Backup das configurações
echo "Salvando configurações do Kubernetes..."
kubectl get configmap -n $NAMESPACE -o yaml > $BACKUP_DIR/configs/configmaps_$TIMESTAMP.yaml
kubectl get secrets -n $NAMESPACE -o yaml > $BACKUP_DIR/secrets/secrets_$TIMESTAMP.yaml (apenas metadados)
kubectl get deployments -n $NAMESPACE -o yaml > $BACKUP_DIR/configs/deployments_$TIMESTAMP.yaml
kubectl get statefulsets -n $NAMESPACE -o yaml > $BACKUP_DIR/configs/statefulsets_$TIMESTAMP.yaml
kubectl get services -n $NAMESPACE -o yaml > $BACKUP_DIR/configs/services_$TIMESTAMP.yaml

# Backup dos volumes persistentes (se aplicável)
echo "Criando snapshot dos volumes persistentes..."
# Nota: Implementação específica depende do provedor de cloud (AWS EBS, GCP PD, Azure Disk)

# Limpeza de backups antigos
echo "Limpando backups com mais de $RETENTION_DAYS dias..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Upload para storage externo (S3, GCS, etc.)
echo "Enviando backup para storage externo..."
# aws s3 cp $BACKUP_DIR s3://your-bucket/backups/$TIMESTAMP/ --recursive

echo "=== Backup Concluído com Sucesso ==="
echo "Localização: $BACKUP_DIR"
du -sh $BACKUP_DIR

# Script de Restore (comentado para segurança)
: <<'RESTORE_SCRIPT'
# Para restaurar:
# 1. kubectl apply -f k8s/namespace.yaml
# 2. kubectl apply -f k8s/configmap.yaml
# 3. kubectl apply -f k8s/secrets.yaml
# 4. kubectl apply -f k8s/postgres-statefulset.yaml
# 5. Aguardar PostgreSQL estar ready
# 6. gunzip -c backups/database/esocial_db_TIMESTAMP.sql.gz | kubectl exec -i postgres-pod -- psql -U user -d esocial_db
# 7. kubectl apply -f restante dos manifests
RESTORE_SCRIPT
