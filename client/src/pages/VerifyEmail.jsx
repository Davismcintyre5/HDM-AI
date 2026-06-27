import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/ui/Card';
import Spinner from '../components/ui/Spinner';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const { verifyEmail } = useAuth();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No verification token provided.');
      return;
    }
    verifyEmail(token)
      .then((res) => {
        setStatus('success');
        setMessage(res.message || 'Email verified!');
      })
      .catch((err) => {
        setStatus('error');
        setMessage(err.response?.data?.error || 'Verification failed.');
      });
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <Card className="w-full max-w-sm text-center">
        {status === 'loading' && <Spinner size="lg" />}
        {status === 'success' && (
          <>
            <h1 className="text-2xl font-bold text-success mb-2">Verified!</h1>
            <p className="text-text-secondary text-sm mb-4">{message}</p>
            <Link to="/chat" className="text-primary hover:underline text-sm">Go to Chat</Link>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 className="text-2xl font-bold text-danger mb-2">Failed</h1>
            <p className="text-text-secondary text-sm mb-4">{message}</p>
            <Link to="/login" className="text-primary hover:underline text-sm">Back to login</Link>
          </>
        )}
      </Card>
    </div>
  );
}