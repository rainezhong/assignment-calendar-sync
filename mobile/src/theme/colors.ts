/**
 * App color palette.
 */

export const colors = {
  // Primary brand colors
  primary: '#4F46E5',  // Indigo
  primaryLight: '#818CF8',
  primaryDark: '#3730A3',

  // Accent colors
  accent: '#10B981',  // Green
  accentLight: '#34D399',
  accentDark: '#059669',

  // Risk levels
  riskLow: '#10B981',
  riskMedium: '#F59E0B',
  riskHigh: '#EF4444',
  riskCritical: '#DC2626',

  // Neutral colors
  white: '#FFFFFF',
  black: '#000000',
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
  gray900: '#111827',

  // Semantic colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Background colors
  background: '#FFFFFF',
  backgroundDark: '#F9FAFB',
  surface: '#FFFFFF',
  surfaceDark: '#F3F4F6',

  // Text colors
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',

  // Border colors
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  borderDark: '#D1D5DB',
};

export type ColorName = keyof typeof colors;
