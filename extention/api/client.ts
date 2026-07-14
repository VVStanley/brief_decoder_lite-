import axios from 'axios';
import { DEFAULT_API_URL, STORAGE_KEYS } from '../config';
import type { BriefResponse } from './types';

// Create the axios instance
const api = axios.create({
  baseURL: DEFAULT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Cache for the API URL
let cachedApiUrl = DEFAULT_API_URL;

// Read config from chrome storage if available
const updateCacheFromStorage = () => {
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get([STORAGE_KEYS.API_URL], (res) => {
      if (res[STORAGE_KEYS.API_URL]) {
        cachedApiUrl = res[STORAGE_KEYS.API_URL] as string;
      }
    });
  }
};

// Initial update
updateCacheFromStorage();

// Listen to storage changes to update config on the fly
if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.onChanged) {
  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'local') {
      if (changes[STORAGE_KEYS.API_URL]) {
        cachedApiUrl = (changes[STORAGE_KEYS.API_URL].newValue as string) || DEFAULT_API_URL;
      }
    }
  });
}

// Apply base URL dynamically using request interceptor
api.interceptors.request.use((config) => {
  config.baseURL = cachedApiUrl;
  return config;
});

/**
 * Updates client configuration programmatically
 */
export const updateClientConfig = (url: string) => {
  cachedApiUrl = url;
};

export const apiService = {
  /**
   * Starts a new brief decode task.
   * Returns a BriefResponse (status: pending/processing, with task UUID).
   */
  async parseBrief(text: string): Promise<BriefResponse> {
    const response = await api.post<BriefResponse>('/api/v1/briefs', { text });
    return response.data;
  },

  /**
   * Retrieves status and results of a brief decode task.
   */
  async getBrief(id: string): Promise<BriefResponse> {
    const response = await api.get<BriefResponse>(`/api/v1/briefs/${id}`);
    return response.data;
  },
};
