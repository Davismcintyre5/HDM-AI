import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuth } from '../../context/AuthContext';
import ScreenWrapper from '../../components/ui/ScreenWrapper';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { useTheme } from '../../context/ThemeContext';

export default function RegisterScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { colors } = useTheme();

  const handleRegister = async () => {
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
      <ScreenWrapper scroll padded safe>
        <View style={styles.container}>
          <Text style={[styles.title, { color: colors.success }]}>Check Your Email</Text>
          <Text style={[styles.message, { color: colors.textSecondary }]}>{success}</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')}>
            <Text style={[styles.link, { color: colors.accent }]}>Back to login</Text>
          </TouchableOpacity>
        </View>
      </ScreenWrapper>
    );
  }

  return (
    <ScreenWrapper scroll padded safe avoidKeyboard>
      <View style={styles.container}>
        <Text style={[styles.title, { color: colors.text }]}>Create Account</Text>
        <Text style={[styles.subtitle, { color: colors.textMuted }]}>Join HDM AI</Text>

        <Input label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" placeholder="you@example.com" />
        <Input label="Username" value={username} onChangeText={setUsername} placeholder="Your name" />
        <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry placeholder="••••••••" />
        {error ? <Text style={[styles.error, { color: colors.danger }]}>{error}</Text> : null}

        <Button onPress={handleRegister} loading={loading} style={styles.btn}>Create Account</Button>

        <TouchableOpacity onPress={() => navigation.navigate('Login')} style={styles.footer}>
          <Text style={[styles.footerText, { color: colors.textMuted }]}>
            Already have an account? <Text style={{ color: colors.accent }}>Sign in</Text>
          </Text>
        </TouchableOpacity>
      </View>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', maxWidth: 360, width: '100%', alignSelf: 'center' },
  title: { fontSize: 26, fontWeight: '700', textAlign: 'center', marginBottom: 4 },
  subtitle: { fontSize: 14, textAlign: 'center', marginBottom: 28 },
  message: { fontSize: 14, textAlign: 'center', marginBottom: 20, lineHeight: 22 },
  error: { fontSize: 13, marginBottom: 12, textAlign: 'center' },
  btn: { marginTop: 4 },
  link: { textAlign: 'center', marginTop: 14, fontSize: 13 },
  footer: { marginTop: 24, alignItems: 'center' },
  footerText: { fontSize: 13 },
});