# Frontend

## TailwindPlus Theme Systems

### Design Philosophy

Dashboards are **standard pages** within TailwindPlus design system, not separate frameworks.

**Core approach**:
- Leverage TailwindPlus layout primitives (grids, cards, sections)
- Drop chart libraries into TailwindPlus containers
- Maintain theme consistency across marketing, docs, and operational dashboards
- Build reusable metric card patterns

---

## 1. Dashboard Layout Structure

Think of dashboards as **just another page type** in your TailwindPlus design system:

1. **Create a “Dashboard Layout” wrapper**:

   * Top bar: title, date range control, user menu.
   * Left side: nav / filters / entity picker (Fleet, Station, Rider).
   * Main content: responsive grid of cards.
   * Use a **2–3 column grid** that collapses nicely on mobile.

   In code, you want something like:

   ```tsx
   // app/dashboard/layout.tsx
   export function DashboardLayout({ children }) {
     return (
       <div className="min-h-screen flex flex-col">
         <header className="border-b px-4 py-2 flex items-center justify-between">
           <h1 className="text-lg font-semibold">OVES Fleet Dashboard</h1>
           {/* Date range picker, etc. */}
         </header>
         <main className="flex-1 px-4 py-4">
           <div className="grid gap-4 lg:grid-cols-3 md:grid-cols-2 grid-cols-1">
             {children}
           </div>
         </main>
       </div>
     )
   }
   ```

2. **Define a “Metric Card” pattern** in TailwindPlus:

   * Card header (title, subtitle).
   * Value + delta (e.g. “132 kWh / +12%”).
   * Small chart (sparkline, bar, line).
   * Footer (last updated, link to detail).

   Once you have *one* really good metric card, you can reuse it across:

   * Station overview
   * Fleet overview
   * Battery health

3. **Start with 3–4 “hero” metrics**:

   * Total energy delivered today
   * Number of active vehicles / swaps
   * Station utilization
   * PV vs load (if relevant)

   Hook those up to your new `/api/metrics/time-series` endpoint first.

So: **start by building one dashboard page + one reusable metric-card component** using TailwindPlus blocks, then repeat.

---

## 6. Error Handling & Loading States

Production dashboards require:

### Loading States

```tsx
function MetricCard({ title, isLoading, error, children }) {
  return (
    <div className="rounded-xl border bg-background p-4 shadow-sm">
      <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
      {isLoading && <div className="animate-pulse h-32 bg-muted rounded mt-2" />}
      {error && <div className="text-sm text-destructive mt-2">Failed to load data</div>}
      {!isLoading && !error && children}
    </div>
  )
}
```

### Error Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary'

function DashboardPage() {
  return (
    <ErrorBoundary fallback={<div>Dashboard failed to load</div>}>
      <DashboardLayout>
        {/* metric cards */}
      </DashboardLayout>
    </ErrorBoundary>
  )
}
```

### Retry Logic

```tsx
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['metrics', measurement, field],
  queryFn: () => fetchTimeSeries({ measurement, field }),
  retry: 2,
  staleTime: 30000, // 30s cache
})
```

---

## 7. Responsive Design Patterns

**Grid breakpoints**:
```tsx
// Desktop: 3 columns, Tablet: 2 columns, Mobile: 1 column
<div className="grid gap-4 xl:grid-cols-3 lg:grid-cols-2 grid-cols-1">
```

**Chart responsiveness**:
- Use `ResponsiveContainer` (Recharts) for fluid width/height
- Hide axis labels on mobile: `<XAxis hide={isMobile} />`
- Reduce data points on small screens: `maxPoints: isMobile ? 100 : 300`

**Mobile-first controls**:
- Collapsible filter panel: visible by default on desktop, drawer on mobile
- Touch-friendly date range picker with preset buttons (Today, 7d, 30d)

---

## 2. Frontend packages I’d actually recommend

You don’t need a “dashboard framework”. You need:

1. A **charting library** that plays nice with React + Tailwind.
2. A **table** library for drill-downs.
3. Optional: form/date controls.

### 2.1 Chart library: pick one of these

All of these work fine with Tailwind themes because they don’t enforce heavy styling:

#### 🔹 Recharts

* Declarative, very React-y, easy mental model.
* Good for standard IoT charts: line, bar, area, scatter, radial.
* Quick to get something decent-looking, you style container with Tailwind.

Usage pattern:

```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

function MetricChart({ data }: { data: { t: number; v: number }[] }) {
  const formatted = data.map(p => ({ x: p.t, y: p.v }))

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formatted}>
          <XAxis dataKey="x" tickFormatter={t => new Date(t).toLocaleTimeString()} />
          <YAxis />
          <Tooltip labelFormatter={t => new Date(t).toLocaleString()} />
          <Line type="monotone" dataKey="y" stroke="currentColor" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

TailwindPlus handles the card + typography; Recharts just paints inside.

