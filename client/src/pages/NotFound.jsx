import { Link } from 'react-router-dom';
import Card from '../components/ui/Card';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <Card className="w-full max-w-sm text-center">
        <h1 className="text-4xl font-bold text-text-primary mb-2">404</h1>
        <p className="text-text-secondary mb-4">Page not found.</p>
        <Link to="/chat" className="text-primary hover:underline text-sm">Go to Chat</Link>
      </Card>
    </div>
  );
}