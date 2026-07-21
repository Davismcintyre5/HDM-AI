import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MessageSquare, FileSearch, Code, Image, BookOpen, Settings } from 'lucide-react-native';
import { useTheme } from '../context/ThemeContext';
import ChatScreen from '../screens/ChatScreen';
import AnalyzeScreen from '../screens/AnalyzeScreen';
import CodeScreen from '../screens/CodeScreen';
import ImageScreen from '../screens/ImageScreen';
import LearnScreen from '../screens/LearnScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Tab = createBottomTabNavigator();

const tabs = [
  { name: 'Chat', component: ChatScreen, icon: MessageSquare },
  { name: 'Analyze', component: AnalyzeScreen, icon: FileSearch },
  { name: 'Code', component: CodeScreen, icon: Code },
  { name: 'Image', component: ImageScreen, icon: Image },
  { name: 'Learn', component: LearnScreen, icon: BookOpen },
  { name: 'Settings', component: SettingsScreen, icon: Settings },
];

export default function MainTabs() {
  const { colors } = useTheme();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.bgSecondary,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarLabelStyle: { fontSize: 10, fontWeight: '600' },
      }}
    >
      {tabs.map(({ name, component, icon: Icon }) => (
        <Tab.Screen
          key={name}
          name={name}
          component={component}
          options={{
            tabBarIcon: ({ color, size }) => <Icon size={size || 22} color={color} />,
          }}
        />
      ))}
    </Tab.Navigator>
  );
}