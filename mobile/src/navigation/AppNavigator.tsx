/**
 * Main app navigation structure.
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Screens (we'll create these)
import HomeScreen from '../screens/HomeScreen';
import AssignmentsScreen from '../screens/AssignmentsScreen';
import AnalyticsScreen from '../screens/AnalyticsScreen';
import ProfileScreen from '../screens/ProfileScreen';
import LoginScreen from '../screens/LoginScreen';
import AssignmentDetailScreen from '../screens/AssignmentDetailScreen';
import CareerHubScreen from '../screens/CareerHubScreen';
import ReadyToSubmitScreen from '../screens/ReadyToSubmitScreen';

import { colors } from '../theme/colors';

export type RootStackParamList = {
  Login: undefined;
  Main: undefined;
  AssignmentDetail: { assignmentId: number };
};

export type MainTabParamList = {
  Home: undefined;
  Assignments: undefined;
  Analytics: undefined;
  Career: undefined;
  Profile: undefined;
};

export type CareerStackParamList = {
  CareerHub: undefined;
  ReadyToSubmit: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();
const CareerStack = createNativeStackNavigator<CareerStackParamList>();

function CareerNavigator() {
  return (
    <CareerStack.Navigator>
      <CareerStack.Screen
        name="CareerHub"
        component={CareerHubScreen}
        options={{ headerShown: false }}
      />
      <CareerStack.Screen
        name="ReadyToSubmit"
        component={ReadyToSubmitScreen}
        options={{
          headerShown: true,
          title: 'Ready to Submit',
          headerBackTitle: 'Career'
        }}
      />
    </CareerStack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'home';

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Assignments') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Analytics') {
            iconName = focused ? 'stats-chart' : 'stats-chart-outline';
          } else if (route.name === 'Career') {
            iconName = focused ? 'briefcase' : 'briefcase-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.gray400,
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Assignments" component={AssignmentsScreen} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
      <Tab.Screen name="Career" component={CareerNavigator} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  // TODO: Check authentication state
  const isAuthenticated = false;

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          <Stack.Screen name="Login" component={LoginScreen} />
        ) : (
          <>
            <Stack.Screen name="Main" component={MainTabs} />
            <Stack.Screen
              name="AssignmentDetail"
              component={AssignmentDetailScreen}
              options={{ headerShown: true, title: 'Assignment Details' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
