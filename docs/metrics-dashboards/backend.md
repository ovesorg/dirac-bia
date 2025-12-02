# Backend

## InfluxDB v2

### Architecture Overview

**InfluxDB 2.x** serves as the primary time-series database for metrics storage and retrieval.

**Key capabilities**:
- Native time-series operations via Flux query language
- Tag-based filtering (fleet_id, station_id, vehicle_id)
- Built-in aggregation functions (mean, min, max, sum, count)
- RFC3339 and relative time ranges (e.g., `-24h`)

### Connection

Required environment variables:
- `INFLUX_URL`: Database endpoint
- `INFLUX_TOKEN`: Authentication token
- `INFLUX_ORG`: Organization identifier

## Metric Core Module

### Design Principles

Minimal abstraction layer over InfluxDB client:
- Standardizes time-window queries
- Caps max points for UI performance
- Returns chart-friendly shape `{ t, v }[]`
- Maintains type stability for frontend contract
- No external data processing libraries

---

## 1. Folder layout

You can drop this into your backend (Node/TS) project:

```text
src/
  metrics-core/
    influxClient.ts
    types.ts
    timeSeries.ts
  server/
    routes/
      metrics.ts    // (optional example usage)
```

---

## 2. `influxClient.ts` – single Influx entry point

```ts
// src/metrics-core/influxClient.ts
import { InfluxDB } from '@influxdata/influxdb-client'

const INFLUX_URL = process.env.INFLUX_URL!
const INFLUX_TOKEN = process.env.INFLUX_TOKEN!
const INFLUX_ORG = process.env.INFLUX_ORG!

if (!INFLUX_URL || !INFLUX_TOKEN || !INFLUX_ORG) {
  throw new Error('INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG env vars are required')
}

const influx = new InfluxDB({ url: INFLUX_URL, token: INFLUX_TOKEN })

export const queryApi = influx.getQueryApi(INFLUX_ORG)
```

---

## 3. `types.ts` – shared types

```ts
// src/metrics-core/types.ts

/** Time range for the query. Use RFC3339 or Flux relative times (e.g. -24h). */
export interface TimeRange {
  start: string   // "2025-12-02T00:00:00Z" or "-24h"
  stop?: string   // optional, e.g. "now()"
}

/** A single point ready for plotting on the frontend. */
export interface SeriesPoint {
  t: number     // timestamp, ms since epoch
  v: number     // value
  tags?: Record<string, string> // optional tag info, e.g. station_id, fleet_id
}

/** Basic query for a single time series. */
export interface TimeSeriesQuery {
  bucket: string
  measurement: string
  field: string
  tags?: Record<string, string>   // { fleet_id: 'F123', station_id: 'S01' }
  range: TimeRange
  maxPoints?: number              // optional hard cap for UI, e.g. 300
  aggregateEvery?: string         // optional Flux duration for aggregateWindow, e.g. "5m"
  aggregateFn?: 'mean' | 'min' | 'max' | 'sum' | 'count'
}

/** Result wrapper with optional metadata for debugging and optimization. */
export interface TimeSeriesResult {
  points: SeriesPoint[]
  metadata?: {
    count: number
    timeRange?: {
      start?: number
      end?: number
    }
  }
}
```

---

## 4. `timeSeries.ts` – minimalist query helper

This is the core: it builds a Flux query for a single metric, applies **time window**, optional **aggregation**, and **point cap**, then returns `{ t, v }[]`.

```ts
// src/metrics-core/timeSeries.ts
import { queryApi } from './influxClient'
import {
  TimeSeriesQuery,
  TimeSeriesResult,
  SeriesPoint,
} from './types'

/**
 * Build a Flux filter clause for tags like { fleet_id: "F123", station_id: "S01" }.
 */
function buildTagFilter(tags?: Record<string, string>): string {
  if (!tags || Object.keys(tags).length === 0) return ''
  const conditions = Object.entries(tags).map(
    ([key, value]) => {
      // Sanitize tag values to prevent Flux injection
      const sanitized = value.replace(/"/g, '\\"')
      return `r.${key} == "${sanitized}"`
    }
  )
  return `|> filter(fn: (r) => ${conditions.join(' and ')})`
}

/**
 * Minimal time-series query helper:
 * - applies time window (range)
 * - filters by measurement, field, tags
 * - optional aggregateWindow
 * - optional hard point cap via limit()
 * - returns [{ t, v, tags? }]
 */
export async function getTimeSeries(
  q: TimeSeriesQuery
): Promise<TimeSeriesResult> {
  const { bucket, measurement, field, tags, range } = q
  const maxPoints = q.maxPoints ?? 0
  const aggregateEvery = q.aggregateEvery
  const aggregateFn = q.aggregateFn ?? 'mean'

  const start = range.start
  const stop = range.stop ?? 'now()'

  const tagFilter = buildTagFilter(tags)

  const aggregateClause = aggregateEvery
    ? `|> aggregateWindow(every: ${aggregateEvery}, fn: ${aggregateFn}, createEmpty: false)`
    : ''

  // Simple hard cap for UI – we do not try to be clever here.
  const limitClause = maxPoints > 0 ? `|> limit(n: ${maxPoints})` : ''

  const flux = `
    from(bucket: "${bucket}")
      |> range(start: ${start}, stop: ${stop})
      |> filter(fn: (r) => r._measurement == "${measurement}")
      |> filter(fn: (r) => r._field == "${field}")
      ${tagFilter}
      |> sort(columns: ["_time"])
      ${aggregateClause}
      ${limitClause}
  `

  const rows: any[] = []

  return new Promise<TimeSeriesResult>((resolve, reject) => {
    queryApi.queryRows(flux, {
      next(row, tableMeta) {
        const o = tableMeta.toObject(row)
        rows.push(o)
      },
      error(err) {
        reject(err)
      },
      complete() {
        const points: SeriesPoint[] = rows.map((r) => ({
          t: new Date(r._time).getTime(),
          v: Number(r._value),
          tags: {
            ...(r.fleet_id ? { fleet_id: String(r.fleet_id) } : {}),
            ...(r.station_id ? { station_id: String(r.station_id) } : {}),
            ...(r.vehicle_id ? { vehicle_id: String(r.vehicle_id) } : {}),
          },
        }))

        // Include metadata for frontend debugging/optimization
        resolve({ 
          points,
          metadata: {
            count: points.length,
            timeRange: {
              start: points[0]?.t,
              end: points[points.length - 1]?.t
            }
          }
        })
      },
    })
  })
}
```

