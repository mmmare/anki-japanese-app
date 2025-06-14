import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import App from './App';

// Extend the theme with custom colors and other properties
const theme = extendTheme({
  colors: {
    brand: {
      50: '#e6f7ff',
      100: '#b3e0ff',
      200: '#80cbff',
      300: '#4db6ff',
      400: '#26a6ff',
      500: '#0096ff', // Primary color
      600: '#0078cc',
      700: '#005a99',
      800: '#003c66',
      900: '#001e33',
    },
    accent: {
      500: '#ff9f1c', // Japanese-inspired accent color
    },
  },
  fonts: {
    heading: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
    body: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: '#f7fafc',
        color: '#1a202c',
      },
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'semibold',
        borderRadius: 'md',
      },
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);