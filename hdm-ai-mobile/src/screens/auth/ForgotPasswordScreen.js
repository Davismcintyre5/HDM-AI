import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import api from '../../api/axios';
import ScreenWrapper from '../../components/ui/ScreenWrapper';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { useTheme } from '../../context/ThemeContext';

export default function ForgotPasswordScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { colors } = useTheme();

  const handleSubmit = async () => {
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
      <ScreenWrapper padded safe>
        <View style={styles.container}>
          <Text style={[styles.title, { color: colors.text }]}>Check Your Email</Text>
          <Text style={[styles.message, { color: colors.textSecondary }]}>If that email exists, we sent a reset link.</Text>
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
        <Text style={[styles.title, { color: colors.text }]}>Reset Password</Text>
        <Text style={[styles.subtitle, { color: colors.textMuted }]}>Enter your email to receive a reset link.</Text>

        <Input label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" placeholder="you@example.com" />
        {error ? <Text style={[styles.error, { color: colors.danger }]}>{error}</Text> : null}

        <Button onPress={handleSubmit} loading={loading} style={styles.btn}>Send Reset Link</Button>

        <TouchableOpacity onPress={() => navigation.navigate('Login')}>
          <Text style={[styles.link, { color: colors.accent }]}>Back to login</Text>
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
});