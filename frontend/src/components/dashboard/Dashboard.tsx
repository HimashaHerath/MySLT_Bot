import { useState } from "react";
import { UsageCard } from "@/components/usage/UsageCard";
import { ProfileCard } from "@/components/profile/ProfileCard";
import { BillCard } from "@/components/bill/BillCard";
import { VASBundleCard } from "@/components/vas/VASBundleCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Gauge, BarChart3, CheckCircle2, Info, AlertCircle } from "lucide-react";
import { useUsageSummary, useProfile, useBillStatus, useVasBundles } from "@/hooks/useApiData";

export function Dashboard() {
  // For the summary view, we need all the data
  const { data: usage, isLoading: usageLoading, error: usageError } = useUsageSummary();
  const { data: profile, isLoading: profileLoading, error: profileError } = useProfile();
  const { data: bill, isLoading: billLoading, error: billError } = useBillStatus();
  const { data: vas, isLoading: vasLoading, error: vasError } = useVasBundles();
  
  const isLoading = usageLoading || profileLoading || billLoading || vasLoading;
  const hasError = usageError || profileError || billError || vasError;

  // Function to determine health status
  const getStatus = () => {
    if (hasError) return { label: "Service Unavailable", icon: <AlertCircle className="h-5 w-5 text-red-500" /> };
    if (isLoading) return { label: "Loading...", icon: <Info className="h-5 w-5 text-yellow-500" /> };
    return { label: "All Systems Operational", icon: <CheckCircle2 className="h-5 w-5 text-green-500" /> };
  };
  
  // Get summary information
  const status = getStatus();
  const activeVasBundles = vas.bundles?.length || 0;
  const hasBillDue = bill.status?.toLowerCase()?.includes('unpaid');
  
  // Stats for the dashboard
  const stats = [
    {
      title: "Data Usage",
      value: `${usage.percentage.toFixed(1)}%`,
      description: `${usage.used}GB of ${usage.limit}GB used`,
      icon: <Gauge className="h-5 w-5" />,
      color: usage.percentage > 80 ? "text-red-500" : usage.percentage > 60 ? "text-yellow-500" : "text-green-500"
    },
    {
      title: "Active Bundles",
      value: activeVasBundles.toString(),
      description: activeVasBundles === 1 ? "VAS bundle active" : "VAS bundles active",
      icon: <BarChart3 className="h-5 w-5" />,
      color: "text-blue-500"
    }
  ];

  return (
    <div className="space-y-8">
      {/* Status Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {status.icon}
            <span>Status: {status.label}</span>
          </CardTitle>
          <CardDescription>MySLT API connection status</CardDescription>
        </CardHeader>
        {hasError && (
          <CardContent>
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Connection Error</AlertTitle>
              <AlertDescription>
                There was an error connecting to the MySLT API. Please try refreshing or check your connection.
              </AlertDescription>
            </Alert>
          </CardContent>
        )}
      </Card>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2">
        {stats.map((stat, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className="rounded-full p-1 bg-muted">
                {stat.icon}
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${stat.color}`}>
                {stat.value}
              </div>
              <p className="text-xs text-muted-foreground">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Bill Alert (show only if there's a bill due) */}
      {hasBillDue && !billLoading && !billError && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Payment Due</AlertTitle>
          <AlertDescription>
            You have a pending bill payment of Rs. {bill.amount?.toFixed(2)}. Due date: {bill.due_date || 'Check bill details'}.
          </AlertDescription>
        </Alert>
      )}

      {/* Information Tabs */}
      <Tabs defaultValue="usage" className="w-full">
        <TabsList className="grid grid-cols-4 mb-4">
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="bill">Bill</TabsTrigger>
          <TabsTrigger value="vas">VAS Bundles</TabsTrigger>
        </TabsList>
        
        <TabsContent value="usage">
          <UsageCard />
        </TabsContent>
        
        <TabsContent value="profile">
          <ProfileCard />
        </TabsContent>
        
        <TabsContent value="bill">
          <BillCard />
        </TabsContent>
        
        <TabsContent value="vas">
          <VASBundleCard />
        </TabsContent>
      </Tabs>
    </div>
  );
} 