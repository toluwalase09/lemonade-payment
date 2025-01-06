from prometheus_client import start_http_server, Gauge
import requests
import time
import os

# Define metrics
queue_messages = Gauge("rabbitmq_individual_queue_messages", "Total messages", ["host", "vhost", "name"])
queue_ready = Gauge("rabbitmq_individual_queue_messages_ready", "Messages ready", ["host", "vhost", "name"])
queue_unacked = Gauge("rabbitmq_individual_queue_messages_unacknowledged", "Unacknowledged messages", ["host", "vhost", "name"])

# Environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

def fetch_metrics():
    url = f"http://{RABBITMQ_HOST}:15672/api/queues"
    auth = (RABBITMQ_USER, RABBITMQ_PASSWORD)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    return []

def update_metrics(data):
    for queue in data:
        host = RABBITMQ_HOST
        vhost = queue["vhost"]
        name = queue["name"]
        queue_messages.labels(host, vhost, name).set(queue.get("messages", 0))
        queue_ready.labels(host, vhost, name).set(queue.get("messages_ready", 0))
        queue_unacked.labels(host, vhost, name).set(queue.get("messages_unacknowledged", 0))

if __name__ == "__main__":
    start_http_server(8000)
    while True:
        metrics = fetch_metrics()
        update_metrics(metrics)
        time.sleep(10)