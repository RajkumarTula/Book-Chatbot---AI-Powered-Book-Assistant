import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaUser, FaRobot } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

const MessageContainer = styled(motion.div)`
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  
  &.user-message {
    flex-direction: row-reverse;
  }
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
  background: ${props => props.isUser 
    ? '#ffd700' 
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  };
  color: ${props => props.isUser ? '#333' : 'white'};
`;

const MessageContent = styled.div`
  flex: 1;
  max-width: 70%;
  
  .user-message & {
    text-align: right;
  }
`;

const MessageText = styled.div`
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
  
  .user-message & {
    background: #667eea;
    color: white;
  }
  
  /* Markdown styling */
  h1, h2, h3, h4, h5, h6 {
    margin: 0.5rem 0;
    color: inherit;
  }
  
  p {
    margin: 0.5rem 0;
    color: inherit;
  }
  
  strong {
    font-weight: 600;
    color: inherit;
  }
  
  em {
    font-style: italic;
    color: inherit;
  }
  
  ul, ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
    color: inherit;
  }
  
  li {
    margin: 0.25rem 0;
    color: inherit;
  }
  
  a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
    cursor: pointer;
    
    &:hover {
      text-decoration: underline;
    }
    
    .user-message & {
      color: #ffd700;
    }
  }
  
  code {
    background: rgba(0, 0, 0, 0.1);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
  }
  
  pre {
    background: rgba(0, 0, 0, 0.1);
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 0.5rem 0;
  }
  
  blockquote {
    border-left: 4px solid #667eea;
    padding-left: 1rem;
    margin: 0.5rem 0;
    font-style: italic;
    color: #666;
  }
`;

const MessageTime = styled.div`
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
  
  .user-message & {
    text-align: right;
  }
`;

const BookLink = styled.span`
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 1px dotted #667eea;
  
  &:hover {
    text-decoration: underline;
    border-bottom: 1px solid #667eea;
  }
  
  .user-message & {
    color: #ffd700;
    border-bottom-color: #ffd700;
    
    &:hover {
      border-bottom-color: #ffd700;
    }
  }
`;

const PriceHighlight = styled.span`
  background: #28a745;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.9em;
`;

const StarRating = styled.div`
  display: inline-flex;
  gap: 0.1rem;
  align-items: center;
  margin: 0.25rem 0;
`;

const Star = styled.span`
  color: #ffd700;
  font-size: 0.9rem;
  
  &.empty {
    color: #ddd;
  }
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-style: italic;
`;

const TypingDots = styled.div`
  display: flex;
  gap: 0.25rem;
`;

const TypingDot = styled.span`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #666;
  animation: typing 1.4s infinite;
  
  &:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  &:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
      opacity: 0.5;
    }
    30% {
      transform: translateY(-10px);
      opacity: 1;
    }
  }
`;

function Message({ message, onBookClick }) {
  const isUser = message.sender === 'user';
  const isTyping = message.isTyping;

  const formatMessage = (text) => {
    if (!text) return '';
    
    // Convert book titles to clickable links
    let formatted = text.replace(/\*\*([^*]+)\*\*/g, (match, title) => {
      return `<span class="book-link" onclick="window.handleBookClick('${title}')">${title}</span>`;
    });
    
    // Convert price patterns
    formatted = formatted.replace(/\$(\d+(?:\.\d+)?)/g, '<span class="price-highlight">$$$1</span>');
    
    // Convert rating patterns
    formatted = formatted.replace(/(\d+(?:\.\d+)?)\/5/g, (match, rating) => {
      return createStarRating(parseFloat(rating));
    });
    
    return formatted;
  };

  const createStarRating = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    let stars = '';
    for (let i = 0; i < fullStars; i++) {
      stars += '<span class="star">★</span>';
    }
    if (hasHalfStar) {
      stars += '<span class="star">☆</span>';
    }
    for (let i = 0; i < emptyStars; i++) {
      stars += '<span class="star empty">☆</span>';
    }

    return `<span class="star-rating">${stars}</span>`;
  };

  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Make book click handler available globally
  React.useEffect(() => {
    window.handleBookClick = onBookClick;
    return () => {
      delete window.handleBookClick;
    };
  }, [onBookClick]);

  if (isTyping) {
    return (
      <MessageContainer
        className={isUser ? 'user-message' : 'bot-message'}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Avatar isUser={isUser}>
          {isUser ? <FaUser /> : <FaRobot />}
        </Avatar>
        <MessageContent>
          <MessageText>
            <TypingIndicator>
              <span>Typing</span>
              <TypingDots>
                <TypingDot />
                <TypingDot />
                <TypingDot />
              </TypingDots>
            </TypingIndicator>
          </MessageText>
        </MessageContent>
      </MessageContainer>
    );
  }

  return (
    <MessageContainer
      className={isUser ? 'user-message' : 'bot-message'}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Avatar isUser={isUser}>
        {isUser ? <FaUser /> : <FaRobot />}
      </Avatar>
      <MessageContent>
        <MessageText>
          <ReactMarkdown
            components={{
              span: ({ children, ...props }) => {
                if (props.className === 'book-link') {
                  return (
                    <BookLink onClick={() => onBookClick(children)}>
                      {children}
                    </BookLink>
                  );
                }
                if (props.className === 'price-highlight') {
                  return <PriceHighlight>{children}</PriceHighlight>;
                }
                if (props.className === 'star-rating') {
                  return <StarRating dangerouslySetInnerHTML={{ __html: children }} />;
                }
                return <span {...props}>{children}</span>;
              }
            }}
          >
            {message.text}
          </ReactMarkdown>
        </MessageText>
        <MessageTime>
          {message.timestamp || getCurrentTime()}
        </MessageTime>
      </MessageContent>
    </MessageContainer>
  );
}

export default Message;



