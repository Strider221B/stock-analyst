// /frontend/src/pages/auth/RegisterForm.tsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const registerSchema = z.object({
    email: z.string().email({ message: "Invalid email address" }),
    password: z.string()
        .min(8, { message: "Password must be at least 8 characters" })
        .max(128, { message: "Password cannot exceed 128 characters" })
        .regex(/[A-Z]/, { message: "Must contain at least one uppercase letter" })
        .regex(/[a-z]/, { message: "Must contain at least one lowercase letter" })
        .regex(/\d/, { message: "Must contain at least one number" })
        .regex(/[!@#$%^&*(),.?":{}|<>]/, { message: "Must contain at least one special character" }),
    confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterForm() {
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login);
    const [error, setError] = useState<string | null>(null);

    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterFormValues>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormValues) => {
        try {
            setError(null);
            const _envUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const baseURL = _envUrl === '/' ? '' : _envUrl;

            // 1. Hit your backend register route
            await axios.post(`${baseURL}/api/auth/register`, {
                email: data.email,
                password: data.password
            });

            // 2. Immediately log them in using the Zustand action
            const formData = new URLSearchParams();
            formData.append('username', data.email);
            formData.append('password', data.password);
            await login(formData);

            // 3. Send them to the app
            navigate('/dashboard', { replace: true });
        } catch (err: any) {

            // Only log the full error in development mode
            // Vite automatically injects a boolean flag called import.meta.env.DEV that is true when you run npm run dev
            // and false when you run npm run build.
            if (import.meta.env.DEV) {
                console.error("Auth Failure:", err);
            }

            const detail = err.response?.data?.detail;

            // 1. If FastAPI sends a standard string error message (like 400 Bad Request)
            if (typeof detail === 'string') {
                setError(detail);
            }
            // 2. If FastAPI sends a Pydantic Validation Error array (422 Unprocessable Entity)
            else if (Array.isArray(detail)) {
                // Extracts just the readable messages and joins them with a comma
                const messages = detail.map((e: any) => `${e.loc[e.loc.length - 1]}: ${e.msg}`);
                setError(messages.join(', '));
            }
            // 3. Fallback for network crashes
            else {
                setError("An unexpected error occurred. Please try again.");
            }
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">{error}</div>}
            <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" {...register('email')} />
                {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" {...register('password')} />
                {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
            </div>
            <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input id="confirmPassword" type="password" {...register('confirmPassword')} />
                {errors.confirmPassword && <p className="text-xs text-red-500">{errors.confirmPassword.message}</p>}
            </div>
            <Button type="submit" className="w-full mt-4" disabled={isSubmitting}>
                {isSubmitting ? 'Creating account...' : 'Create account'}
            </Button>
            <p className="text-center text-sm text-slate-600">
                Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Sign in</Link>
            </p>
        </form>
    );
}
