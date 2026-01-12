# Monitoring & Observability Documentation

Comprehensive guide to OVES monitoring, logging, and alerting infrastructure.

## Overview

The OVES monitoring stack provides complete observability across all infrastructure and applications. We use industry-standard tools for metrics collection, log aggregation, alerting, and uptime monitoring, ensuring we can quickly detect, diagnose, and resolve issues.

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Sources                                 │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐             │
│  │ Kubernetes   │  │ Applications   │  │ AWS Services │             │
│  │ Clusters     │  │ (Microservices)│  │ (CloudWatch) │             │
│  └──────┬───────┘  └───────┬────────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Collection Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Prometheus   │  │    Loki      │  │  CloudWatch  │              │
│  │ (Metrics)    │  │   (Logs)     │  │  (AWS Logs)  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                     │
│         │                 │                 │                     │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐              │
│  │  Logstash    │  │ Elasticsearch│  │   CloudWatch │              │
│  │ (Processing) │  │  (Indexing)  │  │   Insights   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Visualization Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Grafana    │  │    Kibana    │  │  CloudWatch  │              │
│  │ (Dashboards) │  │ (Log Search) │  │  (Dashboards)│              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Alerting Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ AlertManager │  │    Uptime    │  │   Checkcle   │              │
│  │              │  │     Kuma     │  │              │              │
│  └──────┬───────┘  └──────┬───────┘  └───────┬──────┘              │
│         │                 │                  │                     │
│         └─────────────────┴──────────────────┘                     │
│                           │                                        │
│                           ▼                                        │
│                  ┌──────────────────┐                               │
│                  │ Microsoft Teams  │                               │
│                  │    (Alerts)      │                               │
│                  └──────────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Monitoring Stack Components

### 1. Metrics Collection (Prometheus)

**Purpose**: Time-series metrics collection and storage

**What It Monitors**:
- Kubernetes cluster metrics (nodes, pods, containers)
- Application metrics (request rates, latency, errors)
- Database metrics (connections, queries, performance)
- Infrastructure metrics (CPU, memory, disk, network)
- Custom business metrics

**Architecture**:
- **Prometheus Server**: Central metrics collection and storage
- **Node Exporter**: Host-level metrics (CPU, memory, disk)
- **kube-state-metrics**: Kubernetes object state metrics
- **Service Monitors**: Automatic service discovery and scraping
- **Pushgateway**: For short-lived jobs and batch processes

**Deployment**:
```yaml
# Deployed in dev cluster
namespace: monitoring
replicas: 2 (HA setup)
retention: 15 days
storage: 100GB EBS volume
scrape_interval: 30s
```

**Key Metrics Collected**:
- **Infrastructure**: `node_cpu_seconds_total`, `node_memory_bytes`, `node_disk_io_time_seconds_total`
- **Kubernetes**: `kube_pod_status_phase`, `kube_deployment_status_replicas`, `kube_node_status_condition`
- **Applications**: `http_requests_total`, `http_request_duration_seconds`, `http_requests_errors_total`
- **Databases**: `mongodb_connections`, `redis_connected_clients`, `postgres_up`

**Example ServiceMonitor**:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: account-microservice
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: account-microservice
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 2. Visualization (Grafana)

**Purpose**: Metrics visualization and dashboarding

**Features**:
- Real-time dashboards
- Custom visualizations
- Alerting rules
- Multi-data source support (Prometheus, Loki, Elasticsearch, CloudWatch)
- Team collaboration
- Dashboard templating

**Access**:
- Dev: `https://grafana-dev.omnivoltaic.com`
- Prod: `https://grafana.omnivoltaic.com`

**Pre-built Dashboards**:

1. **Cluster Overview**
   - Node status and resource usage
   - Pod distribution
   - Network traffic
   - Storage utilization

2. **Application Performance**
   - Request rate (RPS)
   - Response time (p50, p95, p99)
   - Error rate
   - Active connections

3. **Database Performance**
   - Query performance
   - Connection pool status
   - Cache hit rates
   - Replication lag

4. **Infrastructure Health**
   - CPU, Memory, Disk usage
   - Network I/O
   - Load averages
   - System errors

5. **Business Metrics**
   - User registrations
   - Transaction volumes
   - API usage by endpoint
   - Payment processing

**Dashboard Example**:
```json
{
  "dashboard": {
    "title": "Account Microservice",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{service='account-microservice'}[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service='account-microservice'}[5m]))"
          }
        ]
      }
    ]
  }
}
```

### 3. Log Aggregation

We use multiple log aggregation systems for different purposes:

#### Loki (Primary for Kubernetes)

**Purpose**: Kubernetes log aggregation and querying

**Features**:
- Label-based log indexing (like Prometheus for logs)
- Efficient storage (only indexes metadata)
- Native Grafana integration
- LogQL query language
- Multi-tenancy support

