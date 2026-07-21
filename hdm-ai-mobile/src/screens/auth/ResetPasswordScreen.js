import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import api from '../../api/axios';
import ScreenWrapper from '../../components/ui/ScreenWrapper';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { useTheme } from '../../context/ThemeContext';

export default function ResetPasswordScreen({ route, navigation }) {
  const token = route.params?.token;
  const [password, setPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { colors } = useTheme();

  const handleSubmit = async () => {
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
      <ScreenWrapper padded safe>
        <View style={styles.container}>
          <Text style={[styles.title, { color: colors.danger }]}>Invalid Link</Text>
          <Text style={[styles.message, { color: colors.textSecondary }]}>No reset token provided.</Text>
          <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
            <Text style={[styles.link, { color: colors.accent }]}>Request new link</Text>
          </TouchableOpacity>
        </View>
      </ScreenWrapper>
    );
  }

  if (success) {
    return (
      <ScreenWrapper padded safe>
        <View style={styles.container}>
          <Text style={[styles.title, { color: colors.success }]}>Password Reset!</Text>
          <Text style={[styles.message, { color: colors.textSecondary }]}>You can now sign in with your new password.</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')}>
            <Text style={[styles.link, { color: colors.accent }]}>Sign in</Text>
          </TouchableOpacity>
        </View>
      </ScreenWrapper>
    );
  }

  return (
    <ScreenWrapper scroll padded safe avoidKeyboard>
      <View style={styles.container}>
        <Text style={[styles.title, { color: colors.text }]}>New Password</Text>
        <Text style={[styles.subtitle, { color: colors.textMuted }]}>Choose a new password.</Text>

        <Input label="New Password" value={password} onChangeText={setPassword} secureTextEntry placeholder="••••••••" />
        {error ? <Text style={[styles.error, { color: colors.danger }]}>{error}</Text> : null}

        <Button onPress={handleSubmit} loading={loading} style={styles.btn}>Reset Password</Button>
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