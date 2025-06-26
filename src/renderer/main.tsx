import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';

// 创建深色主题，保持原有颜色方案
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#58a6ff', // GitHub蓝色
    },
    secondary: {
      main: '#f85149', // GitHub红色
    },
    background: {
      default: '#0d1117', // 主背景色
      paper: '#161b22', // 卡片背景色
    },
    text: {
      primary: '#e1e4e8',
      secondary: '#8b949e',
    },
    divider: '#30363d',
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: 13,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          overflow: 'hidden',
          '-webkit-font-smoothing': 'antialiased',
          '-moz-osx-font-smoothing': 'grayscale',
        },
      },
    },
  },
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);