**Deployment**:
```yaml
namespace: monitoring
replicas: 3 (HA setup)
retention: 30 days
storage: 200GB EBS volume
```

**Log Collection**:
- **Promtail**: Deployed as DaemonSet on all nodes
- Automatically discovers and tails pod logs
- Enriches logs with Kubernetes metadata

**Example Query**:
```logql
# Find errors in account microservice
{namespace="production", app="account-microservice"} |= "error" | json

# Count errors per minute
sum(rate({namespace="production"} |= "error" [1m])) by (app)

# Find slow queries
{app="mongodb"} | json | duration > 1s
```

#### Elasticsearch + Logstash + Kibana (ELK Stack)

**Purpose**: Advanced log analysis and full-text search

**Components**:

1. **Logstash**: Log processing and transformation
   - Parses structured logs (JSON)
   - Enriches with additional metadata
   - Filters and transforms data
   - Sends to Elasticsearch

2. **Elasticsearch**: Log storage and indexing
   - Full-text search capabilities
   - Aggregations and analytics
   - Scalable distributed storage
   - 30-day retention

3. **Kibana**: Log exploration and visualization
   - Interactive log search
   - Custom visualizations
   - Saved searches and dashboards
   - Alerting on log patterns

**Deployment**:
```yaml
# All deployed in dev cluster
namespace: logging

elasticsearch:
  replicas: 3
  storage: 500GB EBS volume
  heap_size: 4GB

logstash:
  replicas: 2
  heap_size: 2GB

kibana:
  replicas: 2
```

**Access**:
- Kibana: `https://kibana-dev.omnivoltaic.com`

**Use Cases**:
- Complex log queries and aggregations
- Historical log analysis
- Compliance and audit logging
- Security event investigation

#### CloudWatch Logs

**Purpose**: AWS service logs and CloudWatch integration

**What It Collects**:
- EKS control plane logs
- Lambda function logs
- RDS database logs
- VPC Flow Logs
- CloudTrail audit logs
- Application logs from EC2 instances

**Features**:
- Native AWS integration
- Log Insights for querying
- Automatic retention management
- Metric filters for alerting

**Example Query**:
```sql
# CloudWatch Insights query
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

### 4. Alerting (AlertManager)

**Purpose**: Alert routing, grouping, and notification management

**Features**:
- Alert deduplication
- Alert grouping
- Silencing and inhibition
- Multi-channel notifications
- Alert routing based on labels

**Deployment**:
```yaml
namespace: monitoring
replicas: 3 (HA setup)
```

**Alert Channels**:
1. **Microsoft Teams** (Primary)
   - Critical alerts
   - Service degradation
   - Infrastructure issues

2. **Email**
   - Non-critical alerts
   - Daily summaries
   - Weekly reports

3. **PagerDuty** (On-call)
   - Production incidents
   - Service outages
   - Critical errors

**Alert Configuration**:
```yaml
route:
  receiver: 'teams-default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
  - match:
      severity: critical
    receiver: 'teams-critical'
    continue: true
  - match:
      severity: critical
      environment: production
    receiver: 'pagerduty'

receivers:
- name: 'teams-default'
  webhook_configs:
  - url: 'https://outlook.office.com/webhook/...'
    send_resolved: true

- name: 'teams-critical'
  webhook_configs:
  - url: 'https://outlook.office.com/webhook/.../critical'
    send_resolved: true

- name: 'pagerduty'
  pagerduty_configs:
  - service_key: '<pagerduty-key>'
```

**Common Alerts**:

1. **High CPU Usage**
```yaml
- alert: HighCPUUsage
  expr: node_cpu_seconds_total{mode="idle"} < 20
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High CPU usage on {{ $labels.instance }}"
    description: "CPU usage is above 80% for 5 minutes"
```

2. **Pod CrashLooping**
```yaml
- alert: PodCrashLooping
  expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Pod {{ $labels.pod }} is crash looping"
    description: "Pod has restarted {{ $value }} times in the last 15 minutes"
```

3. **High Error Rate**
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate in {{ $labels.service }}"
    description: "Error rate is {{ $value | humanizePercentage }}"
```

4. **Database Connection Issues**
```yaml
- alert: DatabaseConnectionPoolExhausted
  expr: mongodb_connections_current / mongodb_connections_available > 0.9
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Database connection pool nearly exhausted"
    description: "{{ $labels.database }} is using {{ $value | humanizePercentage }} of available connections"
```

### 5. Uptime Monitoring

#### Uptime Kuma

**Purpose**: Service availability monitoring and status pages

**Features**:
- HTTP/HTTPS monitoring
- TCP port monitoring
- Ping monitoring
- Keyword monitoring
- SSL certificate expiry monitoring
- Status pages for stakeholders

