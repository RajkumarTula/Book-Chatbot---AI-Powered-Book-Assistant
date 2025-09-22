import { useState, useCallback } from 'react';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function useBooks() {
  const [featuredBooks, setFeaturedBooks] = useState([]);

  // Query for featured books
  const { refetch: loadFeaturedBooks } = useQuery(
    'featuredBooks',
    async () => {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'bestseller',
          max_results: 3,
          source: 'both'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setFeaturedBooks(data.books || []);
      return data;
    },
    {
      enabled: false, // Don't auto-fetch
      onError: (error) => {
        console.error('Error loading featured books:', error);
        toast.error('Failed to load featured books');
      }
    }
  );

  // Mutation for getting book details
  const getBookDetailsMutation = useMutation(
    async (bookTitle) => {
      const response = await fetch(`${API_BASE_URL}/book-details`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: bookTitle
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onError: (error) => {
        console.error('Error fetching book details:', error);
        toast.error('Failed to load book details');
      }
    }
  );

  const getBookDetails = useCallback(async (bookTitle) => {
    try {
      const data = await getBookDetailsMutation.mutateAsync(bookTitle);
      return data;
    } catch (error) {
      throw error;
    }
  }, [getBookDetailsMutation]);

  return {
    featuredBooks,
    loadFeaturedBooks,
    getBookDetails,
    isLoading: getBookDetailsMutation.isLoading
  };
}


