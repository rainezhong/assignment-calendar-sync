/**
 * Assignment detail screen with AI analysis.
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { format } from 'date-fns';
import api from '../services/api';
import { colors } from '../theme/colors';
import { Assignment, RiskAssessment } from '../types';

interface Props {
  route: { params: { assignmentId: number } };
}

export default function AssignmentDetailScreen({ route }: Props) {
  const { assignmentId } = route.params;
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [assignmentId]);

  const loadData = async () => {
    try {
      const [assignmentData, riskData] = await Promise.all([
        api.getAssignment(assignmentId),
        api.assessRisk(assignmentId),
      ]);

      setAssignment(assignmentData);
      setRisk(riskData);
    } catch (error) {
      console.error('Failed to load assignment:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return colors.riskLow;
      case 'medium':
        return colors.riskMedium;
      case 'high':
        return colors.riskHigh;
      case 'critical':
        return colors.riskCritical;
      default:
        return colors.gray400;
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!assignment) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Assignment not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>{assignment.title}</Text>
        <Text style={styles.course}>{assignment.course_name}</Text>

        <View style={styles.metadata}>
          <View style={styles.metadataItem}>
            <Ionicons name="calendar" size={16} color={colors.textSecondary} />
            <Text style={styles.metadataText}>
              Due {format(new Date(assignment.due_date), 'MMM d, h:mm a')}
            </Text>
          </View>

          {assignment.estimated_hours && (
            <View style={styles.metadataItem}>
              <Ionicons name="time" size={16} color={colors.textSecondary} />
              <Text style={styles.metadataText}>~{assignment.estimated_hours}h</Text>
            </View>
          )}
        </View>
      </View>

      {/* Risk Assessment */}
      {risk && (
        <View style={[styles.card, { borderLeftColor: getRiskColor(risk.risk_level) }]}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Risk Assessment</Text>
            <View
              style={[
                styles.riskBadge,
                { backgroundColor: getRiskColor(risk.risk_level) + '20' },
              ]}
            >
              <Text style={[styles.riskBadgeText, { color: getRiskColor(risk.risk_level) }]}>
                {risk.risk_level.toUpperCase()}
              </Text>
            </View>
          </View>

          <Text style={styles.riskProbability}>
            {(risk.probability * 100).toFixed(0)}% chance of missing deadline
          </Text>

          <View style={styles.riskFactors}>
            {risk.risk_factors.map((factor, index) => (
              <View key={index} style={styles.riskFactor}>
                <View style={styles.riskFactorHeader}>
                  <Text style={styles.riskFactorName}>{factor.factor}</Text>
                  <Text style={styles.riskFactorScore}>
                    {(factor.score * 100).toFixed(0)}%
                  </Text>
                </View>
                <Text style={styles.riskFactorDescription}>{factor.description}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* AI Analysis */}
      {assignment.blooms_level && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>AI Analysis</Text>

          <View style={styles.analysisGrid}>
            <View style={styles.analysisItem}>
              <Text style={styles.analysisLabel}>Cognitive Level</Text>
              <Text style={styles.analysisValue}>{assignment.blooms_level}</Text>
            </View>

            <View style={styles.analysisItem}>
              <Text style={styles.analysisLabel}>Complexity</Text>
              <Text style={styles.analysisValue}>
                {assignment.complexity_score &&
                  (assignment.complexity_score * 100).toFixed(0)}
                %
              </Text>
            </View>

            <View style={styles.analysisItem}>
              <Text style={styles.analysisLabel}>Estimated Time</Text>
              <Text style={styles.analysisValue}>{assignment.estimated_hours}h</Text>
            </View>

            <View style={styles.analysisItem}>
              <Text style={styles.analysisLabel}>Actual Time</Text>
              <Text style={styles.analysisValue}>{assignment.actual_hours_spent}h</Text>
            </View>
          </View>
        </View>
      )}

      {/* Description */}
      {assignment.description && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Description</Text>
          <Text style={styles.description}>{assignment.description}</Text>
        </View>
      )}

      {/* Suggested Actions */}
      {risk && risk.suggested_actions.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Suggested Actions</Text>
          {risk.suggested_actions.map((action, index) => (
            <View key={index} style={styles.actionItem}>
              <Ionicons name="checkmark-circle-outline" size={20} color={colors.primary} />
              <Text style={styles.actionText}>{action}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.button, assignment.is_completed && styles.buttonOutline]}
        >
          <Text
            style={[
              styles.buttonText,
              assignment.is_completed && styles.buttonOutlineText,
            ]}
          >
            {assignment.is_completed ? 'Mark Incomplete' : 'Mark Complete'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundDark,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  header: {
    backgroundColor: colors.white,
    padding: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: 8,
  },
  course: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '500',
    marginBottom: 16,
  },
  metadata: {
    flexDirection: 'row',
    gap: 16,
  },
  metadataItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metadataText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  card: {
    backgroundColor: colors.white,
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: 'transparent',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 12,
  },
  riskBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  riskBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  riskProbability: {
    fontSize: 16,
    color: colors.textPrimary,
    marginBottom: 16,
  },
  riskFactors: {
    gap: 12,
  },
  riskFactor: {
    padding: 12,
    backgroundColor: colors.backgroundDark,
    borderRadius: 8,
  },
  riskFactorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  riskFactorName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  riskFactorScore: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
  },
  riskFactorDescription: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  analysisGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  analysisItem: {
    flex: 1,
    minWidth: '45%',
  },
  analysisLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  analysisValue: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  description: {
    fontSize: 16,
    color: colors.textPrimary,
    lineHeight: 24,
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 12,
  },
  actionText: {
    flex: 1,
    fontSize: 16,
    color: colors.textPrimary,
    lineHeight: 22,
  },
  actions: {
    padding: 16,
  },
  button: {
    backgroundColor: colors.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: colors.primary,
  },
  buttonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  buttonOutlineText: {
    color: colors.primary,
  },
});
