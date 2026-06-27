import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../components/ui/Toast';
import api from '../api/axios';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Modal from '../components/ui/Modal';
import Badge from '../components/ui/Badge';
import { Sun, Moon, Trash2, Key, Globe, Server, RefreshCw, Plus, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { formatDate } from '../utils/formatDate';

export default function Settings() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { addToast } = useToast();
  const [tab, setTab] = useState('profile');
  const [subtab, setSubtab] = useState('outbound');

  const [deleteModal, setDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);

  const [username, setUsername] = useState(user?.username || '');
  const [editingProfile, setEditingProfile] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);

  const [outboundKeys, setOutboundKeys] = useState([]);
  const [inboundKeys, setInboundKeys] = useState([]);
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyFull, setNewKeyFull] = useState(null);
  const [creating, setCreating] = useState(false);

  const [showInbound, setShowInbound] = useState(false);
  const [inboundForm, setInboundForm] = useState({ provider: 'erp', name: '', apiKey: '', baseUrl: '', apiStructure: '' });
  const [editingInbound, setEditingInbound] = useState(null);
  const [testingId, setTestingId] = useState(null);

  const loadOutbound = () => api.get('/keys/outbound').then(({ data }) => setOutboundKeys(data.data || [])).catch(() => {});
  const loadInbound = () => api.get('/keys/third-party').then(({ data }) => setInboundKeys(data.data || [])).catch(() => {});

  useState(() => { loadOutbound(); loadInbound(); }, []);

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      await api.put('/auth/profile', { username });
      addToast('Profile updated', 'success');
      setEditingProfile(false);
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed', 'error');
    }
    setSavingProfile(false);
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      return addToast('Passwords do not match', 'error');
    }
    setChangingPassword(true);
    try {
      await api.put('/auth/password', { currentPassword, newPassword });
      addToast('Password changed', 'success');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed', 'error');
    }
    setChangingPassword(false);
  };

  const handleCreateKey = async () => {
    setCreating(true);
    try {
      const { data } = await api.post('/keys/outbound', { project: 'general', name: newKeyName || 'My Key' });
      setNewKeyFull(data.data.fullKey);
      loadOutbound();
      addToast('Key created!', 'success');
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed', 'error');
    }
    setCreating(false);
  };

  const revokeKey = async (id) => {
    try { await api.delete(`/keys/outbound/${id}`); loadOutbound(); addToast('Key deleted.', 'info'); }
    catch { addToast('Failed', 'error'); }
  };

  const handleInboundSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = { provider: inboundForm.provider, name: inboundForm.name, apiKey: inboundForm.apiKey, baseUrl: inboundForm.baseUrl, apiStructure: inboundForm.apiStructure || undefined };
      if (editingInbound) {
        await api.put(`/keys/third-party/${editingInbound}`, payload);
        addToast('Key updated', 'success');
      } else {
        await api.post('/keys/third-party', payload);
        addToast('Key stored', 'success');
      }
      setShowInbound(false); setEditingInbound(null);
      setInboundForm({ provider: 'erp', name: '', apiKey: '', baseUrl: '', apiStructure: '' });
      loadInbound();
    } catch (err) { addToast(err.response?.data?.error || 'Failed', 'error'); }
  };

  const testInbound = async (id) => {
    setTestingId(id);
    try {
      const { data } = await api.post(`/keys/third-party/${id}/test`);
      addToast(data.data?.message || 'Test complete', data.data?.success ? 'success' : 'error');
      loadInbound();
    } catch { addToast('Test failed', 'error'); }
    setTestingId(null);
  };

  const deleteInbound = async (id) => {
    try { await api.delete(`/keys/third-party/${id}`); loadInbound(); addToast('Deleted', 'info'); }
    catch { addToast('Failed', 'error'); }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    try {
      await api.delete('/auth/account', { data: { password: deletePassword } });
      addToast('Account deleted.', 'info');
      logout();
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed', 'error');
    }
    setDeleting(false);
    setDeleteModal(false);
  };

  const tabs = [
    { id: 'profile', label: 'Profile' },
    { id: 'keys', label: 'API Keys' },
    { id: 'security', label: 'Security' },
  ];

  return (
    <div className="h-full flex">
      <div className="w-56 border-r border-border shrink-0 p-3 space-y-1">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${tab === t.id ? 'bg-primary/10 text-primary font-medium' : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'}`}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {tab === 'profile' && (
          <div className="max-w-lg space-y-6">
            <h1 className="text-2xl font-bold text-text-primary">Profile</h1>

            <Card>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-text-primary">Account Info</h2>
                {!editingProfile && <Button variant="ghost" size="sm" onClick={() => setEditingProfile(true)}>Edit</Button>}
              </div>
              {editingProfile ? (
                <div className="space-y-4">
                  <Input label="Username" value={username} onChange={e => setUsername(e.target.value)} />
                  <Input label="Email" value={user?.email || ''} disabled />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSaveProfile} loading={savingProfile}>Save</Button>
                    <Button variant="secondary" size="sm" onClick={() => { setEditingProfile(false); setUsername(user?.username || ''); }}>Cancel</Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between"><span className="text-text-secondary">Username</span><span className="text-text-primary">{user?.username || 'Not set'}</span></div>
                  <div className="flex justify-between"><span className="text-text-secondary">Email</span><span className="text-text-primary">{user?.email}</span></div>
                  <div className="flex justify-between"><span className="text-text-secondary">Role</span><Badge variant="primary">{user?.role || 'user'}</Badge></div>
                </div>
              )}
            </Card>

            <Card>
              <h2 className="font-semibold text-text-primary mb-4">Change Password</h2>
              <form onSubmit={handleChangePassword} className="space-y-3">
                <Input label="Current Password" type="password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} required />
                <Input label="New Password" type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
                <Input label="Confirm Password" type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
                <Button type="submit" size="sm" loading={changingPassword}>Change Password</Button>
              </form>
            </Card>

            <Card>
              <h2 className="font-semibold text-text-primary mb-4">Appearance</h2>
              <div className="flex items-center justify-between">
                <span className="text-text-secondary text-sm">Theme</span>
                <Button variant="secondary" size="sm" onClick={toggleTheme}>
                  {theme === 'dark' ? <Sun className="w-4 h-4 mr-1" /> : <Moon className="w-4 h-4 mr-1" />}
                  {theme === 'dark' ? 'Light' : 'Dark'}
                </Button>
              </div>
            </Card>
          </div>
        )}

        {tab === 'keys' && (
          <div className="max-w-2xl">
            <h1 className="text-2xl font-bold text-text-primary mb-6">API Keys</h1>

            <div className="flex gap-1 mb-6 bg-bg-tertiary rounded-lg p-1 w-fit">
              <button onClick={() => setSubtab('outbound')} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm ${subtab === 'outbound' ? 'bg-primary text-black' : 'text-text-secondary hover:text-text-primary'}`}><ArrowUpRight size={14} /> Outbound</button>
              <button onClick={() => setSubtab('inbound')} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm ${subtab === 'inbound' ? 'bg-primary text-black' : 'text-text-secondary hover:text-text-primary'}`}><ArrowDownRight size={14} /> Inbound</button>
            </div>

            {subtab === 'outbound' && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-text-secondary">Keys for apps to call HDM AI</p>
                  <Button size="sm" onClick={() => { setNewKeyFull(null); setNewKeyName(''); setShowCreateKey(true); }}><Plus className="w-4 h-4 mr-1" /> New Key</Button>
                </div>

                {newKeyFull && (
                  <Card className="mb-4 border-primary/30 bg-primary/5">
                    <p className="text-sm text-primary font-medium mb-3">⚠ Save your key — shown only once!</p>
                    <div className="bg-bg-tertiary rounded-lg p-3 font-mono text-sm text-text-primary break-all mb-3">{newKeyFull}</div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => { navigator.clipboard.writeText(newKeyFull); addToast('Copied!', 'success'); }}>Copy</Button>
                      <Button size="sm" variant="secondary" onClick={() => setNewKeyFull(null)}>Done</Button>
                    </div>
                  </Card>
                )}

                {showCreateKey && (
                  <Card className="mb-4">
                    <h3 className="text-sm font-medium text-text-primary mb-3">New Outbound Key</h3>
                    <Input value={newKeyName} onChange={e => setNewKeyName(e.target.value)} placeholder="Key name (e.g., My App)" className="mb-3" />
                    <p className="text-xs text-text-muted mb-3">Only General AI keys are available.</p>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={handleCreateKey} loading={creating}>Create</Button>
                      <Button size="sm" variant="secondary" onClick={() => setShowCreateKey(false)}>Cancel</Button>
                    </div>
                  </Card>
                )}

                <div className="space-y-3">
                  {outboundKeys.length === 0 && <Card className="text-center py-12 text-text-muted"><Key size={32} className="mx-auto mb-3 opacity-30" /><p>No outbound keys</p></Card>}
                  {outboundKeys.map(k => (
                    <Card key={k._id}>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2"><span className="font-mono text-sm text-text-primary">{k.keyPrefix}</span><Badge variant="primary">{k.project}</Badge></div>
                          <p className="text-xs text-text-muted mt-1">{k.name} • Created {formatDate(k.createdAt)}</p>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => revokeKey(k._id)}><Trash2 className="w-4 h-4" /></Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </>
            )}

            {subtab === 'inbound' && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-text-secondary">External keys HDM AI uses to fetch your data</p>
                  <Button size="sm" onClick={() => { setEditingInbound(null); setInboundForm({ provider: 'erp', name: '', apiKey: '', baseUrl: '', apiStructure: '' }); setShowInbound(true); }}><Plus className="w-4 h-4 mr-1" /> Add Key</Button>
                </div>

                {showInbound && (
                  <Card className="mb-4">
                    <h3 className="text-sm font-medium text-text-primary mb-4">{editingInbound ? 'Edit Key' : 'Add External Key'}</h3>
                    <form onSubmit={handleInboundSubmit} className="space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm text-text-secondary mb-1">Provider</label>
                          <select value={inboundForm.provider} onChange={e => setInboundForm({ ...inboundForm, provider: e.target.value })} className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-primary">
                            <option value="openai">OpenAI</option><option value="anthropic">Anthropic</option><option value="deepseek">DeepSeek</option><option value="google">Google</option><option value="erp">ERP System</option><option value="crm">CRM System</option><option value="database">Database</option><option value="custom">Custom API</option>
                          </select>
                        </div>
                        <Input label="Name" value={inboundForm.name} onChange={e => setInboundForm({ ...inboundForm, name: e.target.value })} required />
                      </div>
                      <Input label="API Key" type="password" value={inboundForm.apiKey} onChange={e => setInboundForm({ ...inboundForm, apiKey: e.target.value })} placeholder={editingInbound ? 'Leave blank to keep current' : 'sk-...'} required={!editingInbound} />
                      <Input label="Base URL" value={inboundForm.baseUrl} onChange={e => setInboundForm({ ...inboundForm, baseUrl: e.target.value })} placeholder="https://api.example.com" />
                      <div>
                        <label className="block text-sm text-text-secondary mb-1">API Structure (key:value per line)</label>
                        <textarea value={inboundForm.apiStructure} onChange={e => setInboundForm({ ...inboundForm, apiStructure: e.target.value })} placeholder="products: /inventory/products" className="w-full h-24 bg-bg-tertiary border border-border rounded-lg p-3 text-sm text-text-primary font-mono resize-none focus:outline-none focus:border-primary" />
                      </div>
                      <div className="flex gap-2">
                        <Button type="submit" size="sm">{editingInbound ? 'Update' : 'Store Key'}</Button>
                        <Button variant="secondary" size="sm" type="button" onClick={() => { setShowInbound(false); setEditingInbound(null); }}>Cancel</Button>
                      </div>
                    </form>
                  </Card>
                )}

                <div className="space-y-3">
                  {inboundKeys.length === 0 && <Card className="text-center py-12 text-text-muted"><Globe size={32} className="mx-auto mb-3 opacity-30" /><p>No external keys</p></Card>}
                  {inboundKeys.map(k => (
                    <Card key={k._id}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${k.isVerified ? 'bg-success' : 'bg-yellow-400'}`} />
                          <div>
                            <div className="flex items-center gap-2"><h4 className="text-sm font-medium text-text-primary">{k.name}</h4><Badge variant="muted">{k.provider}</Badge></div>
                            <p className="text-xs text-text-muted mt-0.5">{k.baseUrl}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button variant="ghost" size="sm" onClick={() => testInbound(k._id)} loading={testingId === k._id}><RefreshCw size={14} /></Button>
                          <Button variant="ghost" size="sm" onClick={() => { setEditingInbound(k._id); setInboundForm({ provider: k.provider, name: k.name, apiKey: '', baseUrl: k.baseUrl || '', apiStructure: '' }); setShowInbound(true); }}>✎</Button>
                          <Button variant="ghost" size="sm" onClick={() => deleteInbound(k._id)}><Trash2 size={14} /></Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {tab === 'security' && (
          <div className="max-w-lg space-y-6">
            <h1 className="text-2xl font-bold text-text-primary">Security</h1>
            <Card className="border-danger/30">
              <h2 className="font-semibold text-danger mb-2">Danger Zone</h2>
              <p className="text-text-muted text-sm mb-4">Permanently delete your account and all data.</p>
              <Button variant="danger" size="sm" onClick={() => setDeleteModal(true)}><Trash2 className="w-4 h-4 mr-1" /> Delete Account</Button>
            </Card>

            <Modal open={deleteModal} onClose={() => setDeleteModal(false)} title="Delete Account">
              <p className="text-sm text-text-secondary mb-4">This action is permanent. All your data, conversations, and keys will be deleted.</p>
              <Input label="Enter your password to confirm" type="password" value={deletePassword} onChange={e => setDeletePassword(e.target.value)} placeholder="••••••••" className="mb-4" />
              <div className="flex gap-2">
                <Button variant="danger" size="sm" onClick={handleDeleteAccount} loading={deleting} disabled={!deletePassword}>Delete Forever</Button>
                <Button variant="secondary" size="sm" onClick={() => setDeleteModal(false)}>Cancel</Button>
              </div>
            </Modal>
          </div>
        )}
      </div>
    </div>
  );
}