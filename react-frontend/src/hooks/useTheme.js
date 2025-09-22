import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? JSON.parse(saved) : true; // Default to dark
  });

  useEffect(() => {
    localStorage.setItem('theme', JSON.stringify(isDark));
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const theme = {
    isDark,
    colors: {
      // Dark theme
      dark: {
        background: '#0f0f23',
        surface: '#1a1a2e',
        surfaceSecondary: '#16213e',
        border: '#2a2a4e',
        text: '#ffffff',
        textSecondary: '#b0b0b0',
        accent: '#00d4ff',
        accentSecondary: '#0099cc',
        userMessage: '#00d4ff',
        userText: '#0f0f23',
        botMessage: '#1a1a2e',
        botText: '#ffffff',
        inputBg: '#1a1a2e',
        inputBorder: '#2a2a4e',
        inputFocus: '#00d4ff',
        buttonPrimary: '#00d4ff',
        buttonSecondary: '#2a2a4e',
        link: '#00d4ff',
        price: '#00d4ff',
        star: '#00d4ff',
        starEmpty: '#555',
      },
      // Light theme
      light: {
        background: '#ffffff',
        surface: '#f8f9fa',
        surfaceSecondary: '#ffffff',
        border: '#e9ecef',
        text: '#333333',
        textSecondary: '#666666',
        accent: '#667eea',
        accentSecondary: '#764ba2',
        userMessage: '#667eea',
        userText: '#ffffff',
        botMessage: '#ffffff',
        botText: '#333333',
        inputBg: '#ffffff',
        inputBorder: '#e9ecef',
        inputFocus: '#667eea',
        buttonPrimary: '#ffd700',
        buttonSecondary: '#f8f9fa',
        link: '#667eea',
        price: '#28a745',
        star: '#ffd700',
        starEmpty: '#ddd',
      }
    }
  };

  return (
    <ThemeContext.Provider value={{ theme: theme.colors[isDark ? 'dark' : 'light'], isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};