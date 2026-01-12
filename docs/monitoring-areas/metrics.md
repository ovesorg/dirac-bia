# Metrics Collection & Monitoring

Comprehensive guide to metrics collection, visualization, and analysis in the OVES ecosystem.

## Overview

Metrics provide quantitative measurements of system behavior, performance, and health. The OVES metrics infrastructure uses Prometheus for collection and storage, and Grafana for visualization and alerting.

## Metrics Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Metric Sources                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Kubernetes   │  │ Applications │  │ Databases    │          │
│  │ Components   │  │ /metrics     │  │ Exporters    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Discovery                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Prometheus Server                           │  │
│  │  - Kubernetes SD (ServiceMonitor, PodMonitor)            │  │
│  │  - Static Configs                                        │  │
│  │  - Scrape Targets Every 30s                              │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Time-Series Storage                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Prometheus TSDB                             │  │
│  │  - 15 days retention                                     │  │
│  │  - 100GB storage                                         │  │
│  │  - Compression enabled                                   │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Visualization & Alerting                     │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Grafana    │  │ AlertManager │  │   Prometheus │          │
│  │  Dashboards  │  │  Routing     │  │   Alerts     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Prometheus Setup

### Prometheus Configuration

```yaml
global:
  scrape_interval: 30s
  scrape_timeout: 10s
  evaluation_interval: 30s
  external_labels:
    cluster: oves-prod
    environment: production

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules
rule_files:
  - /etc/prometheus/rules/*.yml

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Kubernetes API server
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

  # Kubernetes nodes
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  # Kubernetes pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  # Service monitors (via Prometheus Operator)
  - job_name: 'kubernetes-service-endpoints'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        target_label: kubernetes_name
```

### ServiceMonitor Example

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: account-microservice
  namespace: monitoring
  labels:
    app: account-microservice
    release: prometheus
spec:
  selector:
    matchLabels:
      app: account-microservice
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
      scheme: http
  namespaceSelector:
    matchNames:
      - production
      - staging
```

## Metric Types

### 1. Counter

**Purpose**: Cumulative metric that only increases (or resets to zero)

**Use Cases**:
- Request counts
- Error counts
- Task completions
- Bytes transferred

**Example**:
```javascript
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

// Increment counter
httpRequestsTotal.inc({ method: 'GET', route: '/api/accounts', status_code: '200' });
```

**PromQL Queries**:
```promql
# Rate of requests per second
rate(http_requests_total[5m])

# Total requests in last hour
increase(http_requests_total[1h])

# Requests per minute by status code
sum(rate(http_requests_total[1m])) by (status_code)
```

### 2. Gauge

**Purpose**: Metric that can go up or down

**Use Cases**:
- Current memory usage
- Active connections
- Queue size
- Temperature readings

**Example**:
```javascript
const activeConnections = new promClient.Gauge({
  name: 'active_connections',
  help: 'Number of active database connections',
  labelNames: ['database']
});

// Set gauge value
activeConnections.set({ database: 'mongodb' }, 25);

// Increment/decrement
activeConnections.inc({ database: 'mongodb' });
activeConnections.dec({ database: 'mongodb' });
```

**PromQL Queries**:
```promql
# Current value
active_connections

# Average over time
avg_over_time(active_connections[5m])

# Max value in last hour
max_over_time(active_connections[1h])
```

### 3. Histogram

**Purpose**: Samples observations and counts them in configurable buckets

**Use Cases**:
- Request duration
- Response size
- Query execution time

**Example**:
```javascript
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

// Observe value
const end = httpRequestDuration.startTimer();
// ... process request ...
end({ method: 'GET', route: '/api/accounts', status_code: '200' });
```

**PromQL Queries**:
```promql
# 95th percentile response time
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# Average response time
rate(http_request_duration_seconds_sum[5m]) / 
rate(http_request_duration_seconds_count[5m])

# Requests slower than 1 second
sum(rate(http_request_duration_seconds_bucket{le="1"}[5m]))
```

### 4. Summary

**Purpose**: Similar to histogram but calculates quantiles on client side

**Use Cases**:
- Request latencies
- Response times when you need exact quantiles

**Example**:
```javascript
const requestLatency = new promClient.Summary({
  name: 'request_latency_seconds',
  help: 'Request latency in seconds',
  labelNames: ['service'],
  percentiles: [0.5, 0.9, 0.95, 0.99]
});

// Observe value
requestLatency.observe({ service: 'account' }, 0.234);
```

## Key Metrics by Component

### Application Metrics

#### HTTP Metrics
```javascript
// Request rate
http_requests_total

// Request duration
http_request_duration_seconds

// Request size
http_request_size_bytes

// Response size
http_response_size_bytes

// Active requests
http_requests_in_flight
```

#### Database Metrics
```javascript
// Connection pool
db_connections_active
db_connections_idle
db_connections_max

// Query performance
db_query_duration_seconds
db_queries_total
db_query_errors_total

