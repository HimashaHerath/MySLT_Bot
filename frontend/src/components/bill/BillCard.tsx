import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useBillStatus } from "@/hooks/useApiData";
import { Loader2, AlertCircle, RefreshCw, Receipt, Calendar, Clock, Wallet } from "lucide-react";
import { useState } from "react";

export function BillCard() {
  const { data: bill, isLoading, error, refetch } = useBillStatus();
  const [paymentProcessing, setPaymentProcessing] = useState(false);

  const handlePayBill = () => {
    setPaymentProcessing(true);
    // Simulate payment processing
    setTimeout(() => {
      alert("This is a demo. In a real app, this would redirect to a payment gateway.");
      setPaymentProcessing(false);
    }, 1500);
  };

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-10">
          <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">Loading bill information...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error loading bill information</AlertTitle>
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

  // Format the due date if available
  const formattedDueDate = bill.due_date 
    ? new Date(bill.due_date).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    : 'Not available';

  // Determine status color and icon
  const getStatusInfo = (status: string) => {
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes('paid')) {
      return {
        color: 'text-green-500',
        badgeClass: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
        icon: <Clock className="h-4 w-4" />
      };
    } 
    if (lowerStatus.includes('due') || lowerStatus.includes('unpaid')) {
      return {
        color: 'text-red-500',
        badgeClass: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
        icon: <AlertCircle className="h-4 w-4" />
      };
    }
    // Default
    return {
      color: 'text-yellow-500',
      badgeClass: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
      icon: <Clock className="h-4 w-4" />
    };
  };

  const statusInfo = getStatusInfo(bill.status);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bill Status</CardTitle>
        <CardDescription>Your current bill information</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Receipt className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">Status</span>
          </div>
          <span className={`px-2.5 py-0.5 rounded-md text-xs font-medium ${statusInfo.badgeClass}`}>
            {statusInfo.icon && <span className="mr-1 inline-block">{statusInfo.icon}</span>}
            {bill.status}
          </span>
        </div>

        <div className="flex flex-col space-y-4 mt-4">
          {bill.amount !== undefined && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Wallet className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium">Amount</span>
              </div>
              <span className="font-semibold">
                Rs. {typeof bill.amount === 'number' ? bill.amount.toFixed(2) : bill.amount}
              </span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm font-medium">Due Date</span>
            </div>
            <span>{formattedDueDate}</span>
          </div>
        </div>

        {bill.status.toLowerCase().includes('unpaid') && (
          <Alert className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Payment Due</AlertTitle>
            <AlertDescription>
              Your bill payment is due. Please make a payment to continue enjoying uninterrupted service.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button variant="outline" onClick={refetch} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
        {bill.status.toLowerCase().includes('unpaid') && (
          <Button onClick={handlePayBill} disabled={paymentProcessing}>
            {paymentProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              'Pay Bill'
            )}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
} 