**Deployment**:
```yaml
namespace: monitoring
replicas: 1
storage: 10GB EBS volume
```

**Access**: `https://uptime.omnivoltaic.com`

**Monitored Services**:
- All public APIs
- Web applications
- Database endpoints
- Third-party integrations
- DNS resolution

**Check Intervals**:
- Critical services: 1 minute
- Standard services: 5 minutes
- Internal services: 10 minutes

#### Checkly

**Purpose**: Synthetic monitoring and API testing

**Features**:
- Multi-region checks
- API endpoint monitoring
- Browser-based checks
- Performance monitoring
- Alerting on failures

**Monitored Endpoints**:
- GraphQL APIs
- REST APIs
- Authentication flows
- Payment processing
- Critical user journeys

**Check Locations**:
- US East (Virginia)
- US West (California)
- EU (Frankfurt)
- Asia (Singapore)

### 6. Cloud Monitoring (CloudWatch)

**Purpose**: AWS-native monitoring and alerting

**What It Monitors**:
- EC2 instance metrics
- EKS cluster metrics
- RDS database metrics
- Load balancer metrics
- S3 bucket metrics
- Lambda function metrics

**Key Metrics**:
- CPU utilization
- Network in/out
- Disk read/write
- Status checks
- Request counts
- Error rates

**CloudWatch Alarms**:
- EC2 instance health
- RDS storage space
- Load balancer unhealthy targets
- Lambda errors and throttling
- Billing alerts

## Monitoring Best Practices

### 1. Metrics

- **Use Labels Wisely**: Don't create high-cardinality labels
- **Instrument Everything**: Add metrics to all services
- **Follow Naming Conventions**: Use standard Prometheus naming
- **Set Appropriate Retention**: Balance storage cost vs. historical data needs
- **Use Recording Rules**: Pre-compute expensive queries

### 2. Logging

- **Structured Logging**: Use JSON format for logs
- **Include Context**: Add request IDs, user IDs, trace IDs
- **Log Levels**: Use appropriate levels (DEBUG, INFO, WARN, ERROR)
- **Avoid Sensitive Data**: Never log passwords, tokens, PII
- **Sampling**: Sample high-volume logs to reduce costs

### 3. Alerting

- **Alert on Symptoms, Not Causes**: Alert on user-facing issues
- **Reduce Noise**: Avoid alert fatigue with proper thresholds
- **Actionable Alerts**: Every alert should require action
- **Runbooks**: Link alerts to troubleshooting guides
- **Test Alerts**: Regularly test alert delivery

### 4. Dashboards

- **Start with Overview**: High-level health dashboard
- **Drill-Down Capability**: Link to detailed dashboards
- **Use Templates**: Create reusable dashboard templates
- **Keep It Simple**: Don't overcrowd dashboards
- **Document**: Add descriptions to panels

## Accessing Monitoring Tools

### Development Environment

- **Grafana**: `https://grafana-dev.omnivoltaic.com`
- **Prometheus**: `https://prometheus-dev.omnivoltaic.com`
- **Kibana**: `https://kibana-dev.omnivoltaic.com`
- **AlertManager**: `https://alertmanager-dev.omnivoltaic.com`

### Production Environment

- **Grafana**: `https://grafana.omnivoltaic.com`
- **Uptime Kuma**: `https://uptime.omnivoltaic.com`
- **CloudWatch**: AWS Console → CloudWatch

### Authentication

- **SSO**: All tools integrated with company SSO
- **RBAC**: Role-based access control
- **API Keys**: Available for automation

## Troubleshooting

### High Cardinality Issues

**Symptom**: Prometheus running out of memory

**Solutions**:
1. Identify high-cardinality metrics: `promtool tsdb analyze /prometheus/data`
2. Remove or aggregate problematic labels
3. Use recording rules to pre-aggregate
4. Increase Prometheus memory allocation

### Missing Metrics

**Symptom**: Metrics not appearing in Grafana

**Solutions**:
1. Check ServiceMonitor configuration: `kubectl get servicemonitor`
2. Verify Prometheus targets: `https://prometheus/targets`
3. Check application metrics endpoint: `curl http://service:port/metrics`
4. Review Prometheus logs for scrape errors

### Log Ingestion Issues

**Symptom**: Logs not appearing in Loki/Elasticsearch

**Solutions**:
1. Check Promtail/Logstash status: `kubectl get pods -n monitoring`
2. Verify log format is correct (JSON preferred)
3. Check storage capacity
4. Review ingestion rate limits

### Alert Not Firing

**Symptom**: Expected alert not triggering

**Solutions**:
1. Check alert rule syntax in Prometheus
2. Verify AlertManager configuration
3. Test alert expression in Prometheus UI
4. Check AlertManager routing rules
5. Verify webhook/notification channel configuration

)
