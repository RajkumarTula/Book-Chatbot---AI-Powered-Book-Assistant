import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function useChat() {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! I'm your personal book assistant. I can help you find books, get recommendations, check prices, ratings, and availability. What would you like to know about books today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [isLoading, setIsLoading] = useState(false);

  const queryClient = useQueryClient();

  const sendMessageMutation = useMutation(
    async ({ message, source }) => {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          source_preference: source || 'both'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onMutate: async ({ message }) => {
        // Add user message immediately
        const userMessage = {
          sender: 'user',
          text: message,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
      },
      onSuccess: (data) => {
        // Add bot response
        const botMessage = {
          sender: 'bot',
          text: data.response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          intent: data.intent
        };
        
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
      },
      onError: (error) => {
        console.error('Error sending message:', error);
        toast.error('Sorry, I encountered an error. Please try again.');
        setIsLoading(false);
        
        // Add error message
        const errorMessage = {
          sender: 'bot',
          text: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  );

  const sendMessage = useCallback(async (message, source) => {
    if (!message.trim()) return;
    
    try {
      await sendMessageMutation.mutateAsync({ message, source });
    } catch (error) {
      // Error handling is done in onError
    }
  }, [sendMessageMutation]);

  const clearChat = useCallback(() => {
    setMessages([
      {
        sender: 'bot',
        text: "Hello! I'm your personal book assistant. I can help you find books, get recommendations, check prices, ratings, and availability. What would you like to know about books today?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    toast.success('Chat cleared');
  }, []);

  const newSession = useCallback(() => {
    setMessages([
      {
        sender: 'bot',
        text: 'New session started! How can I help you with books today?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    toast.success('New session started');
  }, []);

  return {
    messages,
    sendMessage,
    clearChat,
    newSession,
    isLoading: isLoading || sendMessageMutation.isLoading
  };
}


