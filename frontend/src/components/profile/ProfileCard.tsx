import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useProfile } from "@/hooks/useApiData";
import { Loader2, AlertCircle, RefreshCw, User, Package, Phone, Mail, Smartphone } from "lucide-react";

export function ProfileCard() {
  const { data: profile, isLoading, error, refetch } = useProfile();

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-10">
          <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">Loading profile data...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error loading profile</AlertTitle>
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

  const profileFields = [
    { icon: <User className="h-4 w-4" />, label: "Name", value: profile.fullname },
    { icon: <Package className="h-4 w-4" />, label: "Package", value: profile.package },
    { icon: <Phone className="h-4 w-4" />, label: "Contact No", value: profile.contact_no || 'Not provided' },
    { icon: <Mail className="h-4 w-4" />, label: "Email", value: profile.email || 'Not provided' },
    { 
      icon: <Smartphone className="h-4 w-4" />, 
      label: "Mobile No", 
      value: profile.raw_data?.mobile_no || 'Not provided'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Profile</CardTitle>
        <CardDescription>Your SLT account information</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="flex flex-col space-y-4">
            {profileFields.map((field, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="rounded-full p-2 bg-muted flex items-center justify-center">
                  {field.icon}
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">{field.label}</p>
                  <p className="text-sm">{field.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" onClick={refetch} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh Profile
        </Button>
      </CardFooter>
    </Card>
  );
} 