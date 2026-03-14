# Log Management Documentation

Comprehensive guide to logging infrastructure, best practices, and troubleshooting in the OVES ecosystem.

## Overview

Effective logging is crucial for debugging, monitoring, and understanding system behavior. The OVES logging infrastructure uses multiple tools to collect, aggregate, analyze, and visualize logs from all applications and infrastructure components.

## Logging Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Log Sources                                │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Kubernetes  │  │ Applications│  │   AWS       │             │
│  │   Pods      │  │   (stdout)  │  │  Services   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Log Collection                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Promtail   │  │  Fluentd    │  │ CloudWatch  │             │
│  │  (K8s logs) │  │ (App logs)  │  │   Agent     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Log Processing                                │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Loki     │  │  Logstash   │  │ CloudWatch  │             │
│  │  (Storage)  │  │ (Transform) │  │   Insights  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          │                 ▼                 │
          │         ┌─────────────┐           │
          │         │Elasticsearch│           │
          │         │  (Indexing) │           │
          │         └──────┬──────┘           │
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Visualization                                 │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Grafana   │  │   Kibana    │  │ CloudWatch  │             │
│  │   (Loki)    │  │    (ELK)    │  │  Dashboard  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Log Collection Systems

### 1. Loki + Promtail (Primary for Kubernetes)

**Purpose**: Lightweight, cost-effective log aggregation for Kubernetes workloads

#### How It Works

1. **Promtail** runs as a DaemonSet on every Kubernetes node
2. Automatically discovers all pods and containers
3. Tails log files from `/var/log/pods`
4. Enriches logs with Kubernetes metadata (namespace, pod, container)
5. Sends logs to Loki for storage

#### Promtail Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: monitoring
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0
    
    positions:
      filename: /tmp/positions.yaml
    
    clients:
      - url: http://loki:3100/loki/api/v1/push
    
    scrape_configs:
      # Kubernetes pod logs
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
          - role: pod
        
        relabel_configs:
          # Add namespace label
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          
          # Add pod name label
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          
          # Add container name label
          - source_labels: [__meta_kubernetes_pod_container_name]
            target_label: container
          
          # Add app label
          - source_labels: [__meta_kubernetes_pod_label_app]
            target_label: app
          
          # Add environment label
          - source_labels: [__meta_kubernetes_pod_label_environment]
            target_label: environment
```

#### Loki Configuration

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2023-01-01
      store: boltdb-shipper
      object_store: s3
      schema: v11
      index:
        prefix: loki_index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: s3
  
  aws:
    s3: s3://us-east-1/oves-loki-logs
    region: us-east-1

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20

chunk_store_config:
  max_look_back_period: 720h  # 30 days

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days
```

#### Querying Logs with LogQL

**Basic Queries**:
```logql
# View all logs from a specific app
{app="account-microservice"}

# Filter by namespace
{namespace="production"}

# Combine multiple labels
{namespace="production", app="account-microservice"}

# Search for specific text
{app="account-microservice"} |= "error"

# Case-insensitive search
{app="account-microservice"} |~ "(?i)error"

# Exclude specific text
{app="account-microservice"} != "health check"
```

**Advanced Queries**:
```logql
# Parse JSON logs
{app="account-microservice"} | json | level="error"

# Extract fields
{app="account-microservice"} | json | line_format "{{.timestamp}} {{.message}}"

# Count errors per minute
sum(rate({namespace="production"} |= "error" [1m])) by (app)

# Find slow queries (duration > 1 second)
{app="mongodb"} | json | duration > 1

# Top 10 error messages
topk(10, sum by (message) (rate({level="error"} [5m])))

# Calculate error rate percentage
sum(rate({level="error"} [5m])) / sum(rate({} [5m])) * 100
```

**Time-based Queries**:
```logql
# Last 5 minutes
{app="account-microservice"} [5m]

# Specific time range
{app="account-microservice"} [2024-01-01T00:00:00Z:2024-01-01T23:59:59Z]

# Rate of log entries
rate({app="account-microservice"} [5m])
```

### 2. ELK Stack (Elasticsearch, Logstash, Kibana)

**Purpose**: Advanced log analysis, full-text search, and complex aggregations

#### Logstash Pipeline

**Input Configuration**:
```ruby
input {
  # Beats input (from Filebeat)
  beats {
    port => 5044
  }
  
  # HTTP input (from applications)
  http {
    port => 8080
    codec => json
  }
  
  # Kafka input (for high-volume logs)
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["application-logs"]
    codec => json
  }
}
```

