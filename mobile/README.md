# Assignment Calendar Sync - Mobile App

React Native mobile application built with Expo for iOS and Android.

## Features

- **Authentication**: Secure login/registration with JWT tokens
- **Dashboard**: Real-time health score and upcoming assignments
- **Assignment Management**: Create, view, and track assignments
- **AI Intelligence**: Complexity analysis and resource recommendations
- **Performance Analytics**: Track academic health and trends
- **Risk Assessment**: Predictive alerts for deadline risks
- **Smart Suggestions**: Proactive AI-powered recommendations

## Tech Stack

- **React Native**: Cross-platform mobile framework
- **Expo**: Development toolchain and managed workflow
- **TypeScript**: Type-safe development
- **React Navigation**: Native navigation library
- **Axios**: HTTP client for API calls
- **AsyncStorage**: Secure local storage
- **date-fns**: Date manipulation

## Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac only) or Android Studio
- Expo Go app on physical device (for testing)

## Setup

1. **Install dependencies**:
   ```bash
   cd mobile
   npm install
   ```

2. **Configure API endpoint**:
   - Edit `src/services/api.ts`
   - Update `API_BASE_URL` for development and production

3. **Start development server**:
   ```bash
   npm start
   ```

4. **Run on device/simulator**:
   ```bash
   # iOS (Mac only)
   npm run ios

   # Android
   npm run android

   # Web
   npm run web
   ```

## Project Structure

```
mobile/
├── src/
│   ├── screens/               # Screen components
│   │   ├── LoginScreen.tsx           # Authentication
│   │   ├── HomeScreen.tsx            # Dashboard with health score
│   │   ├── AssignmentsScreen.tsx     # Assignment list
│   │   ├── AssignmentDetailScreen.tsx # Detail view with AI analysis
│   │   ├── AnalyticsScreen.tsx       # Performance charts
│   │   └── ProfileScreen.tsx         # User settings
│   ├── navigation/
│   │   └── AppNavigator.tsx   # Navigation structure
│   ├── services/
│   │   └── api.ts            # API client
│   ├── types/
│   │   └── index.ts          # TypeScript types
│   ├── theme/
│   │   └── colors.ts         # Color palette
│   └── components/           # Reusable UI components
├── assets/                    # Images, fonts, icons
├── App.tsx                    # Entry point
├── app.json                   # Expo configuration
├── package.json              # Dependencies
└── tsconfig.json             # TypeScript config
```

## Screens

### 1. Login Screen
- User registration and login
- JWT token management
- Form validation

### 2. Home Dashboard
- Academic health score (0-100)
- Health trend indicator
- Upcoming assignments (top 5)
- AI-powered suggestions
- Pull-to-refresh

### 3. Assignments Screen
- List of all assignments
- Filter tabs: All / Active / Completed
- Quick actions (mark complete)
- Progress indicators
- Add new assignment button

### 4. Assignment Detail Screen
- Full assignment information
- Risk assessment with color coding
- AI analysis (Bloom's taxonomy, complexity)
- Required skills
- Suggested actions
- Mark complete/incomplete

### 5. Analytics Screen
- Performance trends
- Key insights from AI
- Personalized recommendations
- Historical data visualization

### 6. Profile Screen
- User information
- Premium badge (if applicable)
- Settings menu
- Calendar integration
- Logout

## API Integration

The app connects to the FastAPI backend via REST API:

```typescript
// Example API usage
import api from './services/api';

// Authentication
await api.login(email, password);
await api.register(email, password, fullName);

// Assignments
const assignments = await api.getAssignments();
const assignment = await api.getAssignment(id);

// Intelligence
const analysis = await api.analyzeAssignment(id);

// Analytics
const health = await api.getHealthScore();

// Predictions
const risk = await api.assessRisk(assignmentId);
```

## Development Tips

### Running on Physical Device

1. Install Expo Go app from App Store / Play Store
2. Run `npm start`
3. Scan QR code with camera (iOS) or Expo Go app (Android)

### Hot Reloading

- Changes to code automatically refresh
- Shake device or press `R` to manually reload
- Press `M` to open developer menu

### Debugging

```bash
# Open React Native Debugger
npm start
# Press `J` to open debugger
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Building for Production

### iOS

1. **Configure app.json**:
   - Update `bundleIdentifier`
   - Add splash screen and icon

2. **Build**:
   ```bash
   eas build --platform ios
   ```

3. **Submit to App Store**:
   ```bash
   eas submit --platform ios
   ```

### Android

1. **Configure app.json**:
   - Update `package` name
   - Add splash screen and icon

2. **Build**:
   ```bash
   eas build --platform android
   ```

3. **Submit to Play Store**:
   ```bash
   eas submit --platform android
   ```

## Environment Variables

For production, use Expo's environment configuration:

```bash
# .env
API_BASE_URL=https://api.yourapp.com
```

## Testing

```bash
npm test
```

## Key Features Implementation

### Authentication Flow
- JWT tokens stored in AsyncStorage
- Automatic token refresh
- Secure logout

### Offline Support
- Coming soon: Local caching with AsyncStorage
- Sync when back online

### Push Notifications
- Reminder notifications for due assignments
- Risk alerts
- AI suggestions

### Calendar Integration
- Sync with device calendar
- Export assignments to calendar events

## Performance Optimization

- Lazy loading for images
- FlatList for efficient list rendering
- Memoization for expensive computations
- API response caching

## Next Steps

1. **Add offline support**: Cache API responses locally
2. **Push notifications**: Implement notification system
3. **Calendar sync**: Two-way sync with device calendar
4. **Dark mode**: Add theme toggle
5. **Animations**: Smooth transitions and micro-interactions
6. **Error boundaries**: Better error handling
7. **Loading states**: Skeleton screens
8. **Search**: Global search for assignments
9. **Filters**: Advanced filtering and sorting
10. **Settings**: More customization options

## Troubleshooting

**Issue: Metro bundler not starting**
```bash
npm start -- --reset-cache
```

**Issue: iOS build fails**
```bash
cd ios && pod install && cd ..
```

**Issue: Android build fails**
```bash
cd android && ./gradlew clean && cd ..
```

## License

MIT - See LICENSE file
