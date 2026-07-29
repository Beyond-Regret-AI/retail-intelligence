import { createBrowserRouter, Navigate, NavLink, Outlet, RouterProvider, useNavigate, useParams } from 'react-router';
import type { ReactNode } from 'react';
import { useState } from 'react';
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Skeleton,
  useAnalyticsQuery,
} from '@databricks/appkit-ui/react';
import { sql } from '@databricks/appkit-ui/js';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Database,
  Phone,
  ShieldCheck,
  Sparkles,
  Target,
  UserRound,
  type LucideIcon,
} from 'lucide-react';

type Row = Record<string, unknown>;
type QueryKey =
  | 'customers_requiring_action'
  | 'customer_action'
  | 'customer_campaigns'
  | 'customer_prediction'
  | 'customer_profile'
  | 'customer_support'
  | 'customer_transactions'
  | 'data_quality_status'
  | 'executive_metrics'
  | 'high_risk_by_segment'
  | 'layer_record_counts'
  | 'operations_status'
  | 'risk_distribution'
  | 'top_churn_drivers';
type CustomerQueryKey =
  | 'customer_action'
  | 'customer_campaigns'
  | 'customer_prediction'
  | 'customer_profile'
  | 'customer_support'
  | 'customer_transactions';
type NoParamQueryKey = Exclude<QueryKey, CustomerQueryKey>;
type MiniQueryResult = {
  data?: unknown[] | null;
  loading: boolean;
  error?: unknown;
};

const demoCustomerId = 'CUST-0007';

function numberValue(value: unknown): number {
  return Number(value ?? 0);
}

function textValue(value: unknown): string {
  return String(value ?? '');
}

function formatSek(value: unknown): string {
  return `SEK ${numberValue(value).toLocaleString('sv-SE', { maximumFractionDigits: 0 })}`;
}

function formatPct(value: unknown): string {
  return `${Math.round(numberValue(value) * 100)}%`;
}

function displayTier(value: unknown): string {
  const tiers: Record<string, string> = {
    Bronze: 'Club Member',
    Silver: 'Club Plus',
    Gold: 'Club Premier',
    Platinum: 'Club Signature',
  };
  const tier = textValue(value);
  return tiers[tier] ?? tier;
}

function displayTableName(value: unknown): string {
  const names: Record<string, string> = {
    bronze_campaign_interactions: 'Campaign interactions',
    bronze_customers: 'Customer profiles',
    bronze_loyalty_activity: 'Loyalty activity',
    bronze_retention_documents: 'Retention policy documents',
    bronze_support_tickets: 'Support tickets',
    bronze_transactions: 'Transactions',
  };
  const tableName = textValue(value);
  return names[tableName] ?? tableName.replace(/^bronze_/, '').replaceAll('_', ' ');
}

function displayQualityStatus(value: unknown): string {
  return textValue(value).toLowerCase() === 'pass' ? 'Validated' : textValue(value);
}

function normalizeList(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String);
  if (typeof value === 'string' && value.trim().startsWith('[')) {
    try {
      const parsed = JSON.parse(value);
      return Array.isArray(parsed) ? parsed.map(String) : [value];
    } catch {
      return [value];
    }
  }
  return value ? [String(value)] : [];
}

function rows(value: unknown): Row[] {
  return Array.isArray(value) ? (value as Row[]) : [];
}

function badgeVariant(risk: unknown): 'default' | 'secondary' | 'destructive' | 'outline' {
  const value = textValue(risk);
  if (value === 'High') return 'destructive';
  if (value === 'Medium') return 'secondary';
  return 'outline';
}

function useQuery(queryKey: NoParamQueryKey) {
  return useAnalyticsQuery(queryKey, {});
}

function useCustomerQuery(queryKey: CustomerQueryKey, customerId: string) {
  return useAnalyticsQuery(queryKey, { customer_id: sql.string(customerId) });
}

function QueryBlock({
  loading,
  error,
  empty,
  children,
}: {
  loading: boolean;
  error?: unknown;
  empty: boolean;
  children: ReactNode;
}) {
  if (loading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }
  if (error) return <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">Unable to load this view.</div>;
  if (empty) return <div className="rounded-md border p-4 text-sm text-muted-foreground">No data available.</div>;
  return <>{children}</>;
}

