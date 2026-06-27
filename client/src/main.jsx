import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

const future = { v7_startTransition: true, v7_relativeSplatPath: true };

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter future={future}>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);