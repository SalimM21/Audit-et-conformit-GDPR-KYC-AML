#!/bin/bash
# deploy_kibana_dashboard.sh
# -----------------------------
# Script pour déployer automatiquement les dashboards Kibana
# Nécessite Elasticsearch et Kibana en fonctionnement

# Variables
KIBANA_HOST="http://localhost:5601"
DASHBOARD_DIR="./dashboards/kibana"

# Vérifier la présence de curl
if ! command -v curl &> /dev/null
then
    echo "curl n'est pas installé. Veuillez l'installer pour continuer."
    exit 1
fi

# Fonction pour importer un dashboard
import_dashboard() {
    local file=$1
    echo "Importation du dashboard $file..."
    response=$(curl -s -X POST "$KIBANA_HOST/api/saved_objects/_import?overwrite=true" \
        -H "kbn-xsrf: true" \
        --form file=@"$file")
    echo "$response"
}

# Parcourir tous les fichiers JSON dans le dossier dashboards/kibana
for dashboard in "$DASHBOARD_DIR"/*.json; do
    if [ -f "$dashboard" ]; then
        import_dashboard "$dashboard"
    fi
done

echo "Tous les dashboards ont été importés dans Kibana !"