function OperationsPanel() {
  const [open, setOpen] = useState(false);
  const status = useQuery('operations_status');
  const counts = useQuery('layer_record_counts');
  const quality = useQuery('data_quality_status');
  const statusRow = status.data?.[0] as Row | undefined;

  return (
    <section className="border-t bg-muted/30 px-4 py-3 md:px-6">
      <Button variant="ghost" size="sm" onClick={() => setOpen((value) => !value)} className="gap-2">
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        Operations
      </Button>
      {open && (
        <div className="mt-3 grid gap-3 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Pipeline Status</CardTitle>
            </CardHeader>
            <CardContent>
              <QueryBlock loading={status.loading} error={status.error} empty={!statusRow}>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span>Status</span><Badge variant="outline">{textValue(statusRow?.status)}</Badge></div>
                  <div className="flex justify-between"><span>Customers scored</span><span>{numberValue(statusRow?.customers_scored)}</span></div>
                  <div className="flex justify-between"><span>Actions generated</span><span>{numberValue(statusRow?.retention_actions_generated)}</span></div>
                </div>
              </QueryBlock>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Table Volumes</CardTitle>
            </CardHeader>
            <CardContent>
              <QueryBlock loading={counts.loading} error={counts.error} empty={!counts.data?.length}>
                <div className="space-y-2 text-sm">
                  {rows(counts.data).map((row) => (
                    <div key={textValue(row.layer)} className="flex justify-between">
                      <span>{textValue(row.layer)}</span>
                      <span>{numberValue(row.records).toLocaleString('sv-SE')}</span>
                    </div>
                  ))}
                </div>
              </QueryBlock>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Source Health Checks</CardTitle>
            </CardHeader>
            <CardContent>
              <QueryBlock loading={quality.loading} error={quality.error} empty={!quality.data?.length}>
                <div className="space-y-2 text-xs">
                  <p className="text-muted-foreground">Input tables passed the prototype completeness checks before Customer 360 was built.</p>
                  {rows(quality.data).slice(0, 6).map((row) => (
                    <div key={textValue(row.table_name)} className="flex justify-between gap-3">
                      <span className="truncate">{displayTableName(row.table_name)}</span>
                      <Badge variant="outline">{displayQualityStatus(row.quality_status)}</Badge>
                    </div>
                  ))}
                </div>
              </QueryBlock>
            </CardContent>
          </Card>
        </div>
      )}
    </section>
  );
}

