import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuth } from '../../context/AuthContext';
import ScreenWrapper from '../../components/ui/ScreenWrapper';
import Spinner from '../../components/ui/Spinner';
import { useTheme } from '../../context/ThemeContext';

export default function VerifyEmailScreen({ route, navigation }) {
  const token = route.params?.token;
  const { verifyEmail } = useAuth();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('');
  const { colors } = useTheme();

  useEffect(() => {
    if (!token) { setStatus('error'); setMessage('No verification token provided.'); return; }
    verifyEmail(token)
      .then((res) => { setStatus('success'); setMessage(res.message || 'Email verified!'); })
      .catch((err) => { setStatus('error'); setMessage(err.response?.data?.error || 'Verification failed.'); });
  }, [token]);

  return (
    <ScreenWrapper padded safe>
      <View style={styles.container}>
        {status === 'loading' && <Spinner size="lg" />}
        {status === 'success' && (
          <>
            <Text style={[styles.title, { color: colors.success }]}>Verified!</Text>
            <Text style={[styles.message, { color: colors.textSecondary }]}>{message}</Text>
            <TouchableOpacity onPress={() => navigation.navigate('MainTabs')}>
              <Text style={[styles.link, { color: colors.accent }]}>Go to Chat</Text>
            </TouchableOpacity>
          </>
        )}
        {status === 'error' && (
          <>
            <Text style={[styles.title, { color: colors.danger }]}>Failed</Text>
            <Text style={[styles.message, { color: colors.textSecondary }]}>{message}</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Login')}>
              <Text style={[styles.link, { color: colors.accent }]}>Back to login</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 26, fontWeight: '700', marginBottom: 8 },
  message: { fontSize: 14, textAlign: 'center', marginBottom: 20, lineHeight: 22 },
  link: { fontSize: 14, fontWeight: '600' },
});