**Filter Configuration**:
```ruby
filter {
  # Parse JSON logs
  if [message] =~ /^\{.*\}$/ {
    json {
      source => "message"
    }
  }
  
  # Add timestamp
  date {
    match => ["timestamp", "ISO8601"]
    target => "@timestamp"
  }
  
  # Parse log level
  if [level] {
    mutate {
      uppercase => ["level"]
    }
  }
  
  # Extract request ID
  if [message] =~ /request_id/ {
    grok {
      match => { "message" => "request_id=%{UUID:request_id}" }
    }
  }
  
  # GeoIP lookup for IP addresses
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
    }
  }
  
  # Add environment tag
  mutate {
    add_field => {
      "environment" => "${ENVIRONMENT:development}"
    }
  }
  
  # Remove sensitive fields
  mutate {
    remove_field => ["password", "token", "api_key"]
  }
}
```

**Output Configuration**:
```ruby
output {
  # Send to Elasticsearch
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{[environment]}-%{+YYYY.MM.dd}"
    document_type => "_doc"
  }
  
  # Send critical errors to dead letter queue
  if [level] == "CRITICAL" {
    file {
      path => "/var/log/critical-errors.log"
      codec => json_lines
    }
  }
  
  # Debug output (optional)
  # stdout { codec => rubydebug }
}
```

#### Elasticsearch Index Templates

```json
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.lifecycle.name": "logs-policy",
    "index.lifecycle.rollover_alias": "logs"
  },
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" },
      "app": { "type": "keyword" },
      "namespace": { "type": "keyword" },
      "pod": { "type": "keyword" },
      "container": { "type": "keyword" },
      "request_id": { "type": "keyword" },
      "user_id": { "type": "keyword" },
      "duration": { "type": "float" },
      "status_code": { "type": "integer" },
      "client_ip": { "type": "ip" },
      "geoip": {
        "properties": {
          "location": { "type": "geo_point" }
        }
      }
    }
  }
}
```

#### Kibana Queries

**Basic Searches**:
```
# Find all errors
level:ERROR

# Search in specific field
message:"database connection failed"

# Wildcard search
app:*-microservice

# Range query
status_code:[400 TO 599]

# Boolean operators
level:ERROR AND app:account-microservice

# Exclude
level:ERROR NOT message:"expected error"
```

**Advanced Searches**:
```
# Regex search
message:/error.*database/

# Exists query
_exists_:request_id

# Missing field
NOT _exists_:user_id

# Date range
@timestamp:[now-1h TO now]

# Aggregation query
app:* | stats count() by level

# Complex query
(level:ERROR OR level:CRITICAL) AND 
namespace:production AND 
@timestamp:[now-1h TO now]
```

### 3. CloudWatch Logs

**Purpose**: AWS service logs and EC2 application logs

#### CloudWatch Agent Configuration

```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/application/*.log",
            "log_group_name": "/aws/ec2/application",
            "log_stream_name": "{instance_id}/{hostname}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S",
            "timezone": "UTC"
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/aws/ec2/nginx",
            "log_stream_name": "{instance_id}/access"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/aws/ec2/nginx",
            "log_stream_name": "{instance_id}/error"
          }
        ]
      }
    },
    "log_stream_name": "{instance_id}"
  }
}
```

#### CloudWatch Insights Queries

```sql
-- Find all errors in the last hour
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Count errors by application
fields @timestamp, application
| filter level = "ERROR"
| stats count() by application

-- Calculate average response time
fields @timestamp, duration
| filter ispresent(duration)
| stats avg(duration) as avg_duration by bin(5m)

-- Find slow queries
fields @timestamp, query, duration
| filter duration > 1000
| sort duration desc

-- Parse JSON logs
fields @timestamp, @message
| parse @message /(?<level>\w+)\s+(?<message>.*)/
| filter level = "ERROR"

-- Top 10 error messages
fields @message
| filter level = "ERROR"
| stats count() as error_count by @message
| sort error_count desc
| limit 10

-- Request rate per minute
fields @timestamp
| stats count() as request_count by bin(1m)

-- Error rate percentage
fields @timestamp, level
| stats count() as total, 
        sum(level = "ERROR") as errors
| fields errors / total * 100 as error_rate
```

## Log Formats and Standards

### Structured Logging (JSON)

