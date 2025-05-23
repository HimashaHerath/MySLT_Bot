import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useVasBundles } from "@/hooks/useApiData";
import { Loader2, AlertCircle, RefreshCw, Box, Calendar } from "lucide-react";

export function VASBundleCard() {
  const { data: vasData, isLoading, error, refetch } = useVasBundles();

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-10">
          <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">Loading VAS bundle information...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error loading VAS bundles</AlertTitle>
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

  // Check if there are no bundles
  if (!vasData.bundles || vasData.bundles.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Value-Added Services</CardTitle>
          <CardDescription>Your active VAS bundles</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>No Active Bundles</AlertTitle>
            <AlertDescription>
              You don't have any active VAS bundles at this time.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Calculate days left for expiry
  const calculateDaysLeft = (expiryDate: string | undefined) => {
    if (!expiryDate) return null;
    
    try {
      const expiry = new Date(expiryDate);
      const today = new Date();
      const diffTime = expiry.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays > 0 ? diffDays : 0;
    } catch (e) {
      return null;
    }
  };

  // Determine color based on days left
  const getExpiryColorClass = (daysLeft: number | null) => {
    if (daysLeft === null) return "text-gray-500";
    if (daysLeft <= 3) return "text-red-500";
    if (daysLeft <= 7) return "text-yellow-500";
    return "text-green-500";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Value-Added Services</CardTitle>
        <CardDescription>Your active VAS bundles</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {vasData.bundles.map((bundle, index) => {
            const daysLeft = calculateDaysLeft(bundle.expiry_date);
            const expiryColorClass = getExpiryColorClass(daysLeft);
            
            return (
              <div 
                key={index} 
                className="border rounded-lg p-4 bg-card"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-md">{bundle.name}</h3>
                  {bundle.expiry_date && (
                    <div className={`flex items-center gap-1 text-xs ${expiryColorClass}`}>
                      <Calendar className="h-3 w-3" />
                      {daysLeft !== null ? (
                        daysLeft === 0 ? "Expires today" : `${daysLeft} day${daysLeft !== 1 ? 's' : ''} left`
                      ) : (
                        `Expires: ${bundle.expiry_date}`
                      )}
                    </div>
                  )}
                </div>
                {bundle.used && (
                  <div className="flex items-center gap-1 text-sm">
                    <Box className="h-4 w-4 text-muted-foreground" />
                    <span>Used: {bundle.used}</span>
                  </div>
                )}
                {bundle.description && (
                  <p className="text-xs text-muted-foreground mt-2">{bundle.description}</p>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" onClick={refetch} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh Bundles
        </Button>
      </CardFooter>
    </Card>
  );
} 