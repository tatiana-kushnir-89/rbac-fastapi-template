import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { UsersService } from "@/client"
import { MetricsService } from "@/client/services/MetricsService"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { permissions } from "@/utils/rbac"

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!permissions.canViewMetrics(user.role)) {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Metrics - FastAPI Template" }],
  }),
})

function Metrics() {
  const {
    data: metrics,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["metrics"],
    queryFn: MetricsService.getMetrics,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading metrics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-destructive">Failed to load metrics</div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">System insights and statistics</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Users" value={metrics?.total_users ?? 0} />
        <MetricCard title="Active Users" value={metrics?.active_users ?? 0} />
        <MetricCard title="Total Items" value={metrics?.total_items ?? 0} />
        <RoleDistributionCard usersByRole={metrics?.users_by_role} />
      </div>
    </div>
  )
}

function MetricCard({ title, value }: { title: string; value: number }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  )
}

function RoleDistributionCard({
  usersByRole,
}: {
  usersByRole?: Record<string, number>
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Users by Role</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm space-y-1">
          {usersByRole &&
            Object.entries(usersByRole).map(([role, count]) => (
              <div key={role} className="flex justify-between">
                <span className="capitalize">{role}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  )
}