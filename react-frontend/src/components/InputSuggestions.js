import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const SuggestionsContainer = styled(motion.div)`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const Suggestion = styled(motion.span)`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #666;
  user-select: none;
  
  &:hover {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
  }
`;

function InputSuggestions({ suggestions, onSuggestionClick }) {
  return (
    <SuggestionsContainer
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
    >
      {suggestions.map((suggestion, index) => (
        <Suggestion
          key={index}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onSuggestionClick(suggestion)}
        >
          {suggestion}
        </Suggestion>
      ))}
    </SuggestionsContainer>
  );
}

export default InputSuggestions;



