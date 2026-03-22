// /frontend/src/components/routing/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Loader2 } from 'lucide-react';

export default function ProtectedRoute() {
    // FIX 3: Granular selectors prevent unnecessary re-renders
    // const { isAuthenticated, isAuthLoading } = useAuthStore(); -This was the "Whole Store" Subscription
    // even if a profile picture changed, for e.g., it would have triggered a re-render.
    // Now we are specifically checking for 2 things only.
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    const isAuthLoading = useAuthStore((state) => state.isAuthLoading);

    if (isAuthLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
}
