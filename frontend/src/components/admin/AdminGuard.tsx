import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { apiGet } from "@/lib/api";
import type { AdminUser } from "@/types/auction";

interface AdminGuardProps { children: (user: AdminUser) => ReactNode }

export function AdminGuard({ children }: AdminGuardProps) {
  const query = useQuery({ queryKey: ["admin-session"], queryFn: () => apiGet<AdminUser>("/admin/auth/me"), retry: false });
  if (query.isLoading) return <div data-testid="admin-session-loading" className="flex min-h-screen items-center justify-center bg-[#f6f7f9] text-sm text-slate-500">Memeriksa sesi pengelola...</div>;
  if (query.isError || !query.data) return <Navigate to="/admin/login" replace />;
  return children(query.data);
}