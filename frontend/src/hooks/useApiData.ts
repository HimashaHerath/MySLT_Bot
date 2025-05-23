import { useState, useEffect } from 'react';
import { api } from '@/services/api';

// Generic hook for fetching data from any API endpoint
export function useApiData<T>(
  fetchFunction: () => Promise<T>,
  initialData: T,
  refreshInterval?: number
) {
  const [data, setData] = useState<T>(initialData);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Set up polling if refreshInterval is provided
    if (refreshInterval) {
      const intervalId = setInterval(fetchData, refreshInterval);
      return () => clearInterval(intervalId);
    }
  }, []);

  return {
    data,
    isLoading,
    error,
    refetch: fetchData,
  };
}

// Specific hooks for each API endpoint
export function useUsageSummary(refreshInterval?: number) {
  return useApiData(api.getUsageSummary, { used: 0, limit: 1, percentage: 0 }, refreshInterval);
}

export function useProfile() {
  return useApiData(api.getProfileInfo, {
    fullname: '',
    package: '',
    raw_data: {}
  });
}

export function useBillStatus() {
  return useApiData(api.getBillStatus, {
    status: '',
    raw_data: {}
  });
}

export function useVasBundles() {
  return useApiData(api.getVASBundles, {
    bundles: []
  });
}

export function useExtraGb() {
  return useApiData(api.getExtraGB, {});
}

export function useHealthCheck() {
  return useApiData(api.checkHealth, { status: '', service: '' });
} 