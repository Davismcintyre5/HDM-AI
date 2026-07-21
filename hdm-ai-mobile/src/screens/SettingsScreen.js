import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, TextInput, StyleSheet, FlatList } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import api from '../api/axios';
import ScreenWrapper from '../components/ui/ScreenWrapper';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import { useToast } from '../components/ui/Toast';
import { Sun, Moon, Trash2, LogOut, Key, Plus, Copy, Globe, Server, RefreshCw, ArrowUpRight, ArrowDownRight } from 'lucide-react-native';

export default function SettingsScreen() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme, colors } = useTheme();
  const { addToast } = useToast();

  const [tab, setTab] = useState('profile');
  const [subtab, setSubtab] = useState('outbound');

  // Profile
  const [username, setUsername] = useState(user?.username || '');
  const [editingProfile, setEditingProfile] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);

  // Password
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);

  // Delete
  const [deleteModal, setDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);

  // Outbound keys
  const [outboundKeys, setOutboundKeys] = useState([]);
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyFull, setNewKeyFull] = useState(null);
  const [creating, setCreating] = useState(false);

  // Inbound keys
  const [inboundKeys, setInboundKeys] = useState([]);
  const [showInbound, setShowInbound] = useState(false);
  const [inboundForm, setInboundForm] = useState({ provider: 'erp', name: '', apiKey: '', baseUrl: '', apiStructure: '' });
  const [editingInbound, setEditingInbound] = useState(null);
  const [testingId, setTestingId] = useState(null);

  useEffect(() => {
    loadOutbound();
    loadInbound();
  }, []);

  const loadOutbound = async () => {
    try { const { data } = await api.get('/keys/outbound'); setOutboundKeys(data.data || []); } catch {}
  };

  const loadInbound = async () => {
    try { const { data } = await api.get('/keys/third-party'); setInboundKeys(data.data || []); } catch {}
  };

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      await api.put('/auth/profile', { username });
      addToast('Profile updated', 'success');
      setEditingProfile(false);
    } catch (err) { addToast(err.response?.data?.error || 'Failed', 'error'); }
    setSavingProfile(false);
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) return addToast('Passwords do not match', 'error');
    setChangingPassword(true);
    try {
      await api.put('/auth/password', { currentPassword, newPassword });
      addToast('Password changed', 'success');
      setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
    } catch (err) { addToast(err.response?.data?.error || 'Failed', 'error'); }
    setChangingPassword(false);
  };

  const handleCreateKey = async () => {
    setCreating(true);
    try {
      const { data } = await api.post('/keys/outbound', { project: 'general', name: newKeyName || 'My Key' });
      setNewKeyFull(data.data.fullKey);
      loadOutbound();
      addToast('Key created!', 'success');
    } catch (err) { addToast(err.response?.data?.error || 'Failed', 'error'); }
    setCreating(false);
  };

  const revokeKey = async (id) => {
    try { await api.delete(`/keys/outbound/${id}`); loadOutbound(); addToast('Key deleted', 'info'); }
    catch { addToast('Failed', 'error'); }
  };

  const copyKey = (text) => {
    addToast('Copied!', 'success');
  };

  const handleInboundSubmit = async () => {
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
    } catch (err) { addToast(err.response?.data?.error || 'Failed', 'error'); }
    setDeleting(false); setDeleteModal(false);
  };

  const tabs = [
    { id: 'profile', label: 'Profile' },
    { id: 'keys', label: 'API Keys' },
    { id: 'security', label: 'Security' },
  ];

  const renderTab = () => {
    switch (tab) {
      case 'profile':
        return (
          <View>
            <Card>
              <View style={styles.cardHeader}>
                <Text style={[styles.sectionTitle, { color: colors.text }]}>Account</Text>
                {!editingProfile && <Button variant="ghost" size="sm" onPress={() => setEditingProfile(true)}><Text style={{ color: colors.accent }}>Edit</Text></Button>}
              </View>
              {editingProfile ? (
                <View style={styles.form}>
                  <Input label="Username" value={username} onChangeText={setUsername} />
                  <Input label="Email" value={user?.email || ''} editable={false} />
                  <View style={styles.formBtns}>
                    <Button size="sm" onPress={handleSaveProfile} loading={savingProfile}>Save</Button>
                    <Button variant="secondary" size="sm" onPress={() => { setEditingProfile(false); setUsername(user?.username || ''); }}>Cancel</Button>
                  </View>
                </View>
              ) : (
                <View>
                  <View style={styles.row}><Text style={[styles.label, { color: colors.textSecondary }]}>Username</Text><Text style={[styles.value, { color: colors.text }]}>{user?.username || 'Not set'}</Text></View>
                  <View style={styles.row}><Text style={[styles.label, { color: colors.textSecondary }]}>Email</Text><Text style={[styles.value, { color: colors.text }]}>{user?.email}</Text></View>
                  <View style={styles.row}><Text style={[styles.label, { color: colors.textSecondary }]}>Role</Text><Badge variant="primary">{user?.role || 'user'}</Badge></View>
                </View>
              )}
            </Card>

            <Card>
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Change Password</Text>
              <View style={styles.form}>
                <Input label="Current Password" value={currentPassword} onChangeText={setCurrentPassword} secureTextEntry />
                <Input label="New Password" value={newPassword} onChangeText={setNewPassword} secureTextEntry />
                <Input label="Confirm Password" value={confirmPassword} onChangeText={setConfirmPassword} secureTextEntry />
                <Button size="sm" onPress={handleChangePassword} loading={changingPassword}>Change Password</Button>
              </View>
            </Card>

            <Card>
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Appearance</Text>
              <View style={styles.row}>
                <Text style={[styles.label, { color: colors.textSecondary }]}>Theme</Text>
                <Button variant="secondary" size="sm" onPress={toggleTheme}>
                  {theme === 'dark' ? <Sun size={16} color={colors.textSecondary} /> : <Moon size={16} color={colors.textSecondary} />}
                  <Text style={{ color: colors.textSecondary, marginLeft: 6 }}>{theme === 'dark' ? 'Light' : 'Dark'}</Text>
                </Button>
              </View>
            </Card>
          </View>
        );

      case 'keys':
        return (
          <View>
            <View style={styles.subtabs}>
              <TouchableOpacity onPress={() => setSubtab('outbound')} style={[styles.subtab, { backgroundColor: subtab === 'outbound' ? colors.accent : colors.bgTertiary }]}>
                <ArrowUpRight size={14} color={subtab === 'outbound' ? '#000' : colors.textSecondary} />
                <Text style={[styles.subtabText, { color: subtab === 'outbound' ? '#000' : colors.textSecondary }]}>Outbound</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => setSubtab('inbound')} style={[styles.subtab, { backgroundColor: subtab === 'inbound' ? colors.accent : colors.bgTertiary }]}>
                <ArrowDownRight size={14} color={subtab === 'inbound' ? '#000' : colors.textSecondary} />
                <Text style={[styles.subtabText, { color: subtab === 'inbound' ? '#000' : colors.textSecondary }]}>Inbound</Text>
              </TouchableOpacity>
            </View>

            {subtab === 'outbound' && (
              <View>
                <View style={styles.cardHeader}>
                  <Text style={[styles.smallLabel, { color: colors.textSecondary }]}>Keys for apps to call HDM AI</Text>
                  <Button size="sm" onPress={() => { setNewKeyFull(null); setNewKeyName(''); setShowCreateKey(true); }}>
                    <Plus size={14} color="#000" /> New Key
                  </Button>
                </View>

                {newKeyFull && (
                  <Card style={{ borderColor: colors.accent }}>
                    <Text style={[styles.warningText, { color: colors.accent }]}>⚠ Save your key — shown only once!</Text>
                    <Text style={[styles.keyText, { color: colors.text }]} selectable>{newKeyFull}</Text>
                    <View style={styles.formBtns}>
                      <Button size="sm" onPress={() => copyKey(newKeyFull)}><Copy size={14} color="#000" /> Copy</Button>
                      <Button variant="secondary" size="sm" onPress={() => setNewKeyFull(null)}>Done</Button>
                    </View>
                  </Card>
                )}

                {showCreateKey && (
                  <Card>
                    <Text style={[styles.sectionTitle, { color: colors.text }]}>New Outbound Key</Text>
                    <Input value={newKeyName} onChangeText={setNewKeyName} placeholder="Key name" />
                    <Text style={[styles.smallLabel, { color: colors.textMuted }]}>Only General AI keys available.</Text>
                    <View style={styles.formBtns}>
                      <Button size="sm" onPress={handleCreateKey} loading={creating}>Create</Button>
                      <Button variant="secondary" size="sm" onPress={() => setShowCreateKey(false)}>Cancel</Button>
                    </View>
                  </Card>
                )}

                {outboundKeys.length === 0 && !showCreateKey && (
                  <Card><Text style={[styles.emptyText, { color: colors.textMuted }]}>No outbound keys</Text></Card>
                )}
                {outboundKeys.map(k => (
                  <Card key={k._id}>
                    <View style={styles.row}>
                      <View style={{ flex: 1 }}>
                        <Text style={[styles.keyPrefix, { color: colors.text }]}>{k.keyPrefix}</Text>
                        <Text style={[styles.smallLabel, { color: colors.textMuted }]}>{k.name} • {k.project}</Text>
                      </View>
                      <Button variant="ghost" size="sm" onPress={() => revokeKey(k._id)}><Trash2 size={14} color={colors.danger} /></Button>
                    </View>
                  </Card>
                ))}
              </View>
            )}

            {subtab === 'inbound' && (
              <View>
                <View style={styles.cardHeader}>
                  <Text style={[styles.smallLabel, { color: colors.textSecondary }]}>External keys HDM AI uses</Text>
                  <Button size="sm" onPress={() => { setEditingInbound(null); setInboundForm({ provider: 'erp', name: '', apiKey: '', baseUrl: '', apiStructure: '' }); setShowInbound(true); }}>
                    <Plus size={14} color="#000" /> Add Key
                  </Button>
                </View>

                {showInbound && (
                  <Card>
                    <Text style={[styles.sectionTitle, { color: colors.text }]}>{editingInbound ? 'Edit Key' : 'Add External Key'}</Text>
                    <View style={styles.form}>
                      <View style={styles.inlineRow}>
                        <View style={{ flex: 1 }}>
                          <Text style={[styles.label, { color: colors.textSecondary }]}>Provider</Text>
                          <TouchableOpacity style={[styles.picker, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
                            <Text style={{ color: colors.text }}>{inboundForm.provider}</Text>
                          </TouchableOpacity>
                        </View>
                        <View style={{ flex: 1 }}>
                          <Input label="Name" value={inboundForm.name} onChangeText={t => setInboundForm({ ...inboundForm, name: t })} />
                        </View>
                      </View>
                      <Input label="API Key" value={inboundForm.apiKey} onChangeText={t => setInboundForm({ ...inboundForm, apiKey: t })} secureTextEntry placeholder={editingInbound ? 'Leave blank to keep' : 'sk-...'} />
                      <Input label="Base URL" value={inboundForm.baseUrl} onChangeText={t => setInboundForm({ ...inboundForm, baseUrl: t })} placeholder="https://api.example.com" />
                      <Input label="API Structure (key:value per line)" value={inboundForm.apiStructure} onChangeText={t => setInboundForm({ ...inboundForm, apiStructure: t })} multiline placeholder="products: /inventory/products" />
                      <View style={styles.formBtns}>
                        <Button size="sm" onPress={handleInboundSubmit}>{editingInbound ? 'Update' : 'Store Key'}</Button>
                        <Button variant="secondary" size="sm" onPress={() => { setShowInbound(false); setEditingInbound(null); }}>Cancel</Button>
                      </View>
                    </View>
                  </Card>
                )}

                {inboundKeys.length === 0 && !showInbound && (
                  <Card><Text style={[styles.emptyText, { color: colors.textMuted }]}>No external keys</Text></Card>
                )}
                {inboundKeys.map(k => (
                  <Card key={k._id}>
                    <View style={styles.row}>
                      <View style={{ flex: 1 }}>
                        <View style={styles.inlineRow}>
                          <View style={[styles.statusDot, { backgroundColor: k.isVerified ? colors.success : '#facc15' }]} />
                          <Text style={[styles.value, { color: colors.text }]}>{k.name}</Text>
                          <Badge variant="muted">{k.provider}</Badge>
                        </View>
                        {k.baseUrl ? <Text style={[styles.smallLabel, { color: colors.textMuted }]}>{k.baseUrl}</Text> : null}
                      </View>
                      <View style={styles.inlineRow}>
                        <Button variant="ghost" size="sm" onPress={() => testInbound(k._id)} loading={testingId === k._id}><RefreshCw size={14} color={colors.textSecondary} /></Button>
                        <Button variant="ghost" size="sm" onPress={() => { setEditingInbound(k._id); setInboundForm({ provider: k.provider, name: k.name, apiKey: '', baseUrl: k.baseUrl || '', apiStructure: '' }); setShowInbound(true); }}><Text style={{ color: colors.textSecondary }}>✎</Text></Button>
                        <Button variant="ghost" size="sm" onPress={() => deleteInbound(k._id)}><Trash2 size={14} color={colors.danger} /></Button>
                      </View>
                    </View>
                  </Card>
                ))}
              </View>
            )}
          </View>
        );

      case 'security':
        return (
          <View>
            <Card style={{ borderColor: colors.danger + '30' }}>
              <Text style={[styles.sectionTitle, { color: colors.danger }]}>Danger Zone</Text>
              <Text style={[styles.dangerText, { color: colors.textMuted }]}>Permanently delete your account and all data.</Text>
              <Button variant="danger" size="sm" onPress={() => setDeleteModal(true)}>
                <Trash2 size={16} color="#fff" /><Text style={{ color: '#fff', marginLeft: 6 }}>Delete Account</Text>
              </Button>
            </Card>
            <TouchableOpacity onPress={logout} style={[styles.logoutBtn, { borderColor: colors.border }]}>
              <LogOut size={18} color={colors.danger} />
              <Text style={[styles.logoutText, { color: colors.danger }]}>Sign Out</Text>
            </TouchableOpacity>
          </View>
        );

      default:
        return null;
    }
  };

  return (
    <ScreenWrapper style={{ backgroundColor: colors.bg }}>
      <View style={styles.header}>
        <Text style={[styles.heading, { color: colors.text }]}>Settings</Text>
      </View>

      <View style={styles.tabBar}>
        {tabs.map(t => (
          <TouchableOpacity key={t.id} onPress={() => setTab(t.id)}
            style={[styles.tabBtn, { backgroundColor: tab === t.id ? colors.accent + '15' : 'transparent' }]}>
            <Text style={[styles.tabLabel, { color: tab === t.id ? colors.accent : colors.textSecondary }]}>{t.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {renderTab()}
      </ScrollView>

      <Modal open={deleteModal} onClose={() => setDeleteModal(false)} title="Delete Account">
        <Text style={[styles.modalText, { color: colors.textSecondary }]}>This action is permanent. All your data, conversations, and keys will be deleted.</Text>
        <Input label="Enter your password to confirm" value={deletePassword} onChangeText={setDeletePassword} secureTextEntry placeholder="••••••••" />
        <View style={styles.formBtns}>
          <Button variant="danger" size="sm" onPress={handleDeleteAccount} loading={deleting} disabled={!deletePassword}>Delete Forever</Button>
          <Button variant="secondary" size="sm" onPress={() => setDeleteModal(false)}>Cancel</Button>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: 16, paddingTop: 10 },
  heading: { fontSize: 24, fontWeight: '700', marginBottom: 12 },
  tabBar: { flexDirection: 'row', paddingHorizontal: 12, marginBottom: 8, gap: 4 },
  tabBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
  tabLabel: { fontSize: 13, fontWeight: '600' },
  content: { flex: 1, paddingHorizontal: 14 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  sectionTitle: { fontSize: 15, fontWeight: '600', marginBottom: 12 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 8 },
  label: { fontSize: 13 },
  value: { fontSize: 13, fontWeight: '500' },
  smallLabel: { fontSize: 11, marginTop: 2 },
  form: { gap: 6 },
  formBtns: { flexDirection: 'row', gap: 8, marginTop: 8 },
  warningText: { fontSize: 13, fontWeight: '600', marginBottom: 8 },
  keyText: { fontSize: 12, fontFamily: 'monospace', marginBottom: 10, lineHeight: 20 },
  keyPrefix: { fontSize: 14, fontFamily: 'monospace', fontWeight: '500' },
  emptyText: { textAlign: 'center', paddingVertical: 16, fontSize: 13 },
  subtabs: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  subtab: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10 },
  subtabText: { fontSize: 12, fontWeight: '600' },
  inlineRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  statusDot: { width: 8, height: 8, borderRadius: 4 },
  picker: { borderWidth: 1, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 12 },
  dangerText: { fontSize: 12, marginBottom: 12, lineHeight: 18 },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 20, borderWidth: 1, borderRadius: 12, paddingVertical: 14 },
  logoutText: { fontSize: 14, fontWeight: '600' },
  modalText: { fontSize: 13, marginBottom: 16, lineHeight: 20 },
});