### Notes on design (intentionally simple)

* **No `sample()` here** – just `limit()`.

  * For a *minimal* version, you can control volume using:

    * `aggregateEvery` (time bucketing)
    * `maxPoints` (limit)
  * If later you want more aggressive reduction, you can add `|> sample(n: ...)` inside this function without touching any frontend code.

* **`aggregateEvery` is optional**:

  * If **absent** → you get raw points (capped by `maxPoints` if set).
  * If **present** → use `aggregateWindow` with `mean` (or any other fn).

This keeps the logic easy for the devs: they supply either just `maxPoints` or both `aggregateEvery + maxPoints` if needed.

---

## 5. Example usage in an API route (Express-style)

Here’s how your HTTP API could expose this to React:

```ts
// src/server/routes/metrics.ts
import express from 'express'
import { getTimeSeries } from '../../metrics-core/timeSeries'

const router = express.Router()

router.get('/time-series', async (req, res) => {
  try {
    const {
      bucket = 'telemetry',
      measurement,
      field,
      start,
      stop,
      maxPoints,
      fleetId,
      stationId,
    } = req.query as Record<string, string>

    if (!measurement || !field || !start) {
      return res.status(400).json({ error: 'measurement, field, start are required' })
    }

    const tags: Record<string, string> = {}
    if (fleetId) tags.fleet_id = fleetId
    if (stationId) tags.station_id = stationId

    // Simple heuristic: if range is long, aggregate; if short, don’t.
    // (Minimal, you can refine later.)
    const range: { start: string; stop?: string } = {
      start,
      stop: stop ?? 'now()',
    }

    const q = {
      bucket,
      measurement,
      field,
      tags,
      range,
      maxPoints: maxPoints ? Number(maxPoints) : 300,
      // you can choose to always aggregate for long ranges on the client side
      // or leave aggregateEvery undefined and rely on limit() only.
    }

    const result = await getTimeSeries(q)
    return res.json(result)
  } catch (err: any) {
    console.error('metrics /time-series error', err)
    return res.status(500).json({ error: 'Internal server error' })
  }
})

export default router
```

Frontend call (e.g. in your React dashboard):

```ts
// example React data fetch
const resp = await fetch(
  `/api/metrics/time-series?bucket=telemetry` +
  `&measurement=battery_soc&field=soc` +
  `&start=-24h&maxPoints=300&fleetId=F123`
)

const { points } = await resp.json()
// points: [{ t: 1733145600000, v: 78.2, tags: {...} }, ...]
```

Then your Mosaic/TailwindPlus chart components just use:

* `x = new Date(point.t)`
* `y = point.v`

---

## 6. How to evolve this later (without breaking the frontend)

When you want more sophistication, you can **only touch `getTimeSeries`** and keep the type `TimeSeriesResult` the same:

* add `sample(n:)` before `limit()`
* dynamically choose `aggregateEvery` based on range length
* calculate and add basic stats (`min`, `max`, `avg`) into `TimeSeriesResult`
* enforce per-user tag filters based on auth (e.g. restrict `fleet_id`)

Frontend won’t need any change as long as `points: SeriesPoint[]` stays stable.

## Security Considerations

1. **Tag Injection**: Tag values are sanitized to prevent Flux injection attacks
2. **Point Capping**: `maxPoints` enforces UI performance limits (default: 300)
3. **Auth Filtering**: Future enhancement to restrict queries by user permissions (e.g., fleet-level access control)

## Performance Guidelines

**Query optimization**:
- Use `aggregateEvery` for time ranges > 24h to reduce point count
- Set `maxPoints` based on chart resolution needs (typically 200-500 points)
- Apply tag filters to reduce scan scope

**Typical configurations**:
- Real-time (last 1h): raw data, `maxPoints: 300`
- Daily view (24h): `aggregateEvery: "5m"`, `maxPoints: 288`
- Weekly view (7d): `aggregateEvery: "30m"`, `maxPoints: 336`

## Extension Points

**Additional functions to implement**:

1. **`getTopN()`**: Leaderboards (e.g., "Top 10 stations by energy in last 24h")
2. **`getAggregates()`**: Summary statistics (min, max, mean, p95) for KPI cards
3. **`getMultiSeries()`**: Multiple metrics in single query for correlation analysis
4. **`getRealtime()`**: Streaming updates via WebSocket for live dashboards

