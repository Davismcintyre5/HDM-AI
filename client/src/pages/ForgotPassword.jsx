import { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/auth/forgot-password', { email });
      setSent(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong.');
    }
    setLoading(false);
  };

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg p-4">
        <Card className="w-full max-w-sm text-center">
          <h1 className="text-2xl font-bold text-text-primary mb-2">Check Your Email</h1>
          <p className="text-text-secondary text-sm">If that email exists, we sent a reset link.</p>
          <Link to="/login" className="text-primary hover:underline text-sm mt-4 inline-block">Back to login</Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <Card className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-text-primary text-center mb-2">Reset Password</h1>
        <p className="text-text-muted text-center text-sm mb-6">Enter your email to receive a reset link.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" />
          {error && <p className="text-danger text-sm">{error}</p>}
          <Button type="submit" loading={loading} className="w-full">Send Reset Link</Button>
        </form>
        <p className="mt-4 text-center text-sm text-text-muted">
          <Link to="/login" className="text-primary hover:underline">Back to login</Link>
        </p>
      </Card>
    </div>
  );
}