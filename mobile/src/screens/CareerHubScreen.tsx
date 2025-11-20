/**
 * Career Hub main screen - Job search dashboard
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
import { useNavigation } from '@react-navigation/native';
import api from '../services/api';
import { colors } from '../theme/colors';

export default function CareerHubScreen() {
  const navigation = useNavigation();
  const [stats, setStats] = useState<any>(null);
  const [topMatches, setTopMatches] = useState<any[]>([]);
  const [readyQueue, setReadyQueue] = useState<any[]>([]);
  const [hasProfile, setHasProfile] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Check if user has profile
      try {
        await api.getCareerProfile();
        setHasProfile(true);

        // Load stats, matches, and ready queue
        const [statsData, matchesData, queueData] = await Promise.all([
          api.getApplicationStats(),
          api.getJobMatches({ limit: 5 }),
          api.getReadyToSubmitQueue(),
        ]);

        setStats(statsData);
        setTopMatches(matchesData);
        setReadyQueue(queueData);
      } catch (error: any) {
        if (error.response?.status === 404) {
          setHasProfile(false);
        }
      }
    } catch (error) {
      console.error('Failed to load career hub data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleSearchJobs = async () => {
    try {
      await api.searchJobs();
      alert('Job search started! Check back soon for matches.');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to start job search');
    }
  };

  if (!hasProfile) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyState}>
          <Ionicons name="briefcase-outline" size={80} color={colors.gray300} />
          <Text style={styles.emptyTitle}>Welcome to Career Hub!</Text>
          <Text style={styles.emptyText}>
            Get started by creating your profile and uploading your resume.
          </Text>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => navigation.navigate('ProfileSetup' as never)}
          >
            <Text style={styles.primaryButtonText}>Create Profile</Text>
          </TouchableOpacity>
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
        <Text style={styles.title}>Career Hub</Text>
        <TouchableOpacity onPress={() => navigation.navigate('ProfileSettings' as never)}>
          <Ionicons name="settings-outline" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* Ready to Submit Alert - CRITICAL FEATURE */}
      {readyQueue.length > 0 && (
        <TouchableOpacity
          style={styles.readyToSubmitCard}
          onPress={() => navigation.navigate('ReadyToSubmit' as never)}
        >
          <View style={styles.readyToSubmitHeader}>
            <View style={styles.readyToSubmitIcon}>
              <Ionicons name="rocket" size={32} color={colors.white} />
            </View>
            <View style={styles.readyToSubmitContent}>
              <Text style={styles.readyToSubmitTitle}>
                {readyQueue.length} Application{readyQueue.length > 1 ? 's' : ''} Ready!
              </Text>
              <Text style={styles.readyToSubmitSubtitle}>
                Auto-prepared and ready to submit
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color={colors.white} />
          </View>
          <View style={styles.readyToSubmitFooter}>
            <Ionicons name="information-circle" size={16} color={colors.white} />
            <Text style={styles.readyToSubmitFooterText}>
              Tap to review and submit with one click
            </Text>
          </View>
        </TouchableOpacity>
      )}

      {/* Quick Stats */}
      {stats && (
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{stats.total || 0}</Text>
            <Text style={styles.statLabel}>Applications</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {stats.by_status?.interviewing || 0}
            </Text>
            <Text style={styles.statLabel}>Interviews</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {stats.by_status?.offer || 0}
            </Text>
            <Text style={styles.statLabel}>Offers</Text>
          </View>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity style={styles.actionButton} onPress={handleSearchJobs}>
          <Ionicons name="search" size={24} color={colors.primary} />
          <Text style={styles.actionButtonText}>Find Jobs</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('JobMatches' as never)}
        >
          <Ionicons name="star" size={24} color={colors.primary} />
          <Text style={styles.actionButtonText}>Matches</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Applications' as never)}
        >
          <Ionicons name="list" size={24} color={colors.primary} />
          <Text style={styles.actionButtonText}>Track Apps</Text>
        </TouchableOpacity>
      </View>

      {/* Top Matches */}
      {topMatches.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Top Matches</Text>
            <TouchableOpacity onPress={() => navigation.navigate('JobMatches' as never)}>
              <Text style={styles.seeAllText}>See All</Text>
            </TouchableOpacity>
          </View>

          {topMatches.map((match) => (
            <TouchableOpacity
              key={match.id}
              style={styles.jobCard}
              onPress={() =>
                navigation.navigate('JobDetail' as never, { matchId: match.id } as never)
              }
            >
              <View style={styles.jobCardHeader}>
                <Text style={styles.jobTitle} numberOfLines={1}>
                  {match.job.title}
                </Text>
                <View style={styles.matchBadge}>
                  <Text style={styles.matchScore}>{Math.round(match.match_score * 100)}%</Text>
                </View>
              </View>

              <Text style={styles.jobCompany}>{match.job.company}</Text>
              <Text style={styles.jobLocation}>{match.job.location}</Text>

              {match.match_reasons.length > 0 && (
                <View style={styles.matchReasons}>
                  <Text style={styles.matchReason} numberOfLines={1}>
                    {match.match_reasons[0]}
                  </Text>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Tips Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Career Tips</Text>
        <View style={styles.tipCard}>
          <Ionicons name="bulb-outline" size={24} color={colors.primary} />
          <View style={styles.tipContent}>
            <Text style={styles.tipTitle}>Customize your resume</Text>
            <Text style={styles.tipText}>
              Tailor your resume for each job to increase your match score
            </Text>
          </View>
        </View>
      </View>
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
    marginBottom: 24,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  primaryButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.white,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  actionsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.white,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    gap: 8,
  },
  actionButtonText: {
    fontSize: 12,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  section: {
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  seeAllText: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '500',
  },
  jobCard: {
    backgroundColor: colors.white,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  jobCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  jobTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginRight: 8,
  },
  matchBadge: {
    backgroundColor: colors.success + '20',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  matchScore: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.success,
  },
  jobCompany: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  jobLocation: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  matchReasons: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  matchReason: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  tipCard: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  tipContent: {
    flex: 1,
  },
  tipTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  tipText: {
    fontSize: 12,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  readyToSubmitCard: {
    backgroundColor: colors.primary,
    margin: 16,
    borderRadius: 16,
    padding: 20,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  readyToSubmitHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  readyToSubmitIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  readyToSubmitContent: {
    flex: 1,
  },
  readyToSubmitTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.white,
    marginBottom: 4,
  },
  readyToSubmitSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  readyToSubmitFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  readyToSubmitFooterText: {
    fontSize: 13,
    color: colors.white,
    fontWeight: '500',
  },
});
