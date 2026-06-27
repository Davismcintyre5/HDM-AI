import { useState, useEffect } from 'react';
import api from '../api/axios';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Modal from '../components/ui/Modal';
import Badge from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import { useToast } from '../components/ui/Toast';
import { Key, Copy, Trash2, Plus } from 'lucide-react';
import { formatDate } from '../utils/formatDate';

export default function Keys() {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState(null);
  const { addToast } = useToast();

  const fetchKeys = () => {
    api.get('/keys/outbound').then(({ data }) => setKeys(data.data || [])).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { fetchKeys(); }, []);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const { data } = await api.post('/keys/outbound', { project: 'general', name: newName || 'My Key' });
      setNewKey(data.data.fullKey);
      fetchKeys();
      addToast('Key created!', 'success');
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed', 'error');
    }
    setCreating(false);
  };

  const handleRevoke = async (id) => {
    try {
      await api.delete(`/keys/outbound/${id}`);
      fetchKeys();
      addToast('Key deleted.', 'info');
    } catch {
      addToast('Failed to delete key.', 'error');
    }
  };

  const copyKey = (key) => {
    navigator.clipboard.writeText(key);
    addToast('Copied!', 'success');
  };

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2"><Key size={20} className="text-primary" /> API Keys</h1>
        <Button size="sm" onClick={() => { setNewKey(null); setNewName(''); setModalOpen(true); }}><Plus className="w-4 h-4 mr-1" /> New Key</Button>
      </div>

      {keys.length === 0 && (
        <Card className="text-center text-text-muted py-12">
          <Key className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No API keys yet. Create one to connect your apps.</p>
        </Card>
      )}

      {keys.map(k => (
        <Card key={k._id} className="mb-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm text-text-primary">{k.keyPrefix}</span>
                <Badge variant="primary">{k.project}</Badge>
              </div>
              <p className="text-xs text-text-muted mt-1">Created {formatDate(k.createdAt)}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => handleRevoke(k._id)}><Trash2 className="w-4 h-4" /></Button>
          </div>
        </Card>
      ))}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={newKey ? 'Key Created!' : 'Create API Key'}>
        {newKey ? (
          <div className="space-y-4">
            <div className="bg-bg-tertiary rounded-lg p-3 font-mono text-sm text-text-primary break-all">{newKey}</div>
            <p className="text-xs text-danger">Save this key now — it won't be shown again.</p>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => copyKey(newKey)}><Copy className="w-4 h-4 mr-1" /> Copy</Button>
              <Button size="sm" variant="secondary" onClick={() => setModalOpen(false)}>Done</Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <Input label="Key Name" value={newName} onChange={e => setNewName(e.target.value)} placeholder="My App" />
            <p className="text-xs text-text-muted">Only General AI keys are available.</p>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleCreate} loading={creating}>Create</Button>
              <Button size="sm" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}