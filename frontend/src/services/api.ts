// API endpoints for MySLT Bot
const API_BASE_URL = 'http://localhost:8000';

export interface UsageSummary {
  used: number;
  limit: number;
  percentage: number;
}

export interface ProfileInfo {
  fullname: string;
  package: string;
  contact_no?: string;
  email?: string;
  raw_data: Record<string, any>;
}

export interface BillStatus {
  status: string;
  amount?: number;
  due_date?: string;
  raw_data: Record<string, any>;
}

export interface VASBundle {
  name: string;
  used?: string;
  expiry_date?: string;
  description?: string;
  raw_data: Record<string, any>;
}

export interface VASBundles {
  bundles: VASBundle[];
}

// Generic fetch function with error handling
async function fetchData<T>(endpoint: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json() as T;
  } catch (error) {
    console.error(`Failed to fetch data from ${endpoint}:`, error);
    throw error;
  }
}

// API functions
export const api = {
  // Usage related endpoints
  getUsageSummary: () => fetchData<UsageSummary>('/usage/summary'),
  
  // Profile related endpoints
  getProfileInfo: () => fetchData<ProfileInfo>('/profile/info'),
  
  // Bill related endpoints
  getBillStatus: () => fetchData<BillStatus>('/bills/status'),
  getBillPaymentInfo: () => fetchData<Record<string, any>>('/bills/payment'),
  
  // VAS related endpoints
  getVASBundles: () => fetchData<VASBundles>('/vas/bundles'),
  getExtraGB: () => fetchData<Record<string, any>>('/vas/extra-gb'),
  
  // Health check
  checkHealth: () => fetchData<{status: string, service: string}>('/health'),
}; 