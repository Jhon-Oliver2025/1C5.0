
// Hook personalizado para chamadas à API com autenticação automática
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

interface ApiResponse<T = any> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

export const useApi = () => {
  const { apiCall } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = async <T = any>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiCall(url, options);
      
      if (response.ok) {
        const data = await response.json();
        setLoading(false);
        return { data, error: null, loading: false };
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Erro desconhecido' }));
        const errorMessage = errorData.error || `Erro ${response.status}`;
        setError(errorMessage);
        setLoading(false);
        return { data: null, error: errorMessage, loading: false };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro de conexão';
      setError(errorMessage);
      setLoading(false);
      return { data: null, error: errorMessage, loading: false };
    }
  };

  return {
    request,
    loading,
    error,
  };
};

export default useApi;