// Operations
db_operations_total{operation="insert|update|delete|find"}
```

#### Business Metrics
```javascript
// User activity
user_registrations_total
user_logins_total
user_sessions_active

// Transactions
transactions_total{status="success|failed"}
transaction_amount_total
transaction_duration_seconds

// API usage
api_calls_total{endpoint="/api/accounts"}
api_quota_remaining
```

### Kubernetes Metrics

#### Node Metrics
```promql
# CPU usage
node_cpu_seconds_total

# Memory usage
node_memory_MemAvailable_bytes
node_memory_MemTotal_bytes

# Disk usage
node_filesystem_avail_bytes
node_filesystem_size_bytes

# Network I/O
node_network_receive_bytes_total
node_network_transmit_bytes_total
```

#### Pod Metrics
```promql
# Pod status
kube_pod_status_phase{phase="Running|Pending|Failed"}

# Container restarts
kube_pod_container_status_restarts_total

# Resource requests/limits
kube_pod_container_resource_requests{resource="cpu|memory"}
kube_pod_container_resource_limits{resource="cpu|memory"}

# Actual usage
container_cpu_usage_seconds_total
container_memory_working_set_bytes
```

#### Deployment Metrics
```promql
# Replica status
kube_deployment_status_replicas
kube_deployment_status_replicas_available
kube_deployment_status_replicas_unavailable

# Deployment conditions
kube_deployment_status_condition{condition="Available|Progressing"}
```

### Database Exporters

#### MongoDB Exporter
```promql
# Connections
mongodb_connections{state="current|available"}

# Operations
mongodb_op_counters_total{type="insert|query|update|delete"}

# Replication lag
mongodb_mongod_replset_member_replication_lag

# Memory
mongodb_memory{type="resident|virtual|mapped"}
```

#### Redis Exporter
```promql
# Connected clients
redis_connected_clients

# Memory usage
redis_memory_used_bytes
redis_memory_max_bytes

# Hit rate
redis_keyspace_hits_total
redis_keyspace_misses_total

# Commands processed
redis_commands_processed_total
```

#### PostgreSQL Exporter
```promql
# Active connections
pg_stat_database_numbackends

# Transaction rate
rate(pg_stat_database_xact_commit[5m])
rate(pg_stat_database_xact_rollback[5m])

# Cache hit ratio
pg_stat_database_blks_hit / 
(pg_stat_database_blks_hit + pg_stat_database_blks_read)

# Slow queries
pg_stat_statements_mean_time_seconds > 1
```

## PromQL Query Examples

### Basic Queries

```promql
# Current value
http_requests_total

# Filter by labels
http_requests_total{method="GET", status_code="200"}

# Regex matching
http_requests_total{route=~"/api/.*"}

# Negative matching
http_requests_total{status_code!="200"}

# Multiple conditions
http_requests_total{method="POST", status_code=~"5.."}
```

### Rate and Increase

```promql
# Requests per second
rate(http_requests_total[5m])

# Total increase over time
increase(http_requests_total[1h])

# Per-second rate with sum
sum(rate(http_requests_total[5m]))

# Rate by label
sum(rate(http_requests_total[5m])) by (status_code)
```

### Aggregation

```promql
# Sum across all instances
sum(http_requests_total)

# Average
avg(http_request_duration_seconds)

# Min/Max
min(http_request_duration_seconds)
max(http_request_duration_seconds)

# Count
count(up == 1)

# Group by labels
sum(http_requests_total) by (method, status_code)

# Without specific labels
sum(http_requests_total) without (instance)
```

### Mathematical Operations

```promql
# Error rate percentage
sum(rate(http_requests_total{status_code=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# Memory usage percentage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) /
node_memory_MemTotal_bytes * 100

# Disk usage percentage
(node_filesystem_size_bytes - node_filesystem_avail_bytes) /
node_filesystem_size_bytes * 100

# Request rate change
rate(http_requests_total[5m]) - rate(http_requests_total[5m] offset 1h)
```

### Time Functions

```promql
# Average over time
avg_over_time(cpu_usage[5m])

# Max over time
max_over_time(memory_usage[1h])

# Min over time
min_over_time(response_time[30m])

# Rate of change
deriv(cpu_usage[5m])

# Predict future value
predict_linear(disk_usage[1h], 3600)
```

### Advanced Queries

```promql
# Top 10 endpoints by request rate
topk(10, sum(rate(http_requests_total[5m])) by (route))

# Bottom 5 by response time
bottomk(5, avg(http_request_duration_seconds) by (route))

# Quantile across instances
quantile(0.95, http_request_duration_seconds)

# Histogram quantile
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# Absent metric (alerting)
absent(up{job="account-microservice"})

# Changes (count resets)
changes(process_start_time_seconds[1h])
```

## Grafana Dashboards

### Creating Dashboards

**Panel Configuration**:
```json
{
  "title": "Request Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total[5m])) by (service)",
      "legendFormat": "{{service}}",
      "refId": "A"
    }
  ],
  "type": "graph",
  "yaxes": [
    {
      "format": "reqps",
      "label": "Requests/sec"
    }
  ]
}
```

### Dashboard Variables

```json
{
  "templating": {
    "list": [
      {
        "name": "namespace",
        "type": "query",
        "query": "label_values(kube_pod_info, namespace)",
        "multi": true,
        "includeAll": true
      },
      {
        "name": "pod",
        "type": "query",
        "query": "label_values(kube_pod_info{namespace=\"$namespace\"}, pod)",
        "multi": true
      }
    ]
  }
}
```

### Common Dashboard Panels

#### 1. Request Rate
```promql
sum(rate(http_requests_total{namespace="$namespace"}[5m])) by (service)
```

#### 2. Error Rate
```promql
sum(rate(http_requests_total{namespace="$namespace", status_code=~"5.."}[5m])) /
sum(rate(http_requests_total{namespace="$namespace"}[5m])) * 100
```

#### 3. Response Time (p95)
```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{namespace="$namespace"}[5m])) by (le, service)
)
```

#### 4. CPU Usage
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="$namespace", pod=~"$pod"}[5m])) by (pod)
```

