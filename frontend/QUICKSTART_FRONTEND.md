# SafeNest Frontend - Quick Start

## 🎉 Setup Complete!

Your modern React frontend is ready to run!

## 🚀 Start Development Server

```powershell
cd C:\Users\nihed\Desktop\SafeNest\frontend
npm run dev
```

The app will start on **http://localhost:3000**

## 🔐 Login

Use these demo credentials:

- **Username:** `admin`
- **Password:** `admin123`

## ✅ What's Included

### Pages
- ✅ **Login Page** - Beautiful animated login with JWT auth
- ✅ **Dashboard** - Stats, charts, and quick actions
- 🚧 **Alerts** - Coming soon
- 🚧 **Incidents** - Coming soon
- 🚧 **Face Recognition** - Coming soon
- 🚧 **AI Chat** - Coming soon

### Features
- ✅ **Dark/Light Mode** - Toggle in header
- ✅ **JWT Authentication** - Auto token refresh
- ✅ **Protected Routes** - Auto redirect
- ✅ **Toast Notifications** - Success/Error messages
- ✅ **Responsive Design** - Mobile-first
- ✅ **Modern UI** - Tailwind CSS + Framer Motion animations
- ✅ **State Management** - Zustand stores
- ✅ **API Integration** - Axios with interceptors
- ✅ **Type Safety** - Full TypeScript

### Components
- ✅ Button (primary, secondary, danger variants)
- ✅ Input (with labels and validation)
- ✅ Card (container with shadows)
- ✅ Loader (loading spinner)
- ✅ Sidebar (navigation)
- ✅ Header (theme toggle, notifications)

## 🔧 Backend Integration

The frontend is configured to proxy API requests to the Django backend:

- **API:** `http://localhost:8000/api` → `/api`
- **WebSocket:** `ws://localhost:8000/ws` → `/ws`

Make sure your Django backend is running on port 8000!

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Loader.tsx
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   ├── pages/          # Page components
│   │   ├── Login.tsx
│   │   └── Dashboard.tsx
│   ├── layouts/        # Layout components
│   │   └── DashboardLayout.tsx
│   ├── store/          # State management
│   │   ├── authStore.ts
│   │   └── themeStore.ts
│   ├── lib/            # Utilities
│   │   ├── api.ts      # Axios instance
│   │   └── types.ts    # TypeScript types
│   ├── App.tsx         # Main app with routing
│   ├── main.tsx        # Entry point
│   └── index.css       # Tailwind styles
├── tailwind.config.js  # Tailwind configuration
├── vite.config.ts      # Vite configuration
└── package.json        # Dependencies
```

## 🎨 Customization

### Theme Colors

Edit `tailwind.config.js` to customize colors:

```js
colors: {
  primary: {
    500: '#0ea5e9',  // Change primary color
    600: '#0284c7',
  },
}
```

### API URL

Edit `.env` to change backend URL:

```bash
VITE_API_URL=http://your-backend-url:8000/api
```

## 🐛 Troubleshooting

### Port Already in Use

```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3001
```

### API Connection Error

1. Check backend is running: `http://localhost:8000/api/`
2. Check CORS settings in Django `settings.py`
3. Verify `.env` file has correct `VITE_API_URL`

### Dark Mode Not Working

The theme is stored in localStorage. Clear it:

```js
// In browser console
localStorage.clear()
```

## 📝 Next Steps

1. **Test Login** - Login with `admin/admin123`
2. **Explore Dashboard** - View stats and cards
3. **Toggle Theme** - Click sun/moon icon in header
4. **Build More Pages** - Add Alerts, Incidents, Faces, etc.

## 🔥 Hot Reload

Vite supports **instant hot reload**. Just edit any file and see changes immediately!

## 📦 Build for Production

```powershell
npm run build
```

Production files will be in `dist/` folder.

## 🎯 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

---

**You're all set! 🚀 Run `npm run dev` and start coding!**
