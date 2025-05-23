import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useUsageSummary } from "@/hooks/useApiData";
import { Loader2, AlertCircle, RefreshCw, Sun, Moon } from "lucide-react";

export function UsageCard() {
  const { data: usage, isLoading, error, refetch } = useUsageSummary();

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-10">
          <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">Loading usage data...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error loading data</AlertTitle>
        <AlertDescription>
          {error.message}
          <div className="mt-2">
            <Button variant="outline" size="sm" onClick={refetch}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  // Calculate color based on percentage
  const getColorClass = (percentage: number) => {
    if (percentage < 50) return "bg-green-500";
    if (percentage < 80) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>SLT Data Usage</CardTitle>
        <CardDescription>
          Your current data usage statistics
          {usage.reported_time && (
            <span className="block text-xs mt-1">Last updated: {usage.reported_time}</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Total Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-medium text-base">Total Usage:</span>
            <span className="font-medium">{usage.total_percentage.toFixed(1)}%</span>
          </div>
          <div className="relative w-full h-3 bg-muted rounded-full overflow-hidden">
            <div 
              className={`absolute top-0 left-0 h-full ${getColorClass(usage.total_percentage)} transition-all duration-500`} 
              style={{ width: `${usage.total_percentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0GB</span>
            <span>{usage.total_limit}GB</span>
          </div>
          <p className="text-sm pt-1">
            You have used <span className="font-medium">{usage.total_used.toFixed(1)}GB</span> out of your <span className="font-medium">{usage.total_limit}GB</span> total monthly data allowance.
          </p>
        </div>

        {/* Daytime & Nighttime Usage Tabs */}
        <Tabs defaultValue="daytime" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="daytime" className="flex items-center gap-1">
              <Sun className="h-4 w-4" /> Daytime
            </TabsTrigger>
            <TabsTrigger value="nighttime" className="flex items-center gap-1">
              <Moon className="h-4 w-4" /> Nighttime
            </TabsTrigger>
          </TabsList>
          
          {/* Daytime Content */}
          <TabsContent value="daytime" className="mt-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">Standard (Daytime) Data:</span>
              <span className="font-medium">{usage.daytime.percentage.toFixed(1)}%</span>
            </div>
            <div className="relative w-full h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className={`absolute top-0 left-0 h-full bg-amber-500 transition-all duration-500`} 
                style={{ width: `${usage.daytime.percentage}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0GB</span>
              <span>{usage.daytime.limit}GB</span>
            </div>
            <p className="text-sm pt-1">
              Used: <span className="font-medium">{usage.daytime.used.toFixed(1)}GB</span> / 
              Remaining: <span className="font-medium">{usage.daytime.remaining.toFixed(1)}GB</span>
            </p>
            <p className="text-xs text-muted-foreground">
              Standard data can be used any time, day or night.
            </p>
          </TabsContent>
          
          {/* Nighttime Content */}
          <TabsContent value="nighttime" className="mt-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">Free (Nighttime) Data:</span>
              <span className="font-medium">{usage.nighttime.percentage.toFixed(1)}%</span>
            </div>
            <div className="relative w-full h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className={`absolute top-0 left-0 h-full bg-blue-500 transition-all duration-500`} 
                style={{ width: `${usage.nighttime.percentage}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0GB</span>
              <span>{usage.nighttime.limit}GB</span>
            </div>
            <p className="text-sm pt-1">
              Used: <span className="font-medium">{usage.nighttime.used.toFixed(1)}GB</span> / 
              Remaining: <span className="font-medium">{usage.nighttime.remaining.toFixed(1)}GB</span>
            </p>
            <p className="text-xs text-muted-foreground">
              Nighttime data can only be used between 12AM and 8AM.
            </p>
          </TabsContent>
        </Tabs>

        {usage.total_percentage > 90 && (
          <Alert className="mt-2">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>High Usage Warning</AlertTitle>
            <AlertDescription>
              You're close to your data limit. Consider purchasing additional data to avoid slowdowns.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
      <CardFooter>
        <Button variant="outline" onClick={refetch} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh Data
        </Button>
      </CardFooter>
    </Card>
  );
} 