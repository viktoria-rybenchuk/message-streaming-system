#!/bin/bash
set -e

# Change to project root directory
cd "$(dirname "$0")/.."

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WAIT_TIME=60

function print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

function print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

function cleanup() {
    print_info "Cleaning up..."
    docker-compose down -v 2>/dev/null || true
    docker rm -f producer1 producer2 2>/dev/null || true

    # Clear all logs for fresh start
    rm -rf logs/*.csv 2>/dev/null || true
    mkdir -p logs reports

    sleep 5
}

function wait_for_kafka() {
    print_info "Waiting for Kafka to be healthy..."
    sleep 10
    for i in {1..30}; do
        if docker-compose ps kafka 2>/dev/null | grep -q "healthy"; then
            print_info "Kafka is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    echo -e "${RED}Error: Kafka failed to become healthy${NC}"
    exit 1
}

function create_topic() {
    local partitions=$1
    print_info "Creating topic with $partitions partition(s)..."

    docker-compose exec -T kafka kafka-topics \
        --delete --if-exists \
        --topic reddit-comments \
        --bootstrap-server kafka:9092 2>/dev/null || true

    sleep 3

    docker-compose exec -T kafka kafka-topics \
        --create \
        --topic reddit-comments \
        --partitions "$partitions" \
        --replication-factor 1 \
        --bootstrap-server kafka:9092

    print_info "Topic created successfully"
}

function verify_logs_created() {
    print_info "Verifying log files are being created..."
    for i in {1..15}; do
        if ls logs/*.csv 1> /dev/null 2>&1; then
            print_info "Log files detected:"
            ls -lh logs/*.csv
            return 0
        fi
        echo -n "."
        sleep 1
    done
    echo ""
    echo -e "${RED}Warning: No log files created after 15 seconds${NC}"
    return 1
}

function wait_for_processing() {
    print_info "Processing messages for ${WAIT_TIME} seconds..."
    local start_time=$(date +%s)

    for i in $(seq 1 $WAIT_TIME); do
        echo -n "."

        # Every 10 seconds, show progress
        if [ $((i % 10)) -eq 0 ]; then
            echo ""
            if ls logs/*.csv 1> /dev/null 2>&1; then
                echo -n "  [${i}s] Log files: "
                wc -l logs/*.csv 2>/dev/null | tail -1 | awk '{print $1 " total lines"}'
            else
                echo "  [${i}s] No log files yet"
            fi
            echo -n "  Progress: "
        fi
        sleep 1
    done

    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo ""
    print_info "Measurement complete (${elapsed}s actual)"

    # Show final log file status
    if ls logs/*.csv 1> /dev/null 2>&1; then
        echo ""
        echo "Final log files:"
        ls -lh logs/*.csv
        echo ""
        echo "Total messages logged:"
        wc -l logs/*.csv 2>/dev/null
    else
        echo -e "${RED}Error: No log files found after ${elapsed}s${NC}"
        return 1
    fi
}

function generate_report() {
    local experiment_name=$1
    print_info "Generating metrics for $experiment_name..."

    echo ""
    echo "=== Aggregator Output ==="
    docker-compose run --rm aggregator
    local aggregator_exit=$?
    echo "=== End Aggregator Output ==="
    echo ""

    if [ $aggregator_exit -ne 0 ]; then
        echo -e "${RED}Warning: Aggregator exited with code $aggregator_exit${NC}"
    fi

    if ls reports/metrics_report_*.json 1> /dev/null 2>&1; then
        latest_report=$(ls -t reports/metrics_report_*.json 2>/dev/null | head -1)
        if [ -f "$latest_report" ]; then
            mv "$latest_report" "reports/${experiment_name}.json"
            print_info "Report saved: reports/${experiment_name}.json"
        fi
    else
        echo -e "${YELLOW}Warning: No report generated${NC}"
        echo "Checking for log files:"
        ls -lh logs/ 2>/dev/null || echo "logs/ directory not found or empty"
    fi
}

function show_metrics() {
    local report_file=$1
    if [ -f "$report_file" ]; then
        echo ""
        echo "=== Metrics Summary ==="
        echo -n "Throughput: "
        jq -r '.throughput.mbps' "$report_file"
        echo -n "Max Latency: "
        jq -r '.latency.max_ms' "$report_file"
        echo -n "Messages: "
        jq -r '.messages.total' "$report_file"
        echo -n "Messages/sec: "
        jq -r '.messages.per_second' "$report_file"
        echo ""
    fi
}

function run_experiment_1() {
    print_header "Experiment 1: 1 Producer, 1 Partition, 1 Consumer"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 1

    print_info "Starting producer and consumer..."
    docker-compose up -d --scale consumer=1 producer consumer

    print_info "Waiting for consumer to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp1_1prod_1part_1cons"
    show_metrics "reports/exp1_1prod_1part_1cons.json"

    print_info "Experiment 1 complete!"
}

function run_experiment_2() {
    print_header "Experiment 2: 1 Producer, 1 Partition, 2 Consumers"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 1

    print_info "Starting producer and consumers..."
    docker-compose up -d --scale consumer=2 producer consumer

    print_info "Waiting for consumers to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp2_1prod_1part_2cons"
    show_metrics "reports/exp2_1prod_1part_2cons.json"

    print_info "Experiment 2 complete!"
}

function run_experiment_3() {
    print_header "Experiment 3: 1 Producer, 2 Partitions, 2 Consumers"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 2

    print_info "Starting producer and consumers..."
    docker-compose up -d --scale consumer=2 producer consumer

    print_info "Waiting for consumers to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp3_1prod_2part_2cons"
    show_metrics "reports/exp3_1prod_2part_2cons.json"

    print_info "Experiment 3 complete!"
}

function run_experiment_4() {
    print_header "Experiment 4: 1 Producer, 5 Partitions, 5 Consumers"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 5

    print_info "Starting producer and consumers..."
    docker-compose up -d --scale consumer=5 producer consumer

    print_info "Waiting for consumers to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp4_1prod_5part_5cons"
    show_metrics "reports/exp4_1prod_5part_5cons.json"

    print_info "Experiment 4 complete!"
}

function run_experiment_5() {
    print_header "Experiment 5: 1 Producer, 10 Partitions, 1 Consumer"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 10

    print_info "Starting producer and consumer..."
    docker-compose up -d --scale consumer=1 producer consumer

    print_info "Waiting for consumer to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp5_1prod_10part_1cons"
    show_metrics "reports/exp5_1prod_10part_1cons.json"

    print_info "Experiment 5 complete!"
}

function run_experiment_6() {
    print_header "Experiment 6: 1 Producer, 10 Partitions, 5 Consumers"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 10

    print_info "Starting producer and consumers..."
    docker-compose up -d --scale consumer=5 producer consumer

    print_info "Waiting for consumers to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp6_1prod_10part_5cons"
    show_metrics "reports/exp6_1prod_10part_5cons.json"

    print_info "Experiment 6 complete!"
}

function run_experiment_7() {
    print_header "Experiment 7: 1 Producer, 10 Partitions, 10 Consumers"

    cleanup
    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 10

    print_info "Starting producer and consumers..."
    docker-compose up -d --scale consumer=10 producer consumer

    print_info "Waiting for consumers to join group and reach steady state (30s)..."
    sleep 30

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop producer consumer

    generate_report "exp7_1prod_10part_10cons"
    show_metrics "reports/exp7_1prod_10part_10cons.json"

    print_info "Experiment 7 complete!"
}

function run_experiment_8() {
    print_header "Experiment 8: 2 Producers, 10 Partitions, 10 Consumers"

    cleanup

    print_info "Splitting dataset into 2 parts..."
    python3 scripts/split_dataset.py 2 datasets/lifestyle_progresspics.csv

    print_info "Verifying dataset split..."
    wc -l datasets/split/*.csv

    docker-compose up -d kafka kafka-ui
    wait_for_kafka
    create_topic 10

    print_info "Ensuring producer image is built..."
    docker-compose build producer 2>/dev/null || true

    print_info "Starting consumers first..."
    docker-compose up -d --scale consumer=10 --no-deps consumer

    print_info "Waiting for consumers to join group (10s)..."
    sleep 10

    print_info "Starting producer1 with part1.csv..."
    docker run -d --name producer1 \
        --network message-streaming-system_kafka-net \
        -v "$(pwd)/datasets:/app/datasets" \
        -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
        -e KAFKA_TOPIC=reddit-comments \
        -e DATASET_PATH=datasets/split/lifestyle_progresspics_part1.csv \
        -e MESSAGE_DELAY_SEC=0.1 \
        message-streaming-system-producer

    print_info "Starting producer2 with part2.csv..."
    docker run -d --name producer2 \
        --network message-streaming-system_kafka-net \
        -v "$(pwd)/datasets:/app/datasets" \
        -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
        -e KAFKA_TOPIC=reddit-comments \
        -e DATASET_PATH=datasets/split/lifestyle_progresspics_part2.csv \
        -e MESSAGE_DELAY_SEC=0.1 \
        message-streaming-system-producer

    print_info "Waiting for system to reach steady state (20s)..."
    sleep 20

    print_info "Starting clean 60-second measurement (clearing logs, no restart)..."
    rm -f logs/*.csv 2>/dev/null || true
    sleep 2
    verify_logs_created

    wait_for_processing

    print_info "Stopping services..."
    docker-compose stop consumer
    docker stop producer1 producer2

    print_info "Checking producer logs..."
    echo "Producer1 final messages:"
    docker logs producer1 2>&1 | grep -E "Total messages sent|Sent.*messages" | tail -3

    echo ""
    echo "Producer2 final messages:"
    docker logs producer2 2>&1 | grep -E "Total messages sent|Sent.*messages" | tail -3

    docker rm -f producer1 producer2

    generate_report "exp8_2prod_10part_10cons"
    show_metrics "reports/exp8_2prod_10part_10cons.json"

    print_info "Experiment 8 complete!"
}

function run_all_experiments() {
    print_header "Running All 8 Experiments"

    mkdir -p reports logs

    run_experiment_1
    run_experiment_2
    run_experiment_3
    run_experiment_4
    run_experiment_5
    run_experiment_6
    run_experiment_7
    run_experiment_8

    print_header "All Experiments Complete!"
    echo ""
    echo "Reports generated:"
    ls -lh reports/*.json 2>/dev/null || echo "No reports found"
    echo ""
    echo "Run 'python scripts/visualize_results.py' to generate graphs"
    echo ""
}

case "${1:-all}" in
    1) run_experiment_1 ;;
    2) run_experiment_2 ;;
    3) run_experiment_3 ;;
    4) run_experiment_4 ;;
    5) run_experiment_5 ;;
    6) run_experiment_6 ;;
    7) run_experiment_7 ;;
    8) run_experiment_8 ;;
    all) run_all_experiments ;;
    clean) cleanup ;;
    *)
        print_header "Kafka Streaming Experiments"
        echo "Usage: $0 [1-8|all|clean]"
        echo ""
        echo "Experiments:"
        echo "  1) 1 Producer, 1 Partition, 1 Consumer"
        echo "  2) 1 Producer, 1 Partition, 2 Consumers"
        echo "  3) 1 Producer, 2 Partitions, 2 Consumers"
        echo "  4) 1 Producer, 5 Partitions, 5 Consumers"
        echo "  5) 1 Producer, 10 Partitions, 1 Consumer"
        echo "  6) 1 Producer, 10 Partitions, 5 Consumers"
        echo "  7) 1 Producer, 10 Partitions, 10 Consumers"
        echo "  8) 2 Producers (split data), 10 Partitions, 10 Consumers"
        echo ""
        echo "  all)   Run all experiments sequentially"
        echo "  clean) Clean up Docker containers and volumes"
        echo ""
        ;;
esac