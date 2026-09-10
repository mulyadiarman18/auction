import { Banknote, ClipboardCheck, Crown, ShieldCheck } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiGet, apiPost } from "@/lib/api";
import type { AdminRole, AdminUser } from "@/types/auction";

interface AdminRoleBarProps { role: AdminRole; onRoleChange: (role: AdminRole) => void }

export function AdminRoleBar({ role }: AdminRoleBarProps) {
  const navigate = useNavigate(); const client = useQueryClient();
  const roleInfo = role === "super_admin" ? { label: "Super Admin", description: "Kelola sistem, operasional, finance, dan audit.", icon: Crown } : role === "finance" ? { label: "Finance MPI", description: "Konfirmasi pembayaran, deposit, invoice, dan settlement.", icon: Banknote } : role === "inspector" ? { label: "Inspektor", description: "Tugas pengecekan fisik, foto, dan grading unit.", icon: ClipboardCheck } : { label: "Reviewer", description: "Verifikasi legalitas pembeli dan penjual.", icon: ShieldCheck };
  const RoleIcon = roleInfo.icon;
  const session = useQuery({ queryKey: ["admin-session"], queryFn: () => apiGet<AdminUser>("/admin/auth/me"), retry: false });
  const logout = useMutation({ mutationFn: () => apiPost<void>("/admin/auth/logout"), onSuccess: () => { client.removeQueries({ queryKey: ["admin-session"] }); navigate("/admin/login", { replace: true }); } });
  return <section data-testid="admin-role-bar" className="mb-5 flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"><div><p data-testid="admin-role-label" className="text-xs font-semibold text-slate-700">{session.data?.name ?? "Pengelola"}</p><p data-testid="admin-role-description" className="mt-1 text-[11px] text-slate-500">{roleInfo.description}</p></div><div className="flex items-center gap-3"><div data-testid="admin-role-locked" className="flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-[#9A6700]"><RoleIcon size={14} />{roleInfo.label}</div><button data-testid="admin-logout-button" type="button" onClick={() => logout.mutate()} className="text-xs font-semibold text-red-600 hover:underline">Keluar</button></div></section>;
}