#### 5. Memory Usage
```promql
sum(container_memory_working_set_bytes{namespace="$namespace", pod=~"$pod"}) by (pod)
```

#### 6. Pod Count
```promql
count(kube_pod_info{namespace="$namespace"}) by (namespace)
```

## Recording Rules

**Purpose**: Pre-compute expensive queries

```yaml
groups:
  - name: application_rules
    interval: 30s
    rules:
      # Request rate by service
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job, service)
      
      # Error rate percentage
      - record: job:http_errors:rate5m
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (job) /
          sum(rate(http_requests_total[5m])) by (job) * 100
      
      # Average response time
      - record: job:http_request_duration:avg5m
        expr: |
          rate(http_request_duration_seconds_sum[5m]) /
          rate(http_request_duration_seconds_count[5m])
      
      # CPU usage by pod
      - record: pod:cpu_usage:rate5m
        expr: |
          sum(rate(container_cpu_usage_seconds_total[5m])) by (namespace, pod)
      
      # Memory usage by pod
      - record: pod:memory_usage:bytes
        expr: |
          sum(container_memory_working_set_bytes) by (namespace, pod)
```

## Best Practices

### 1. Metric Naming

Follow Prometheus naming conventions:

```
# Format: <namespace>_<name>_<unit>
http_requests_total
http_request_duration_seconds
database_connections_active
memory_usage_bytes

# Use base units
_seconds (not _milliseconds)
_bytes (not _megabytes)
_ratio (0-1, not percentage)
```

### 2. Label Usage

```javascript
// ✅ Good - Low cardinality labels
http_requests_total{method="GET", route="/api/accounts", status_code="200"}

// ❌ Bad - High cardinality (user_id changes frequently)
http_requests_total{user_id="12345"}

// ❌ Bad - Unbounded labels
http_requests_total{request_id="550e8400-e29b-41d4-a716-446655440000"}
```

### 3. Instrumentation

```javascript
// Instrument at application boundaries
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    
    httpRequestsTotal.inc({
      method: req.method,
      route: req.route?.path || 'unknown',
      status_code: res.statusCode
    });
    
    httpRequestDuration.observe({
      method: req.method,
      route: req.route?.path || 'unknown',
      status_code: res.statusCode
    }, duration);
  });
  
  next();
});
```

### 4. Alert on Symptoms

```yaml
# ✅ Good - Alert on user-facing issues
- alert: HighErrorRate
  expr: job:http_errors:rate5m > 5
  annotations:
    summary: "High error rate affecting users"

# ❌ Bad - Alert on internal metrics
- alert: HighCPU
  expr: cpu_usage > 80
  annotations:
    summary: "CPU usage high"
```

## Troubleshooting

### High Cardinality

**Problem**: Prometheus using too much memory

**Solutions**:
```bash
# Find high cardinality metrics
promtool tsdb analyze /prometheus/data

# Check series count
curl http://prometheus:9090/api/v1/status/tsdb

# Drop problematic metrics
- metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'high_cardinality_metric.*'
    action: drop
```

### Missing Metrics

**Problem**: Metrics not appearing

**Solutions**:
1. Check target status: `http://prometheus:9090/targets`
2. Verify ServiceMonitor: `kubectl get servicemonitor`
3. Check application `/metrics` endpoint
4. Review Prometheus logs

### Slow Queries

**Problem**: Grafana dashboards loading slowly

**Solutions**:
1. Use recording rules for expensive queries
2. Reduce time range
3. Add more specific label filters
4. Use `rate()` instead of `increase()` for large time ranges

## Related Documentation

- [Monitoring Overview](./index.md)
- [Logs Guide](./logs.md)
- [Alerting Configuration](./index.md#alerting)
- [Grafana Dashboards](https://grafana.omnivoltaic.com)