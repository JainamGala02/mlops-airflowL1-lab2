# Wine Clustering with Apache Airflow

Automated ML pipeline using Airflow to perform K-means clustering on the Wine dataset.

## Setup

1. Create `.env` file:
```bash
echo "AIRFLOW_UID=$(id -u)" > .env
```

2. Start containers:
```bash
docker-compose up -d
```

3. Wait for services to be healthy:
```bash
docker-compose ps
```

## Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow2`
- Password: `airflow2`

## Run DAG

1. Find `Wine_Clustering` DAG in the UI
2. Click the Play button to trigger
