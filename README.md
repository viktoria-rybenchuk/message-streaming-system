# Kafka Message Streaming System

Distributed application using Kafka for investigating throughput with different configurations of producers, consumers, partitions, and replicas.

## Components

- **Generator** (reddit_streamer): Splits dataset into messages and sends to Kafka
- **Processor** (comment_processor): Receives messages, sleeps 1 sec, logs timestamps (comment timestamp + consumer ID)
- **Aggregator** (metrics_aggregator): Generates reports with throughput (Mbps) and max latency (ms)

## Dataset

Reddit comments CSV (subreddit data)

## Quick Start

```bash
# Start system
docker-compose up --build -d

# Generate report
docker-compose run --rm aggregator

# View results
docker run --rm -v message-streaming-system_reports:/reports -v $(pwd):/output alpine cp -r /reports /output/

# Stop
docker-compose down -v
```

## Experiments

Run configurations to compare throughput and latency:

```bash
# All experiments
bash scripts/run-all-experiments.sh

# Specific experiment
bash scripts/run-all-experiments.sh 1
```

### Configuration Matrix

1. 1 producer, 1 partition, 1 consumer
2. 1 producer, 1 partition, 2 consumers
3. 1 producer, 2 partitions, 2 consumers
4. 1 producer, 5 partitions, 5 consumers
5. 1 producer, 10 partitions, 1 consumer
6. 1 producer, 10 partitions, 5 consumers
7. 1 producer, 10 partitions, 10 consumers
8. 2 producers, 10 partitions, 10 consumers

### Split Dataset for Multi-Producer

```bash
python scripts/split_dataset.py 2 datasets/lifestyle_progresspics.csv
```

### Visualize Results

```bash
python scripts/visualize_results.py
```

Graph: `reports/experiment_results.png`

## Monitoring

- Kafka UI: http://localhost:8080
- Consumer logs: `docker-compose logs -f consumer1 consumer2`
- Metrics: Throughput (Mbps), Latency (max time from send to processing completion)