function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="border-b px-4 py-3 md:px-6">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-xl font-semibold text-foreground">Retail Intelligence</h1>
          <nav className="flex gap-1 text-sm">
            <NavLink to="/" className={({ isActive }) => `rounded-md px-3 py-1.5 ${isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}>
              Executive Overview
            </NavLink>
            <NavLink to={`/customer/${demoCustomerId}`} className={({ isActive }) => `rounded-md px-3 py-1.5 ${isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}>
              Customer 360
            </NavLink>
            <NavLink to={`/copilot/${demoCustomerId}`} className={({ isActive }) => `rounded-md px-3 py-1.5 ${isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}>
              Retention Copilot
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="flex-1 px-4 py-5 md:px-6">
        <Outlet />
      </main>
      <OperationsPanel />
    </div>
  );
}

function RiskPieChart({ data }: { data: Row[] }) {
  const order = ['High', 'Medium', 'Low'];
  const palette: Record<string, string> = {
    High: 'var(--destructive)',
    Medium: 'var(--warning)',
    Low: 'var(--success)',
  };
  const sortedRows = [...data].sort((a, b) => order.indexOf(textValue(a.risk_category)) - order.indexOf(textValue(b.risk_category)));
  const total = sortedRows.reduce((sum, row) => sum + numberValue(row.customers), 0);
  let cursor = 0;
  const gradient = sortedRows
    .map((row) => {
      const label = textValue(row.risk_category);
      const start = cursor;
      const end = total > 0 ? cursor + (numberValue(row.customers) / total) * 360 : cursor;
      cursor = end;
      return `${palette[label] ?? 'var(--primary)'} ${start}deg ${end}deg`;
    })
    .join(', ');

  return (
    <div className="grid gap-5 sm:grid-cols-[160px_1fr] sm:items-center">
      <div
        className="mx-auto h-40 w-40 rounded-full border"
        style={{ background: `conic-gradient(${gradient})` }}
        role="img"
        aria-label="Churn risk distribution pie chart"
      />
      <div className="space-y-3">
        {sortedRows.map((row) => {
          const label = textValue(row.risk_category);
          const customers = numberValue(row.customers);
          return (
            <div key={label} className="flex items-center justify-between gap-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-sm" style={{ backgroundColor: palette[label] ?? 'var(--primary)' }} />
                <span>{label} risk</span>
              </div>
              <span className="font-medium">{customers} ({total > 0 ? Math.round((customers / total) * 100) : 0}%)</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Kpi({ title, value, note, icon: Icon }: { title: string; value: string; note: string; icon: LucideIcon }) {
  return (
    <Card>
      <CardContent className="flex min-h-28 items-center justify-between gap-4 p-5">
        <div>
          <div className="text-sm text-muted-foreground">{title}</div>
          <div className="mt-1 text-2xl font-semibold">{value}</div>
          <div className="mt-1 text-xs text-muted-foreground">{note}</div>
        </div>
        <Icon className="h-7 w-7 text-primary" />
      </CardContent>
    </Card>
  );
}

function ExecutiveOverview() {
  const navigate = useNavigate();
  const metrics = useQuery('executive_metrics');
  const distribution = useQuery('risk_distribution');
  const segments = useQuery('high_risk_by_segment');
  const drivers = useQuery('top_churn_drivers');
  const customers = useQuery('customers_requiring_action');
  const metric = metrics.data?.[0] as Row | undefined;
  const riskRows = rows(distribution.data);
  const driverRows = rows(drivers.data);
  const maxDriver = Math.max(...(driverRows.length ? driverRows.map((row) => numberValue(row.customers)) : [1]));

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Executive Overview</h2>
        <p className="text-sm text-muted-foreground">Leadership now has one governed view of customer risk and revenue exposure.</p>
      </div>
      <QueryBlock loading={metrics.loading} error={metrics.error} empty={!metric}>
        <div className="grid gap-4 md:grid-cols-4">
          <Kpi title="High churn risk" value={numberValue(metric?.high_risk_customers).toString()} note="Customers needing action" icon={AlertTriangle} />
          <Kpi title="Revenue at risk" value={formatSek(metric?.revenue_at_risk_sek)} note="High-risk exposure" icon={Activity} />
          <Kpi title="Retention opportunities" value={numberValue(metric?.retention_opportunities).toString()} note="High and medium risk" icon={Target} />
          <Kpi title="Customers unified" value={numberValue(metric?.total_customers).toString()} note="Customer 360 records" icon={Database} />
        </div>
      </QueryBlock>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Churn Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <QueryBlock loading={distribution.loading} error={distribution.error} empty={!distribution.data?.length}>
              <RiskPieChart data={riskRows} />
            </QueryBlock>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top Churn Drivers</CardTitle>
          </CardHeader>
          <CardContent>
            <QueryBlock loading={drivers.loading} error={drivers.error} empty={!drivers.data?.length}>
              <div className="space-y-3">
                {driverRows.map((row) => (
                  <div key={textValue(row.reason_code)}>
                    <div className="mb-1 flex justify-between text-sm">
                      <span>{textValue(row.reason_code)}</span>
                      <span>{numberValue(row.customers)}</span>
                    </div>
                    <div className="h-2 rounded bg-muted">
                      <div className="h-2 rounded bg-primary" style={{ width: `${(numberValue(row.customers) / maxDriver) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </QueryBlock>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>High Risk by Customer Segment</CardTitle>
          </CardHeader>
          <CardContent>
            <QueryBlock loading={segments.loading} error={segments.error} empty={!segments.data?.length}>
              <div className="space-y-2 text-sm">
                {rows(segments.data).map((row) => (
                  <div key={`${textValue(row.segment)}-${textValue(row.loyalty_tier)}`} className="flex items-center justify-between gap-3 border-b py-2 last:border-0">
                    <div>
                      <div className="font-medium">{textValue(row.segment)}</div>
                      <div className="text-xs text-muted-foreground">{displayTier(row.loyalty_tier)}</div>
                    </div>
                    <div className="text-right">
                      <div>{numberValue(row.high_risk_customers)} customers</div>
                      <div className="text-xs text-muted-foreground">{formatSek(row.revenue_at_risk_sek)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </QueryBlock>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Customers Requiring Action</CardTitle>
        </CardHeader>
        <CardContent>
          <QueryBlock loading={customers.loading} error={customers.error} empty={!customers.data?.length}>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[860px] text-sm">
                <thead className="border-b text-left text-muted-foreground">
                  <tr>
                    <th className="py-2">Customer</th>
                    <th>Segment</th>
                    <th>Customer club</th>
                    <th>Risk</th>
                    <th>Probability</th>
                    <th>Revenue at risk</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {rows(customers.data).map((row) => (
                    <tr key={textValue(row.customer_id)} className="border-b last:border-0">
                      <td className="py-3">
                        <Button variant="link" className="h-auto p-0" onClick={() => navigate(`/customer/${textValue(row.customer_id)}`)}>
                          {textValue(row.full_name)}
                        </Button>
                        <div className="text-xs text-muted-foreground">{textValue(row.customer_id)}</div>
                      </td>
                      <td>{textValue(row.segment)}</td>
                      <td>{displayTier(row.loyalty_tier)}</td>
                      <td><Badge variant={badgeVariant(row.risk_category)}>{textValue(row.risk_category)}</Badge></td>
                      <td>{formatPct(row.churn_probability)}</td>
                      <td>{formatSek(row.revenue_at_risk_sek)}</td>
                      <td className="max-w-xs">{textValue(row.recommended_intervention)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </QueryBlock>
        </CardContent>
      </Card>
    </div>
  );
}

function useCustomerData(customerId: string) {
  return {
    profile: useCustomerQuery('customer_profile', customerId),
    prediction: useCustomerQuery('customer_prediction', customerId),
    transactions: useCustomerQuery('customer_transactions', customerId),
    support: useCustomerQuery('customer_support', customerId),
    campaigns: useCustomerQuery('customer_campaigns', customerId),
    action: useCustomerQuery('customer_action', customerId),
  };
}

function Customer360() {
  const navigate = useNavigate();
  const { customerId = demoCustomerId } = useParams();
  const data = useCustomerData(customerId);
  const profile = data.profile.data?.[0] as Row | undefined;
  const prediction = data.prediction.data?.[0] as Row | undefined;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">Customer 360</h2>
          <p className="text-sm text-muted-foreground">Sources to Customer 360 to churn prediction.</p>
        </div>
        <Button onClick={() => navigate(`/copilot/${customerId}`)} className="gap-2">
          Retention Copilot <ArrowRight className="h-4 w-4" />
        </Button>
      </div>
      <QueryBlock loading={data.profile.loading || data.prediction.loading} error={data.profile.error || data.prediction.error} empty={!profile || !prediction}>
        <div className="grid gap-4 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><UserRound className="h-5 w-5" /> Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <div className="text-xl font-semibold">{textValue(profile?.full_name)}</div>
                <div className="text-muted-foreground">{textValue(profile?.email)}</div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">PostgreSQL - profile</Badge>
                <Badge variant="outline">PostgreSQL - loyalty</Badge>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Info label="Segment" value={textValue(profile?.segment)} />
                <Info label="Customer club" value={displayTier(profile?.loyalty_tier)} />
                <Info label="Region" value={textValue(profile?.region)} />
                <Info label="Unused points" value={numberValue(profile?.unused_loyalty_points).toLocaleString('sv-SE')} />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Churn Prediction</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-4xl font-semibold">{formatPct(prediction?.churn_probability)}</div>
                <Badge variant={badgeVariant(prediction?.risk_category)}>{textValue(prediction?.risk_category)}</Badge>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">ML model - churn score</Badge>
                {normalizeList(prediction?.reason_codes).map((reason) => <Badge key={reason} variant="secondary">{reason}</Badge>)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Source Flow</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <FlowItem label="PostgreSQL" value="Profile and loyalty" />
              <FlowItem label="MySQL" value="Transactions" />
              <FlowItem label="SaaS" value="Support and campaigns" />
              <FlowItem label="ML model" value="Churn score and reason codes" />
            </CardContent>
          </Card>
        </div>
      </QueryBlock>
      <div className="grid gap-4 lg:grid-cols-3">
        <MiniTable title="Purchase History" source="MySQL - transactions" query={data.transactions} columns={['transaction_date', 'category', 'amount_sek', 'returned']} />
        <MiniTable title="Support Tickets" source="SaaS - support" query={data.support} columns={['opened_date', 'issue_type', 'status', 'csat_score']} />
        <MiniTable title="Campaign Engagement" source="SaaS - campaigns" query={data.campaigns} columns={['campaign_date', 'campaign_name', 'channel', 'opened']} />
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-medium">{value}</div>
    </div>
  );
}

function FlowItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 rounded-md border p-3">
      <CheckCircle2 className="h-4 w-4 text-primary" />
      <div>
        <div className="font-medium">{label}</div>
        <div className="text-muted-foreground">{value}</div>
      </div>
    </div>
  );
}

function MiniTable({ title, source, query, columns }: { title: string; source: string; query: MiniQueryResult; columns: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <Badge variant="outline" className="mb-3">{source}</Badge>
        <QueryBlock loading={query.loading} error={query.error} empty={!query.data?.length}>
          <div className="space-y-2 text-xs">
            {rows(query.data).slice(0, 6).map((row, index) => (
              <div key={index} className="rounded-md border p-2">
                {columns.map((column) => (
                  <div key={column} className="flex justify-between gap-3">
                    <span className="text-muted-foreground">{column.replaceAll('_', ' ')}</span>
                    <span>{column.includes('amount') ? formatSek(row[column]) : textValue(row[column])}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </QueryBlock>
      </CardContent>
    </Card>
  );
}

function RetentionCopilot() {
  const { customerId = demoCustomerId } = useParams();
  const data = useCustomerData(customerId);
  const profile = data.profile.data?.[0] as Row | undefined;
  const prediction = data.prediction.data?.[0] as Row | undefined;
  const action = data.action.data?.[0] as Row | undefined;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Retention Copilot</h2>
        <p className="text-sm text-muted-foreground">Customer 360 + ML Prediction + Business Knowledge to Next-Best Action.</p>
      </div>
      <QueryBlock loading={data.profile.loading || data.prediction.loading || data.action.loading} error={data.profile.error || data.prediction.error || data.action.error} empty={!profile || !prediction || !action}>
        <div className="grid gap-4 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Customer Context</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <Info label="Customer" value={`${textValue(profile?.full_name)} (${customerId})`} />
              <Info label="Segment" value={textValue(profile?.segment)} />
              <Info label="Spend trend" value={numberValue(profile?.spend_trend_ratio).toFixed(3)} />
              <Info label="Open support tickets" value={numberValue(profile?.open_support_ticket_count).toString()} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Model Output</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-4xl font-semibold">{formatPct(prediction?.churn_probability)}</span>
                <Badge variant={badgeVariant(prediction?.risk_category)}>{textValue(prediction?.risk_category)}</Badge>
              </div>
              <div className="flex flex-wrap gap-2">
                {normalizeList(prediction?.reason_codes).map((reason) => <Badge key={reason} variant="secondary">{reason}</Badge>)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Based On</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {normalizeList(action?.evidence_used).map((item) => (
                <div key={item} className="flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-primary" /> {item}</div>
              ))}
            </CardContent>
          </Card>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Sparkles className="h-5 w-5" /> Generated Recommendation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-muted-foreground">Risk summary</div>
                <p className="font-medium">{textValue(action?.risk_summary)}</p>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Next-best action</div>
                <p className="font-medium">{textValue(action?.recommended_intervention)}</p>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                <span className="font-medium">{textValue(action?.suggested_channel)}</span>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Business rationale</div>
                <p>{textValue(action?.estimated_business_rationale)}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Message and Policy Evidence</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-md border p-3 text-sm">{textValue(action?.personalized_message)}</div>
              <div className="space-y-2">
                {normalizeList(action?.policy_excerpts).map((excerpt) => (
                  <div key={excerpt} className="rounded-md bg-muted p-3 text-sm">{excerpt}</div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </QueryBlock>
    </div>
  );
}

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <ExecutiveOverview /> },
      { path: '/customer/:customerId', element: <Customer360 /> },
      { path: '/copilot/:customerId', element: <RetentionCopilot /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
