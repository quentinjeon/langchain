/**
 * API 호출을 위한 유틸리티 함수
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API || 'http://localhost:8000/api';

interface FetchOptions extends RequestInit {
  data?: any;
}

export async function fetcher<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { data, ...fetchOptions } = options;
  
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const config: RequestInit = {
    method: data ? 'POST' : 'GET',
    ...fetchOptions,
    headers,
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || response.statusText);
  }
  
  return response.json();
} 