import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function Register() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const res = await register(email, username, password);
      setSuccess(res.message || 'Check your email to verify your account.');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed.');
    }
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg p-4">
        <Card className="w-full max-w-sm text-center">
          <h1 className="text-2xl font-bold text-text-primary mb-2">Check Your Email</h1>
          <p className="text-text-secondary text-sm">{success}</p>
          <Link to="/login" className="text-primary hover:underline text-sm mt-4 inline-block">Back to login</Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <Card className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-text-primary text-center mb-2">Create Account</h1>
        <p className="text-text-muted text-center text-sm mb-6">Join HDM AI</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" />
          <Input label="Username" value={username} onChange={(e) => setUsername(e.target.value)} required placeholder="Your name" />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
          {error && <p className="text-danger text-sm">{error}</p>}
          <Button type="submit" loading={loading} className="w-full">Create Account</Button>
        </form>
        <p className="mt-4 text-center text-sm text-text-muted">
          Already have an account? <Link to="/login" className="text-primary hover:underline">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}