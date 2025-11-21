# Student Hub - Frontend

Modern React frontend for the Student Hub academic and career management platform.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Open http://localhost:5173
```

## 📚 Tech Stack

- **React 18** + TypeScript
- **Vite** - Build tool
- **React Router** - Navigation
- **TanStack Query** - Server state
- **Zustand** - Client state
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## 🔧 Development

```bash
npm run dev       # Start dev server
npm run build     # Build for production
npm run preview   # Preview build
```

## 🌐 API Connection

Backend: `https://assignment-calendar-sync-production.up.railway.app/api/v1`

The frontend automatically connects to your Railway backend.

## 📖 Features

✅ User authentication
✅ Dashboard with stats
✅ Assignments list (real-time)
✅ Responsive navigation
✅ Protected routes

🚧 Coming soon: Canvas/Gmail/Gradescope integration

## 🚀 Deployment

### Vercel (Recommended)
```bash
vercel
```

### Netlify
```bash
npm run build
netlify deploy --prod --dir=dist
```

## 📁 Project Structure

```
src/
├── api/          # API clients
├── components/   # Reusable components
├── pages/        # Page components
├── store/        # Zustand stores
├── types/        # TypeScript types
└── App.tsx       # Main app with routing
```

## 🔐 Environment Variables

Create `.env.local`:
```env
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

## 📝 License

MIT
