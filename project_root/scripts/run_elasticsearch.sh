#!/bin/bash
# run_elasticsearch.sh
# ----------------------
# Script pour lancer un cluster Elasticsearch + Kibana
# Configure les variables nécessaires et démarre les services

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null
then
    echo "Docker n'est pas installé. Veuillez l'installer pour continuer."
    exit 1
fi

# Définir les ports
ES_PORT=9200
KIBANA_PORT=5601

# Créer un réseau Docker pour Elasticsearch et Kibana
docker network create es_network 2>/dev/null

echo "Lancement du cluster Elasticsearch..."
docker run -d --name elasticsearch \
    --net es_network \
    -p $ES_PORT:9200 \
    -e "discovery.type=single-node" \
    -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
    docker.elastic.co/elasticsearch/elasticsearch:8.12.1

echo "Lancement de Kibana..."
docker run -d --name kibana \
    --net es_network \
    -p $KIBANA_PORT:5601 \
    -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
    docker.elastic.co/kibana/kibana:8.12.1

echo "Attente que Elasticsearch soit opérationnel..."
sleep 20

# Vérifier le statut d'Elasticsearch
curl -X GET "localhost:$ES_PORT/_cluster/health?pretty"

echo "Elasticsearch et Kibana ont été lancés avec succès !"
echo "Elasticsearch : http://localhost:$ES_PORT"
echo "Kibana       : http://localhost:$KIBANA_PORT"
