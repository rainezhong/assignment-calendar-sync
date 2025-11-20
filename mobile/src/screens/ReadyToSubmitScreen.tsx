/**
 * Ready to Submit Queue - Applications auto-prepared by the system
 * User just reviews and taps to submit
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { format } from 'date-fns';
import api from '../services/api';
import { colors } from '../theme/colors';

export default function ReadyToSubmitScreen() {
  const [queue, setQueue] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [submitting, setSubmitting] = useState<number | null>(null);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      const data = await api.getReadyToSubmitQueue();
      setQueue(data);
    } catch (error) {
      console.error('Failed to load queue:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadQueue();
    setRefreshing(false);
  };

  const handleApprove = async (applicationId: number) => {
    Alert.alert(
      'Submit Application?',
      'This will submit your application. You can still review the details first.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Submit',
          style: 'default',
          onPress: async () => {
            setSubmitting(applicationId);
            try {
              await api.approveApplication(applicationId);
              Alert.alert('Success!', 'Application submitted successfully! 🎉');
              // Remove from queue
              setQueue(queue.filter(item => item.id !== applicationId));
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to submit');
            } finally {
              setSubmitting(null);
            }
          },
        },
      ]
    );
  };

  const handleDismiss = async (applicationId: number) => {
    Alert.alert(
      'Dismiss Application?',
      "You won't apply to this job.",
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Dismiss',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.dismissApplication(applicationId);
              setQueue(queue.filter(item => item.id !== applicationId));
            } catch (error: any) {
              Alert.alert('Error', 'Failed to dismiss');
            }
          },
        },
      ]
    );
  };

  if (queue.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyState}>
          <Ionicons name="checkmark-done-circle-outline" size={80} color={colors.gray300} />
          <Text style={styles.emptyTitle}>All caught up!</Text>
          <Text style={styles.emptyText}>
            New applications will appear here automatically when jobs matching your profile are
            found.
          </Text>
          <Text style={styles.emptySubtext}>
            The system searches for jobs daily at 8 AM and prepares applications for you.
          </Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Ready to Submit</Text>
          <Text style={styles.subtitle}>{queue.length} applications prepared</Text>
        </View>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{queue.length}</Text>
        </View>
      </View>

      {/* Info Banner */}
      <View style={styles.infoBanner}>
        <Ionicons name="information-circle" size={20} color={colors.primary} />
        <Text style={styles.infoText}>
          These applications were automatically prepared for you. Review and tap Submit!
        </Text>
      </View>

      {/* Queue Items */}
      {queue.map((item, index) => (
        <View key={item.id} style={styles.card}>
          {/* Job Info */}
          <View style={styles.cardHeader}>
            <View style={styles.cardHeaderLeft}>
              <Text style={styles.jobTitle} numberOfLines={2}>
                {item.job.title}
              </Text>
              <Text style={styles.jobCompany}>{item.job.company}</Text>
              <Text style={styles.jobLocation}>{item.job.location}</Text>
            </View>
            <View style={styles.indexBadge}>
              <Text style={styles.indexText}>#{index + 1}</Text>
            </View>
          </View>

          {/* Salary if available */}
          {item.job.salary_min && (
            <View style={styles.salaryContainer}>
              <Ionicons name="cash-outline" size={16} color={colors.success} />
              <Text style={styles.salaryText}>
                ${item.job.salary_min.toLocaleString()}
                {item.job.salary_max && ` - $${item.job.salary_max.toLocaleString()}`}
              </Text>
            </View>
          )}

          {/* Cover Letter Preview */}
          <View style={styles.coverLetterPreview}>
            <Text style={styles.coverLetterLabel}>Cover Letter (AI-generated):</Text>
            <Text style={styles.coverLetterText} numberOfLines={3}>
              {item.cover_letter}
            </Text>
            <TouchableOpacity>
              <Text style={styles.expandText}>View full letter →</Text>
            </TouchableOpacity>
          </View>

          {/* Auto-filled info */}
          <View style={styles.autoFilledInfo}>
            <Ionicons name="checkmark-circle" size={16} color={colors.success} />
            <Text style={styles.autoFilledText}>All fields pre-filled and ready</Text>
          </View>

          {/* Actions */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[
                styles.submitButton,
                submitting === item.id && styles.submitButtonLoading,
              ]}
              onPress={() => handleApprove(item.id)}
              disabled={submitting === item.id}
            >
              {submitting === item.id ? (
                <Text style={styles.submitButtonText}>Submitting...</Text>
              ) : (
                <>
                  <Ionicons name="send" size={20} color={colors.white} />
                  <Text style={styles.submitButtonText}>Submit Application</Text>
                </>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.dismissButton}
              onPress={() => handleDismiss(item.id)}
              disabled={submitting === item.id}
            >
              <Ionicons name="close-circle-outline" size={20} color={colors.textSecondary} />
              <Text style={styles.dismissButtonText}>Dismiss</Text>
            </TouchableOpacity>
          </View>

          {/* Timestamp */}
          <Text style={styles.timestamp}>
            Prepared {format(new Date(item.created_at), 'MMM d, h:mm a')}
          </Text>
        </View>
      ))}

      {/* Batch Actions */}
      {queue.length > 1 && (
        <View style={styles.batchActions}>
          <TouchableOpacity style={styles.batchButton}>
            <Text style={styles.batchButtonText}>Submit All ({queue.length})</Text>
          </TouchableOpacity>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
    paddingTop: 60,
    backgroundColor: colors.white,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.textPrimary,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 4,
  },
  badge: {
    backgroundColor: colors.primary,
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: 'bold',
  },
  infoBanner: {
    flexDirection: 'row',
    backgroundColor: colors.primary + '10',
    padding: 16,
    margin: 16,
    borderRadius: 12,
    gap: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: colors.textPrimary,
    lineHeight: 20,
  },
  card: {
    backgroundColor: colors.white,
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  cardHeaderLeft: {
    flex: 1,
  },
  jobTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  jobCompany: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '500',
    marginBottom: 4,
  },
  jobLocation: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  indexBadge: {
    backgroundColor: colors.gray100,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    height: 32,
  },
  indexText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  salaryContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginBottom: 12,
  },
  salaryText: {
    fontSize: 14,
    color: colors.success,
    fontWeight: '500',
  },
  coverLetterPreview: {
    backgroundColor: colors.backgroundDark,
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  coverLetterLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: 6,
  },
  coverLetterText: {
    fontSize: 14,
    color: colors.textPrimary,
    lineHeight: 20,
  },
  expandText: {
    fontSize: 12,
    color: colors.primary,
    marginTop: 6,
  },
  autoFilledInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 16,
  },
  autoFilledText: {
    fontSize: 12,
    color: colors.success,
    fontWeight: '500',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
  },
  submitButton: {
    flex: 2,
    flexDirection: 'row',
    backgroundColor: colors.primary,
    padding: 16,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  submitButtonLoading: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  dismissButton: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: colors.gray100,
    padding: 16,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  dismissButtonText: {
    color: colors.textSecondary,
    fontSize: 14,
    fontWeight: '500',
  },
  timestamp: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 12,
    textAlign: 'center',
  },
  batchActions: {
    padding: 16,
  },
  batchButton: {
    backgroundColor: colors.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  batchButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginTop: 16,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: 12,
    lineHeight: 24,
  },
  emptySubtext: {
    fontSize: 14,
    color: colors.textTertiary,
    textAlign: 'center',
    lineHeight: 20,
  },
});