#### 🔹 Tremor (if you want more “premade dashboard-y” charts)

Tremor is a React + Tailwind dashboard kit (basically Tailwind-friendly chart + card components). It can save your team time making things look “productized” from day one.

* Ships with **cards, metric displays, filters, and charts**.
* Designed for Tailwind, so TailwindPlus theming fits naturally.

If your devs want a “batteries included” feel, Tremor + TailwindPlus is a good combo.

#### 🔹 ECharts / Nivo / Visx

These are more powerful but also heavier / more complex; I’d only go there if you hit Recharts’ limits.

**My vote for OVES right now:**

* Start with **Recharts** for line/bar/area + one “metric card”.
* Add **Tremor** later if you want more polished “out-of-the-box” dashboard components.

---

## 3. Tables & drill-downs

Dashboards without tables quickly get frustrating for operations teams.

I’d add:

### 🔹 TanStack Table (React Table)

* Headless table engine.
* You build the look with TailwindPlus.
* Perfect for:

  * “Top 20 stations (last 24h)”
  * “List of recent swaps”
  * “Battery health list”

Pattern:

* Call `/api/metrics/top-n` (we can define this later).
* Feed results to TanStack Table.
* Use TailwindPlus table styles for rows/hover/pills.

---

## 4. Where TailwindPlus actually helps

TailwindPlus gives you:

* Consistent **layout primitives**: grids, sections, cards, shells.
* Prebuilt **UI patterns**: navigation, filters, tabbed panels, etc.
* Theme consistency across:

  * Marketing pages
  * Documentation
  * Operational dashboards

So don’t look for “TailwindPlus-specific dashboards”; instead:
**Use TailwindPlus blocks to build your layout and wrappers, then drop Recharts (or Tremor) components inside those blocks.**

Concretely:

1. Pick a **“2-column app layout”** block from TailwindPlus for the dashboard shell.
2. Use a **“stats card”** block for your metric cards.
3. Inside each stats card, mount a Recharts/Tremor chart using `points` from `metrics-core`.

---

## 5. Suggested “first implementation path” for your team

To make this actionable:

1. **Implement `/api/metrics/time-series`** using the minimal metrics-core we sketched.
2. In your React app:

   * Create `DashboardLayout` using TailwindPlus blocks.
   * Create `MetricCard` component:

     ```tsx
     function MetricCard({ title, metric, children }) {
       return (
         <div className="rounded-xl border bg-background p-4 shadow-sm flex flex-col gap-2">
           <div className="flex items-center justify-between">
             <div>
               <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
               <p className="text-lg font-semibold">{metric}</p>
             </div>
           </div>
           {children /* chart, bar, whatever */}
         </div>
       )
     }
     ```
3. Add one chart card:

   * Fetch `/api/metrics/time-series?measurement=battery_soc&field=soc&start=-24h&maxPoints=300`.
   * Feed to a small `MetricChart` with Recharts.
4. Once that’s working:

   * Clone metric cards for 3–4 main KPIs.
   * Add one table using TanStack Table for detail.

You’ll already have a **real, on-brand dashboard** that:

* Uses TailwindPlus for look & feel.
* Uses metrics-core for safe, capped Influx queries.
* Uses a mainstream charting library (Recharts) so it's familiar to new hires.

---

## Implementation Checklist

**Phase 1: Foundation**
- [ ] Set up DashboardLayout with TailwindPlus blocks
- [ ] Create reusable MetricCard component
- [ ] Wire one metric to `/api/metrics/time-series`
- [ ] Add loading and error states

**Phase 2: Core Metrics**
- [ ] Implement 3-4 hero KPI cards
- [ ] Add one chart using Recharts
- [ ] Test responsive behavior on mobile

**Phase 3: Drill-down**
- [ ] Add TanStack Table for detail views
- [ ] Implement date range controls
- [ ] Add entity filters (Fleet, Station)

**Phase 4: Polish**
- [ ] Add error boundaries
- [ ] Implement retry logic
- [ ] Optimize for mobile (collapsible filters, reduced data points)
- [ ] Add "last updated" timestamps

---

## Technology Recommendations

**Required**:
- **Recharts**: Primary charting library (declarative, React-friendly, Tailwind-compatible)
- **TanStack Table**: Headless table for drill-downs
- **TanStack Query** (React Query): Data fetching with caching and retry logic

**Optional**:
- **Tremor**: Prebuilt dashboard components (if team wants faster UI development)
- **date-fns**: Date manipulation for time range controls
- **react-error-boundary**: Graceful error handling

**Avoid**:
- Heavy dashboard frameworks (AdminLTE, CoreUI) - conflicts with TailwindPlus
- Chart libraries with opinionated styling (Chart.js with default themes)

---

If you specify a chart library preference (Recharts vs Tremor) or identify a specific dashboard use case (Fleet Overview, Station Health), concrete implementation examples can be provided.
