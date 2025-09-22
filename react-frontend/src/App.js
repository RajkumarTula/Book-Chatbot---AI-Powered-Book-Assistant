import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import BookModal from './components/BookModal';
import LoadingOverlay from './components/LoadingOverlay';
import { useChat } from './hooks/useChat';
import { useBooks } from './hooks/useBooks';
import { useAPI } from './hooks/useAPI';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.1);
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  min-height: 0;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const SidebarContainer = styled.div`
  width: 300px;
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
  overflow-y: auto;

  @media (max-width: 768px) {
    width: 100%;
    height: auto;
    max-height: 200px;
  }
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
`;

function App() {
  const [selectedBook, setSelectedBook] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [source, setSource] = useState('both');
  
  const { isOnline, checkAPIStatus } = useAPI();
  const { 
    messages, 
    sendMessage, 
    clearChat, 
    newSession, 
    isLoading: chatLoading 
  } = useChat();
  
  const { 
    featuredBooks, 
    loadFeaturedBooks, 
    getBookDetails 
  } = useBooks();

  useEffect(() => {
    // Check API status on mount
    checkAPIStatus();
    
    // Load featured books
    loadFeaturedBooks();
    
    // Check API status periodically
    const interval = setInterval(checkAPIStatus, 30000);
    
    return () => clearInterval(interval);
  }, [checkAPIStatus, loadFeaturedBooks]);

  const handleSendMessage = async (message) => {
    setIsLoading(true);
    try {
      await sendMessage(message, source);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBookClick = async (bookTitle) => {
    try {
      const bookDetails = await getBookDetails(bookTitle);
      setSelectedBook(bookDetails);
      setIsModalOpen(true);
    } catch (error) {
      console.error('Error fetching book details:', error);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedBook(null);
  };

  const handleQuickAction = (action) => {
    let message = '';
    
    switch (action) {
      case 'search':
        message = 'Search for books';
        break;
      case 'recommend':
        message = 'Recommend me some books';
        break;
      case 'bestsellers':
        message = 'Show me bestsellers';
        break;
      case 'new-releases':
        message = 'Show me new releases';
        break;
      case 'price':
        message = 'Check book prices';
        break;
      case 'rating':
        message = 'Check book ratings';
        break;
      default:
        return;
    }
    
    if (message) {
      handleSendMessage(message);
    }
  };

  return (
    <AppContainer>
      <Header 
        isOnline={isOnline}
        onClearChat={clearChat}
        onNewSession={newSession}
        source={source}
        onChangeSource={setSource}
      />
      
      <MainContent>
        <SidebarContainer>
          <Sidebar
            onQuickAction={handleQuickAction}
            featuredBooks={featuredBooks}
            onBookClick={handleBookClick}
          />
        </SidebarContainer>
        
        <ChatContainer>
          <ChatArea
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading || chatLoading}
            onBookClick={handleBookClick}
          />
        </ChatContainer>
      </MainContent>

      <AnimatePresence>
        {isModalOpen && selectedBook && (
          <BookModal
            book={selectedBook}
            onClose={handleCloseModal}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isLoading && (
          <LoadingOverlay />
        )}
      </AnimatePresence>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </AppContainer>
  );
}

export default App;


