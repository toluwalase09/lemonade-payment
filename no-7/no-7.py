from prometheus_client import start_http_server, Gauge
import requests
import time
import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')

def get_queue_stats():
    """
    Fetches queue statistics from the RabbitMQ management API.

    Returns:
        A dictionary of queues with their statistics.
    """
    try:
        response = requests.get(
            f"http://{RABBITMQ_HOST}:15672/api/queues",
            auth=(RABBITMQ_USER, RABBITMQ_PASSWORD),
            verify=False  # Disable SSL verification for simplicity. In production, use proper SSL handling.
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching queue stats: {e}")
        return []

def main():
    # Create Prometheus metrics
    rabbitmq_individual_queue_messages = Gauge(
        'rabbitmq_individual_queue_messages',
        'Total number of messages in the queue',
        ['host', 'vhost', 'name']
    )
    rabbitmq_individual_queue_messages_ready = Gauge(
        'rabbitmq_individual_queue_messages_ready',
        'Number of ready messages in the queue',
        ['host', 'vhost', 'name']
    )
    rabbitmq_individual_queue_messages_unacknowledged = Gauge(
        'rabbitmq_individual_queue_messages_unacknowledged',
        'Number of unacknowledged messages in the queue',
        ['host', 'vhost', 'name']
    )

    # Start the HTTP server for Prometheus
    start_http_server(8000)

    while True:
        queues = get_queue_stats()
        for queue in queues:
            vhost = queue['vhost']
            name = queue['name']
            rabbitmq_individual_queue_messages.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(queue['messages'])
            rabbitmq_individual_queue_messages_ready.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(queue['messages_ready'])
            rabbitmq_individual_queue_messages_unacknowledged.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(queue['messages_unacknowledged'])

        time.sleep(60)  # Update metrics every 60 seconds

if __name__ == "__main__":
    main()