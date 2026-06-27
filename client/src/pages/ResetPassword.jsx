import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../api/axios';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [password, setPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/auth/reset-password', { token, password });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Reset failed.');
    }
    setLoading(false);
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg p-4">
        <Card className="w-full max-w-sm text-center">
          <h1 className="text-2xl font-bold text-danger mb-2">Invalid Link</h1>
          <p className="text-text-secondary text-sm">No reset token provided.</p>
          <Link to="/forgot-password" className="text-primary hover:underline text-sm mt-4 inline-block">Request new link</Link>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg p-4">
        <Card className="w-full max-w-sm text-center">
          <h1 className="text-2xl font-bold text-success mb-2">Password Reset!</h1>
          <p className="text-text-secondary text-sm">You can now sign in with your new password.</p>
          <Link to="/login" className="text-primary hover:underline text-sm mt-4 inline-block">Sign in</Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <Card className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-text-primary text-center mb-2">New Password</h1>
        <p className="text-text-muted text-center text-sm mb-6">Choose a new password.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="New Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
          {error && <p className="text-danger text-sm">{error}</p>}
          <Button type="submit" loading={loading} className="w-full">Reset Password</Button>
        </form>
      </Card>
    </div>
  );
}