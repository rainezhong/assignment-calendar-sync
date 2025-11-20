/**
 * Home dashboard screen with health score, upcoming assignments, and AI suggestions.
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { format } from 'date-fns';
import api from '../services/api';
import { colors } from '../theme/colors';
import { Assignment, HealthScore } from '../types';

export default function HomeScreen() {
  const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
  const [upcomingAssignments, setUpcomingAssignments] = useState<Assignment[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [health, assignments, suggestionsData] = await Promise.all([
        api.getHealthScore(),
        api.getAssignments({ limit: 5, is_completed: false }),
        api.getSuggestions(),
      ]);

      setHealthScore(health);
      setUpcomingAssignments(assignments);
      setSuggestions(suggestionsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return colors.success;
    if (score >= 60) return colors.warning;
    return colors.error;
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return colors.riskLow;
      case 'medium': return colors.riskMedium;
      case 'high': return colors.riskHigh;
      case 'critical': return colors.riskCritical;
      default: return colors.gray400;
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>Welcome back!</Text>
        <Text style={styles.date}>{format(new Date(), 'EEEE, MMMM d')}</Text>
      </View>

      {/* Health Score Card */}
      {healthScore && (
        <View style={styles.healthCard}>
          <View style={styles.healthHeader}>
            <Text style={styles.cardTitle}>Academic Health</Text>
            <Ionicons
              name={healthScore.trend === 'improving' ? 'trending-up' : 'trending-down'}
              size={20}
              color={healthScore.trend === 'improving' ? colors.success : colors.error}
            />
          </View>

          <View style={styles.healthScoreContainer}>
            <Text
              style={[
                styles.healthScoreText,
                { color: getHealthColor(healthScore.overall_score) },
              ]}
            >
              {healthScore.overall_score.toFixed(0)}
            </Text>
            <Text style={styles.healthScoreLabel}>/ 100</Text>
          </View>

          <View style={styles.healthMetrics}>
            <View style={styles.metric}>
              <Text style={styles.metricValue}>
                {(healthScore.completion_rate * 100).toFixed(0)}%
              </Text>
              <Text style={styles.metricLabel}>Completion</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricValue}>
                {healthScore.productivity_score.toFixed(0)}
              </Text>
              <Text style={styles.metricLabel}>Productivity</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricValue}>
                {(healthScore.stress_level * 100).toFixed(0)}%
              </Text>
              <Text style={styles.metricLabel}>Stress</Text>
            </View>
          </View>
        </View>
      )}

      {/* Upcoming Assignments */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Upcoming Assignments</Text>
        {upcomingAssignments.map((assignment) => (
          <TouchableOpacity key={assignment.id} style={styles.assignmentCard}>
            <View style={styles.assignmentHeader}>
              <Text style={styles.assignmentTitle} numberOfLines={1}>
                {assignment.title}
              </Text>
              <View
                style={[
                  styles.badge,
                  { backgroundColor: colors.primary + '20' },
                ]}
              >
                <Text style={[styles.badgeText, { color: colors.primary }]}>
                  {assignment.assignment_type}
                </Text>
              </View>
            </View>
            <Text style={styles.assignmentCourse}>{assignment.course_name}</Text>
            <View style={styles.assignmentFooter}>
              <Text style={styles.assignmentDue}>
                Due {format(new Date(assignment.due_date), 'MMM d, h:mm a')}
              </Text>
              {assignment.estimated_hours && (
                <Text style={styles.assignmentHours}>
                  ~{assignment.estimated_hours}h
                </Text>
              )}
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* AI Suggestions */}
      {suggestions.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI Suggestions</Text>
          {suggestions.map((suggestion, index) => (
            <View key={index} style={styles.suggestionCard}>
              <View style={styles.suggestionHeader}>
                <Ionicons
                  name={
                    suggestion.type === 'reminder'
                      ? 'notifications'
                      : suggestion.type === 'break'
                      ? 'cafe'
                      : 'bulb'
                  }
                  size={24}
                  color={colors.primary}
                />
                <Text style={styles.suggestionTitle}>{suggestion.title}</Text>
              </View>
              <Text style={styles.suggestionDescription}>
                {suggestion.description}
              </Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundDark,
  },
  header: {
    padding: 24,
    paddingTop: 60,
    backgroundColor: colors.white,
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.textPrimary,
  },
  date: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: 4,
  },
  healthCard: {
    backgroundColor: colors.white,
    margin: 16,
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  healthHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  healthScoreContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'center',
    marginVertical: 12,
  },
  healthScoreText: {
    fontSize: 56,
    fontWeight: 'bold',
  },
  healthScoreLabel: {
    fontSize: 24,
    color: colors.textSecondary,
    marginLeft: 4,
  },
  healthMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  metric: {
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  metricLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 12,
  },
  assignmentCard: {
    backgroundColor: colors.white,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  assignmentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  assignmentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    flex: 1,
    marginRight: 8,
  },
  assignmentCourse: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  assignmentFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  assignmentDue: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  assignmentHours: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '500',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '500',
  },
  suggestionCard: {
    backgroundColor: colors.white,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  suggestionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  suggestionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginLeft: 12,
  },
  suggestionDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
});
