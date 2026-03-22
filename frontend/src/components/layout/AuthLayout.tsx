// /frontend/src/components/layout/AuthLayout.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Loader2 } from 'lucide-react';

export default function AuthLayout() {
    // Using selectors (Fix 3 applied here as well!)
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    const isAuthLoading = useAuthStore((state) => state.isAuthLoading);

    // Show a spinner while the initial checkAuth is running
    if (isAuthLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
        );
    }

    // FIX 2: If they are already logged in, bounce them to the app
    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
            <div className="w-full max-w-md space-y-8 bg-white p-8 rounded-xl shadow-lg border border-slate-100">
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-extrabold text-slate-900">
                        Equity Analysis
                    </h2>
                    <p className="mt-2 text-sm text-slate-600">
                        Secure your portfolio and chat data
                    </p>
                </div>
                <Outlet />
            </div>
        </div>
    );
}
