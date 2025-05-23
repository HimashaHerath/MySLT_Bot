import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Dashboard } from '@/components/dashboard/Dashboard';
import { UsageCard } from '@/components/usage/UsageCard';
import { ProfileCard } from '@/components/profile/ProfileCard';
import { BillCard } from '@/components/bill/BillCard';
import { VASBundleCard } from '@/components/vas/VASBundleCard';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, Server } from 'lucide-react';
import { useHealthCheck } from '@/hooks/useApiData';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { data: health, isLoading: healthLoading, error: healthError } = useHealthCheck();
  const [isBackendAvailable, setIsBackendAvailable] = useState(true);

  // Check if the backend is available
  useEffect(() => {
    // If loading is complete and there's an error or status is not 'ok'
    if (!healthLoading && (healthError || health.status !== 'ok')) {
      setIsBackendAvailable(false);
    } else if (!healthLoading) {
      setIsBackendAvailable(true);
    }
  }, [healthLoading, healthError, health]);

  const renderContent = () => {
    // If we can't connect to the backend, show an error
    if (!isBackendAvailable && !healthLoading) {
      return (
        <Alert variant="destructive" className="mt-8">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle className="text-lg">Backend Connection Error</AlertTitle>
          <AlertDescription className="mt-2">
            <p className="mb-2">Unable to connect to the MySLT Bot API. This could be due to:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>The API server is not running</li>
              <li>CORS issues (if you're running the frontend and backend on different domains)</li>
              <li>Network connectivity problems</li>
            </ul>
            <div className="flex items-center gap-2 mt-4 p-3 bg-destructive/10 rounded-md">
              <Server className="h-5 w-5" />
              <p>Make sure the API server is running on <code className="bg-destructive/20 rounded px-1">http://localhost:8000</code></p>
            </div>
            <p className="mt-4">You're currently seeing demo data. Actual data will be displayed once the connection is restored.</p>
          </AlertDescription>
        </Alert>
      );
    }

    // Show the content based on the active tab
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'usage':
        return <UsageCard />;
      case 'profile':
        return <ProfileCard />;
      case 'bill':
        return <BillCard />;
      case 'vas':
        return <VASBundleCard />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab}>
      {renderContent()}
    </DashboardLayout>
  );
}

export default App;
