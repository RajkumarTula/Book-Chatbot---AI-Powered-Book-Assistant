import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaBookOpen, FaTrash, FaPlus, FaCircle, FaSun, FaMoon } from 'react-icons/fa';
import { useTheme } from '../hooks/useTheme';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, ${props => props.theme.surface} 0%, ${props => props.theme.surfaceSecondary} 100%);
  color: ${props => props.theme.text};
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid ${props => props.theme.border};
  transition: all 0.3s ease;
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
  color: ${props => props.theme.accent};
`;

const LogoText = styled.h1`
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  color: ${props => props.theme.text};
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
  color: ${props => props.theme.textSecondary};
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
  background: ${props => props.theme.buttonPrimary};
  color: ${props => props.theme.userText};

  &:hover {
    background: ${props => props.theme.accentSecondary};
    transform: translateY(-2px);
  }
`;

const SecondaryButton = styled(Button)`
  background: ${props => props.theme.buttonSecondary};
  color: ${props => props.theme.text};
  border: 1px solid ${props => props.theme.border};

  &:hover {
    background: ${props => props.theme.surface};
  }
`;

const ThemeToggleButton = styled(Button)`
  background: ${props => props.theme.surface};
  color: ${props => props.theme.text};
  border: 1px solid ${props => props.theme.border};
  padding: 0.5rem;

  &:hover {
    background: ${props => props.theme.surfaceSecondary};
  }
`;

const SourceSelect = styled.select`
  background: ${props => props.theme.inputBg};
  color: ${props => props.theme.text};
  border: 1px solid ${props => props.theme.inputBorder};
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-weight: 500;
  outline: none;
  cursor: pointer;
  backdrop-filter: blur(4px);

  option {
    color: ${props => props.theme.userText};
    background: ${props => props.theme.surface};
  }
`;

function Header({ isOnline, onClearChat, onNewSession, source, onChangeSource }) {
  const { theme, isDark, toggleTheme } = useTheme();

  return (
    <HeaderContainer theme={theme}>
      <HeaderContent>
        <Logo>
          <LogoIcon theme={theme} />
          <LogoText theme={theme}>BookBot</LogoText>
        </Logo>

        <HeaderActions>
          <StatusIndicator theme={theme}>
            <StatusDot isOnline={isOnline} />
            <span>{isOnline ? 'Online' : 'Offline'}</span>
          </StatusIndicator>

          <SourceSelect theme={theme} value={source} onChange={(e) => onChangeSource?.(e.target.value)}>
            <option value="dataset">Dataset</option>
            <option value="google">Internet</option>
            <option value="both">Both</option>
          </SourceSelect>

          <ThemeToggleButton
            theme={theme}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleTheme}
            title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            {isDark ? <FaSun /> : <FaMoon />}
          </ThemeToggleButton>

          <SecondaryButton
            theme={theme}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClearChat}
          >
            <FaTrash />
            Clear Chat
          </SecondaryButton>

          <PrimaryButton
            theme={theme}
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


