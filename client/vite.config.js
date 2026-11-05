import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import prerenderStatic from 'vite-plugin-prerender-static';

const staticRoutes = [
  {
    path: '/login',
    tags: {
      title: 'Login — HDM AI',
      description: 'Sign in to HDM AI, the Central Intelligence Platform with 7 AI services.',
    },
  },
  {
    path: '/register',
    tags: {
      title: 'Create Account — HDM AI',
      description: 'Create your HDM AI account and access AI chat, code, image, and analysis tools.',
    },
  },
  {
    path: '/forgot-password',
    tags: {
      title: 'Reset Password — HDM AI',
      description: 'Reset your HDM AI account password.',
    },
  },
];

export default defineConfig({
  plugins: [
    react(),
    prerenderStatic({
      routes: staticRoutes,
      render: () => '<div id="root"></div>',
    }),
  ],
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});