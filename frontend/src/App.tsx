// /frontend/src/App.tsx
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Layouts & Routes
import AuthLayout from './components/layout/AuthLayout';
import LoginForm from './pages/auth/LoginForm';
import RegisterForm from './pages/auth/RegisterForm';
import ProtectedRoute from './components/routing/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import { Toaster } from 'sonner';

function App() {
    const checkAuth = useAuthStore((state) => state.checkAuth);

    // Run exactly once when the React app mounts
    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    return (
        <BrowserRouter>
            <Toaster position="top-right" richColors />
            <Routes>
                {/* Public Auth Routes */}
                <Route element={<AuthLayout />}>
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/register" element={<RegisterForm />} />
                </Route>

                {/* Protected App Routes */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                    {/* Add more protected routes here like /portfolios, /chat */}
                </Route>

                {/* FIX 1: Explicit Root and Catch-All Routing */}
                {/* Send root traffic into the protected layout (which will redirect to login if needed) */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* Send 404 traffic to the public layout (which will redirect to dashboard if logged in) */}
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