**Recommended Format**:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "service": "account-microservice",
  "version": "1.2.3",
  "environment": "production",
  "message": "Failed to connect to database",
  "error": {
    "type": "MongoError",
    "message": "Connection timeout",
    "stack": "Error: Connection timeout\n    at..."
  },
  "context": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_123",
    "correlation_id": "abc-def-ghi",
    "method": "POST",
    "path": "/api/accounts",
    "duration_ms": 5432
  },
  "metadata": {
    "pod": "account-microservice-7d9f8b6c5-x4k2p",
    "namespace": "production",
    "node": "ip-10-0-1-45"
  }
}
```

### Log Levels

Use consistent log levels across all applications:

| Level | Usage | Examples |
|-------|-------|----------|
| **DEBUG** | Detailed diagnostic information | Variable values, function entry/exit |
| **INFO** | General informational messages | Service started, request completed |
| **WARN** | Warning messages for potentially harmful situations | Deprecated API usage, slow query |
| **ERROR** | Error events that might still allow the application to continue | Failed API call, validation error |
| **CRITICAL** | Severe error events that might cause the application to abort | Database unavailable, out of memory |

### Application Logging Best Practices

#### 1. Include Context

```javascript
// ✅ Good - Includes context
logger.info('User login successful', {
  user_id: user.id,
  email: user.email,
  ip_address: req.ip,
  user_agent: req.headers['user-agent'],
  request_id: req.id,
  duration_ms: Date.now() - startTime
});

// ❌ Bad - No context
logger.info('User logged in');
```

#### 2. Use Request IDs

```javascript
// Generate request ID at entry point
app.use((req, res, next) => {
  req.id = uuidv4();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// Include in all logs
logger.info('Processing payment', {
  request_id: req.id,
  amount: payment.amount
});
```

#### 3. Log Errors Properly

```javascript
// ✅ Good - Full error details
try {
  await processPayment(payment);
} catch (error) {
  logger.error('Payment processing failed', {
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
      code: error.code
    },
    payment_id: payment.id,
    amount: payment.amount,
    request_id: req.id
  });
  throw error;
}

// ❌ Bad - Lost error details
catch (error) {
  logger.error('Payment failed');
}
```

#### 4. Avoid Logging Sensitive Data

```javascript
// ✅ Good - Sensitive data masked
logger.info('Payment processed', {
  card_last4: payment.card.slice(-4),
  amount: payment.amount,
  currency: payment.currency
});

// ❌ Bad - Sensitive data exposed
logger.info('Payment processed', {
  card_number: payment.card,  // ❌ Never log full card numbers
  cvv: payment.cvv,           // ❌ Never log CVV
  password: user.password     // ❌ Never log passwords
});
```

## Log Retention Policies

| System | Retention Period | Storage Location | Backup |
|--------|------------------|------------------|--------|
| Loki | 30 days | EBS + S3 | Daily to S3 |
| Elasticsearch | 30 days | EBS | Weekly to S3 |
| CloudWatch | 90 days | CloudWatch | N/A |
| S3 Archive | 1 year | S3 Glacier | N/A |

## Log Analysis Examples

### Finding Performance Issues

```logql
# Loki: Find requests taking > 5 seconds
{app="account-microservice"} 
| json 
| duration_ms > 5000 
| line_format "{{.method}} {{.path}} took {{.duration_ms}}ms"
```

```sql
-- CloudWatch: Average response time by endpoint
fields @timestamp, path, duration
| stats avg(duration) as avg_duration by path
| sort avg_duration desc
```

### Tracking User Activity

```logql
# Loki: Track specific user's actions
{namespace="production"} 
| json 
| user_id="user_123" 
| line_format "{{.timestamp}} {{.action}} {{.resource}}"
```

### Debugging Errors

```logql
# Loki: Find all errors with stack traces
{app="account-microservice", level="ERROR"} 
| json 
| line_format "{{.message}}\n{{.error.stack}}"
```

### Monitoring API Usage

```sql
-- CloudWatch: API endpoint usage
fields @timestamp, method, path
| stats count() as requests by path
| sort requests desc
| limit 20
```

## Troubleshooting

### High Log Volume

**Problem**: Too many logs, high storage costs

**Solutions**:
1. Implement log sampling for high-volume endpoints
2. Reduce DEBUG logs in production
3. Use log levels appropriately
4. Implement log aggregation at application level

```javascript
// Example: Sample 10% of requests
if (Math.random() < 0.1 || req.path.includes('/critical/')) {
  logger.debug('Request details', { ... });
}
```

### Missing Logs

**Problem**: Logs not appearing in aggregation system

**Solutions**:
1. Check Promtail/Fluentd is running: `kubectl get pods -n monitoring`
2. Verify log format is correct (JSON preferred)
3. Check application is writing to stdout/stderr
4. Verify network connectivity to log aggregator
5. Check storage capacity

### Slow Log Queries

**Problem**: Queries taking too long

**Solutions**:
1. Add time range filters
2. Use indexed fields in queries
3. Avoid wildcard searches at beginning of strings
4. Use aggregations instead of returning all results
5. Consider using Elasticsearch for complex queries

## Related Documentation

- [Monitoring Overview](./index.md)
- [Metrics Guide](./metrics.md)
- [Alerting Setup](./index.md#alerting)
