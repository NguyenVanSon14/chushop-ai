export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_platform_admin: boolean;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
};

export type Business = {
  id: string;
  name: string;
  slug: string;
  currency: string;
  timezone: string;
  created_at: string;
  updated_at: string;
};

export type Product = {
  id: string;
  business_id: string;
  name: string;
  sku: string | null;
  selling_price: number;
  cost_price: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ImportPreviewRow = {
  order_code: string;
  channel: string;
  ordered_at: string;
  sku: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  cost_price_snapshot: number;
  fees: number;
};

export type ImportPreview = {
  filename: string;
  row_count: number;
  order_count: number;
  total_revenue: number;
  total_cost: number;
  total_fees: number;
  rows: ImportPreviewRow[];
};

export type SalesImport = {
  id: string;
  business_id: string;
  filename: string;
  row_count: number;
  created_at: string;
};

export type SalesOrderItem = {
  id: string;
  product_id: string | null;
  product_name_snapshot: string;
  sku_snapshot: string;
  quantity: number;
  unit_price: number;
  cost_price_snapshot: number;
  revenue: number;
  cogs: number;
};

export type SalesOrder = {
  id: string;
  business_id: string;
  external_id: string;
  channel: string;
  ordered_at: string;
  fees: number;
  revenue: number;
  cogs: number;
  items: SalesOrderItem[];
};

export type Expense = {
  id: string;
  business_id: string;
  description: string;
  category: string;
  amount: number;
  incurred_on: string;
  created_at: string;
  updated_at: string;
};

export type AnalyticsPeriod = {
  date_from: string;
  date_to: string;
};

export type MetricComparison = {
  current: number;
  previous: number;
  difference: number;
  change_bps: number | null;
};

export type AnalyticsSummary = {
  order_count: number;
  revenue: number;
  cogs: number;
  fees: number;
  gross_profit: number;
  expenses: number;
  net_profit: number;
  gross_margin_bps: number | null;
  net_margin_bps: number | null;
};

export type TrendPoint = {
  date: string;
  revenue: number;
  cogs: number;
  fees: number;
  expenses: number;
  net_profit: number;
};

export type ProductProfitability = {
  sku: string;
  name: string;
  quantity: number;
  revenue: number;
  cogs: number;
  gross_profit: number;
  gross_margin_bps: number | null;
};

export type ChannelProfitability = {
  channel: string;
  order_count: number;
  revenue: number;
  cogs: number;
  fees: number;
  contribution_profit: number;
  contribution_margin_bps: number | null;
};

export type Analytics = {
  period: AnalyticsPeriod;
  previous_period: AnalyticsPeriod;
  summary: AnalyticsSummary;
  revenue_comparison: MetricComparison;
  net_profit_comparison: MetricComparison;
  trends: TrendPoint[];
  products: ProductProfitability[];
  channels: ChannelProfitability[];
};

export type AssistantConversation = {
  id: string;
  business_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type AssistantMessage = {
  id: string;
  conversation_id: string;
  role: "USER" | "ASSISTANT";
  content: string;
  tool_name: string | null;
  tool_result: Record<string, unknown> | null;
  created_at: string;
};

export type AssistantConversationDetail = AssistantConversation & {
  messages: AssistantMessage[];
};

export type AssistantReply = {
  user_message: AssistantMessage;
  assistant_message: AssistantMessage;
};

export type AdminUser = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_platform_admin: boolean;
  created_at: string;
};

export type AdminBusiness = {
  id: string;
  name: string;
  slug: string;
  currency: string;
  timezone: string;
  created_at: string;
};

export type AdminAuditLog = {
  id: string;
  actor_user_id: string;
  action: string;
  target_type: string;
  target_id: string;
  details: Record<string, unknown>;
  created_at: string;
};
