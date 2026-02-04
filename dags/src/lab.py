import pandas as pd
import numpy as np
import pickle
import os
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/opt/airflow')
DATA_PATH = os.path.join(AIRFLOW_HOME, 'dags/data')
MODEL_PATH = os.path.join(AIRFLOW_HOME, 'dags/model')


def load_data():
    print("Loading wine dataset......")
    wine = load_wine()
    df = pd.DataFrame(wine.data, columns=wine.feature_names)
    os.makedirs(DATA_PATH, exist_ok=True)
    csv_path = os.path.join(DATA_PATH, 'wine_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"Shape: {df.shape}")
    print(f"Features: {list(df.columns)}")
    print(f"Saved to {csv_path}")
    return csv_path


def data_preprocessing(csv_path):
    print("Preprocessing data......")
    df = pd.read_csv(csv_path)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    df_scaled = pd.DataFrame(scaled_data, columns=df.columns)
    print(f"Scaled shape: {df_scaled.shape}")
    print(f"Mean: {df_scaled.mean().mean():.4f}")
    print(f"Std: {df_scaled.std().mean():.4f}")
    os.makedirs(MODEL_PATH, exist_ok=True)
    with open(os.path.join(MODEL_PATH, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    # Save scaled data to CSV
    scaled_csv_path = os.path.join(DATA_PATH, 'wine_data_scaled.csv')
    df_scaled.to_csv(scaled_csv_path, index=False)
    return scaled_csv_path


def build_save_model(scaled_csv_path, model_filename='kmeans_model.pkl', **kwargs):
    print("Building models......")
    df = pd.read_csv(scaled_csv_path)
    X = df.values
    scores = {}
    models = {}
    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        scores[k] = score
        models[k] = kmeans
        print(f"for K={k}: Silhouette={score:.4f}")
    best_k = max(scores, key=scores.get)
    best_model = models[best_k]
    print(f"\nBest K: {best_k}")
    print(f"Best Score: {scores[best_k]:.4f}")
    os.makedirs(MODEL_PATH, exist_ok=True)
    model_path = os.path.join(MODEL_PATH, model_filename)
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"Model saved to {model_path}")
    # Save scores to JSON for easy passing
    scores_json_path = os.path.join(MODEL_PATH, 'scores.json')
    import json
    with open(scores_json_path, 'w') as f:
        json.dump({str(k): v for k, v in scores.items()}, f)
    return scores_json_path


def load_model_evaluate(model_filename, scores_json_path):
    print("Evaluating model...")
    model_path = os.path.join(MODEL_PATH, model_filename)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    import json
    with open(scores_json_path, 'r') as f:
        scores_dict = json.load(f)
    scores = {int(k): v for k, v in scores_dict.items()}
    optimal_k = max(scores, key=scores.get)
    optimal_score = scores[optimal_k]
    print("CLUSTERING RESULTS =")
    print()
    print("Dataset: Wine")
    print()
    print("Algorithm: K-Means")
    print()
    print("Metric: Silhouette Score")
    print()
    for k, score in sorted(scores.items()):
        marker = "= BEST MODEL" if k == optimal_k else ""
        print(f"K={k}: {score:.4f}{marker}")
    print()
    print(f"Optimal K: {optimal_k}")
    print(f"Score: {optimal_score:.4f}")
    print()
    return f"Optimal K={optimal_k}, Score={optimal_score:.4f}"