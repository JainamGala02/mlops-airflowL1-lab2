# Wine Clustering with Apache Airflow

DADS 7305 - Machine Learning Operations (MLOps) | Lab 2

> **Note:** The original lab performs K-Means clustering on a generic CSV dataset with a basic DAG pipeline. For my implementation, I've swapped in sklearn's Wine dataset (178 samples, 13 chemical features) and built a complete pipeline that loads data, preprocesses it, trains K-Means with the elbow method (using the `kneed` library), and saves the final model. The Airflow DAG structure, XCom data passing, and Docker setup remain consistent with the original lab - refer to the [original lab README](https://www.mlwithramin.com/blog/airflow-lab1) and [video walkthrough](https://youtu.be/exFSeGUbn4Q?feature=shared) for foundational concepts.

## Folder Structure

```
├── dags/
│   └── airflow.py              # DAG definition with task dependencies
├── src/
│   └── lab.py                  # load_data, preprocessing, model building, elbow method
├── data/                       # output artifacts (model, data)
├── docker-compose.yaml         # Airflow services config
├── .env                        # Airflow UID
└── README.md
```

## Prerequisites

- Docker Desktop installed and running (allocate at least 4GB memory, ideally 8GB)
- `docker compose` CLI available (comes with Docker Desktop)

Verify you have enough memory:

```bash
docker run --rm "debian:bullseye-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'
```

## Setup & Run

**1. Clone the repo and navigate to the project directory:**

```bash
git clone <repo-url>
cd airflow_lab
```

**2. Create the `.env` file:**

This sets the Airflow user ID to your current OS user so file permissions work correctly inside the containers.

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

**3. Create required directories (if not already present):**

```bash
mkdir -p ./dags ./logs ./plugins ./working_data
```

**4. Verify `docker-compose.yaml` settings:**

Make sure the following are set in your `docker-compose.yaml`:

```yaml
# don't load example DAGs
AIRFLOW__CORE__LOAD_EXAMPLES: 'false'

# additional python packages needed by the pipeline
_PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:- pandas scikit-learn kneed }

# mount working data directory
- ${AIRFLOW_PROJ_DIR:-.}/working_data:/opt/airflow/working_data

# admin credentials
_AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow2}
_AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow2}
```

**5. Initialize the Airflow database:**

This runs the DB migrations and creates the admin user. Only needed on first setup.

```bash
docker compose up airflow-init
```

Wait until you see a `0` exit code, then proceed.

**6. Start all Airflow services:**

```bash
docker compose up -d
```

**7. Wait for services to become healthy:**

```bash
docker compose ps
```

All services (`airflow-webserver`, `airflow-scheduler`, `airflow-worker`, etc.) should show `healthy`. This can take 1-2 minutes on first boot. You can also watch logs in real time:

```bash
docker compose logs -f airflow-webserver
```

Look for the health check line:

```
airflow-webserver-1  | 127.0.0.1 - - [..] "GET /health HTTP/1.1" 200 ...
```

## Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow2`
- Password: `airflow2`

## Run the DAG

**1.** Open the Airflow UI and find the `Wine_Clustering` DAG in the DAGs list.

**2.** Toggle the DAG switch to **On** (enabled).

**3.** Click the **Play** button (Trigger DAG) to start a manual run.

**4.** Monitor the run by clicking into the DAG and switching to the **Graph** view. The pipeline executes four tasks in sequence:

```
load_data_task → data_preprocessing_task → build_save_model_task → load_model_task
```

- `load_data_task` - loads the Wine dataset, serializes it, and pushes it via XCom
- `data_preprocessing_task` - pulls data from XCom, applies scaling/feature selection, pushes preprocessed data
- `build_save_model_task` - trains K-Means for k=2..10, computes SSE values, saves the model to disk, pushes SSE via XCom
- `load_model_task` - loads the saved model, applies the elbow method (kneed) on SSE values to determine optimal k

**5.** Click on any task → **Logs** to see detailed output and verify results.

## Stopping the Environment

```bash
docker compose down
```

To also remove volumes (wipes the Airflow DB and all state):

```bash
docker compose down -v
```
