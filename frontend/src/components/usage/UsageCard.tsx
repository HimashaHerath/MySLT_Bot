import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useUsageSummary } from "@/hooks/useApiData";
import { Loader2, AlertCircle, RefreshCw } from "lucide-react";

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
        <CardDescription>Your current data usage statistics</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span>Data Used:</span>
            <span className="font-medium">{usage.percentage.toFixed(1)}%</span>
          </div>
          <div className="relative w-full h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className={`absolute top-0 left-0 h-full ${getColorClass(usage.percentage)} transition-all duration-500`} 
              style={{ width: `${usage.percentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0GB</span>
            <span>{usage.limit}GB</span>
          </div>
        </div>
        <div className="pt-2">
          <p className="text-sm">
            You have used <span className="font-medium">{usage.used}GB</span> out of your <span className="font-medium">{usage.limit}GB</span> monthly data allowance.
          </p>
          {usage.percentage > 90 && (
            <Alert className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>High Usage Warning</AlertTitle>
              <AlertDescription>
                You're close to your data limit. Consider purchasing additional data to avoid slowdowns.
              </AlertDescription>
            </Alert>
          )}
        </div>
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