import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FaPaperPlane, FaUser, FaRobot } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import Message from './Message';
import InputSuggestions from './InputSuggestions';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
`;

const ChatHeader = styled.div`
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #f6f9ff 0%, #fff 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ChatTitle = styled.h2`
  color: #333;
  font-weight: 600;
  margin: 0;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28a745;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background: linear-gradient(180deg, #f8f9ff 0%, #f8f9fa 100%);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const InputArea = styled.div`
  padding: 1.5rem 2rem;
  background: linear-gradient(180deg, #ffffff 0%, #f9f9ff 100%);
  border-top: 1px solid #e9ecef;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 1rem;
  align-items: flex-end;
`;

const InputField = styled.textarea`
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  resize: none;
  min-height: 50px;
  max-height: 120px;
  font-family: inherit;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #999;
  }
`;

const SendButton = styled(motion.button)`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
  
  &:hover:not(:disabled) {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const suggestions = [
  "Find books by Stephen King",
  "What are the best fantasy books?",
  "Show me bestsellers",
  "How much does Harry Potter cost?",
  "Recommend me some mystery novels",
  "What are the new releases?",
  "Compare The Great Gatsby and 1984",
  "Tell me about The Hobbit"
];

function ChatArea({ messages, onSendMessage, isLoading, onBookClick }) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = inputRef.current.scrollHeight + 'px';
    }
  }, [inputValue]);

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      setShowSuggestions(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const handleInputFocus = () => {
    setShowSuggestions(true);
  };

  const handleInputBlur = () => {
    // Delay hiding suggestions to allow clicking on them
    setTimeout(() => setShowSuggestions(false), 200);
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>Chat with BookBot</ChatTitle>
        <StatusIndicator>
          <StatusDot />
          <span>Online</span>
        </StatusIndicator>
      </ChatHeader>

      <MessagesContainer>
        <AnimatePresence>
          {messages.map((message, index) => (
            <Message
              key={index}
              message={message}
              onBookClick={onBookClick}
            />
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputArea>
        <InputContainer>
          <InputField
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={handleInputFocus}
            onBlur={handleInputBlur}
            placeholder="Ask me about books..."
            disabled={isLoading}
          />
          <SendButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
          >
            <FaPaperPlane />
          </SendButton>
        </InputContainer>

        <AnimatePresence>
          {showSuggestions && (
            <InputSuggestions
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
            />
          )}
        </AnimatePresence>
      </InputArea>
    </ChatContainer>
  );
}

export default ChatArea;


