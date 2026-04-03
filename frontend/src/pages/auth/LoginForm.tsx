// /frontend/src/pages/auth/LoginForm.tsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuthStore } from '@/store/authStore';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const loginSchema = z.object({
    email: z.string().email({ message: "Invalid email address" }),
    password: z.string().min(1, { message: "Password is required" }),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginForm() {
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login);
    const [error, setError] = useState<string | null>(null);

    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormValues) => {
        try {
            setError(null);
            await login({ username: data.email, password: data.password });
            navigate('/dashboard', { replace: true });
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                const detail = error.response?.data?.detail;
                if (typeof detail === 'string') {
                    setError(detail);
                } else if (Array.isArray(detail)) {
                    const messages = detail.map((e: { loc: string[]; msg: string }) =>
                        `${e.loc[e.loc.length - 1]}: ${e.msg}`
                    );
                    setError(messages.join(', '));
                } else {
                    setError("Invalid credentials. Please try again.");
                }
            } else {
                setError("An unexpected error occurred. Please try again.");
            }
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {error && (
                <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md border border-red-200">
                    {error}
                </div>
            )}
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
            <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
            <p className="text-center text-sm text-slate-600">
                Don't have an account? <Link to="/register" className="text-blue-600 hover:underline">Register</Link>
            </p>
        </form>
    );
}
