import { Crown, ShieldCheck } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiGet, apiPost } from "@/lib/api";
import type { AdminRole, AdminUser } from "@/types/auction";

interface AdminRoleBarProps { role: AdminRole; onRoleChange: (role: AdminRole) => void }

export function AdminRoleBar({ role }: AdminRoleBarProps) {
  const navigate = useNavigate(); const client = useQueryClient();
  const session = useQuery({ queryKey: ["admin-session"], queryFn: () => apiGet<AdminUser>("/admin/auth/me"), retry: false });
  const logout = useMutation({ mutationFn: () => apiPost<void>("/admin/auth/logout"), onSuccess: () => { client.removeQueries({ queryKey: ["admin-session"] }); navigate("/admin/login", { replace: true }); } });
  return <section data-testid="admin-role-bar" className="mb-5 flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"><div><p data-testid="admin-role-label" className="text-xs font-semibold text-slate-700">{session.data?.name ?? "Pengelola"}</p><p data-testid="admin-role-description" className="mt-1 text-[11px] text-slate-500">{role === "super_admin" ? "Super Admin · kelola lot, jadwal, hasil, dan approval peserta." : "Reviewer · meninjau, menyetujui, atau menolak peserta."}</p></div><div className="flex items-center gap-3"><div data-testid="admin-role-locked" className="flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-[#03AC0E]">{role === "super_admin" ? <Crown size={14} /> : <ShieldCheck size={14} />}{role === "super_admin" ? "Super Admin" : "Reviewer"}</div><button data-testid="admin-logout-button" type="button" onClick={() => logout.mutate()} className="text-xs font-semibold text-red-600 hover:underline">Keluar</button></div></section>;
}