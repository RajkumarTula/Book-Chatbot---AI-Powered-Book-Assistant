import { useState, useEffect, useCallback } from 'react';
import { useQuery } from 'react-query';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function useAPI() {
  const [isOnline, setIsOnline] = useState(true);

  // Query for API health check
  const { refetch: checkAPIStatus } = useQuery(
    'apiHealth',
    async () => {
      const response = await fetch(`${API_BASE_URL}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    },
    {
      enabled: false, // Don't auto-fetch
      onSuccess: (data) => {
        setIsOnline(data.status === 'healthy');
      },
      onError: () => {
        setIsOnline(false);
      }
    }
  );

  // Check online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      checkAPIStatus();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [checkAPIStatus]);

  // Check API status periodically
  useEffect(() => {
    const interval = setInterval(() => {
      checkAPIStatus();
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [checkAPIStatus]);

  // Initial check
  useEffect(() => {
    checkAPIStatus();
  }, [checkAPIStatus]);

  return {
    isOnline,
    checkAPIStatus
  };
}



