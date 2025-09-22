import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaBookOpen, FaTrash, FaPlus, FaCircle } from 'react-icons/fa';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const LogoIcon = styled(FaBookOpen)`
  font-size: 2rem;
  color: #ffd700;
`;

const LogoText = styled.h1`
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  margin-right: 1rem;
`;

const StatusDot = styled(FaCircle)`
  color: ${props => props.isOnline ? '#28a745' : '#dc3545'};
  font-size: 0.8rem;
  animation: ${props => props.isOnline ? 'pulse 2s infinite' : 'none'};
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const Button = styled(motion.button)`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;
`;

const PrimaryButton = styled(Button)`
  background: #ffd700;
  color: #333;
  
  &:hover {
    background: #ffed4e;
    transform: translateY(-2px);
  }
`;

const SecondaryButton = styled(Button)`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const SourceSelect = styled.select`
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-weight: 500;
  outline: none;
  cursor: pointer;
  backdrop-filter: blur(4px);

  option {
    color: #333;
  }
`;

function Header({ isOnline, onClearChat, onNewSession, source, onChangeSource }) {
  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo>
          <LogoIcon />
          <LogoText>BookBot</LogoText>
        </Logo>
        
        <HeaderActions>
          <StatusIndicator>
            <StatusDot isOnline={isOnline} />
            <span>{isOnline ? 'Online' : 'Offline'}</span>
          </StatusIndicator>

          <SourceSelect value={source} onChange={(e) => onChangeSource?.(e.target.value)}>
            <option value="dataset">Dataset</option>
            <option value="google">Internet</option>
            <option value="both">Both</option>
          </SourceSelect>
          
          <SecondaryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClearChat}
          >
            <FaTrash />
            Clear Chat
          </SecondaryButton>
          
          <PrimaryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onNewSession}
          >
            <FaPlus />
            New Session
          </PrimaryButton>
        </HeaderActions>
      </HeaderContent>
    </HeaderContainer>
  );
}

export default Header;


