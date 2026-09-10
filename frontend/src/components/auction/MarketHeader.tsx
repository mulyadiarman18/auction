import { Link, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Bell, ChevronDown, LayoutDashboard, MapPin, Search, ShoppingBag, UserRound } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiGet } from "@/lib/api";
import type { AdminUser, Bidder } from "@/types/auction";

interface MarketHeaderProps {
  bidder: Bidder;
  onBidderChange: (bidder: Bidder) => void;
  search?: string;
  onSearchChange?: (value: string) => void;
}

const defaultBidderOptions: Bidder[] = [
  { name: "Budi Santoso", type: "Verified Bidder VIP" },
  { name: "Siti Rahma", type: "Collector Grade" },
];

export function AuctionHeader({ bidder, onBidderChange, search = "", onSearchChange }: MarketHeaderProps) {
  const location = useLocation();
  const isDashboard = location.pathname === "/dashboard";
  const isAdmin = location.pathname.startsWith("/admin");
  const adminSession = useQuery({ queryKey: ["admin-session"], queryFn: () => apiGet<AdminUser>("/admin/auth/me"), enabled: isAdmin, retry: false });
  const adminRole = adminSession.data?.role;
  const bidderOptions = defaultBidderOptions.some((option) => option.name === bidder.name) ? defaultBidderOptions : [bidder, ...defaultBidderOptions];

  return (
    <header data-testid="auction-header" className="sticky top-0 z-40 border-b border-slate-200 bg-white shadow-[0_2px_8px_rgba(0,0,0,0.05)]">
      <div className="mx-auto flex max-w-[1240px] items-center gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link to="/" data-testid="navbar-brand-logo" className="flex shrink-0 items-center gap-2.5">
          <span data-testid="navbar-brand-name" className="font-heading text-xl font-bold tracking-[-0.05em] text-[#202124]">MIT <span className="text-[#B77900]">Auction</span></span>
        </Link>

        <div data-testid="marketplace-search" className="relative hidden min-w-0 flex-1 md:block">
          <Search size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <label data-testid="marketplace-search-label" htmlFor="marketplace-search-input" className="sr-only">Cari kendaraan</label>
          <input id="marketplace-search-input" data-testid="marketplace-search-input" value={search} onChange={(event) => onSearchChange?.(event.target.value)} placeholder="Cari unit, no. lambung, merk, atau pool..." className="h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-4 text-sm text-slate-700 outline-none transition focus:border-[#F5B800] focus:bg-white focus:ring-2 focus:ring-[#F5B800]/20" />
        </div>

        <div data-testid="marketplace-location" className="hidden items-center gap-2 border-l border-slate-200 pl-4 lg:flex"><MapPin size={16} className="text-[#B77900]" /><div><p className="text-[10px] text-slate-400">Pool utama</p><p data-testid="marketplace-location-value" className="text-xs font-semibold text-slate-700">Kalimantan</p></div></div>
        <button data-testid="marketplace-notification-button" type="button" className="hidden rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-[#03AC0E] sm:block" aria-label="Notifikasi"><Bell size={19} /></button>
        <Link data-testid="marketplace-bag-button" to="/dashboard" className="hidden rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-[#03AC0E] sm:block"><ShoppingBag size={19} /></Link>
        <div data-testid="bidder-persona-selector" className="group relative flex items-center gap-2 border-l border-slate-200 pl-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#FFF4C2] text-[#9A6700]"><UserRound size={15} /></span>
          <label data-testid="bidder-persona-label" htmlFor="bidder-persona" className="sr-only">Pilih persona bidder</label>
          <select id="bidder-persona" data-testid="bidder-persona-select" value={bidder.name} onChange={(event) => { const next = bidderOptions.find((option) => option.name === event.target.value); if (next) onBidderChange(next); }} className="max-w-[112px] cursor-pointer appearance-none bg-transparent pr-4 text-xs font-semibold text-slate-700 outline-none">
            {bidderOptions.map((option) => <option data-testid={`bidder-option-${option.name.toLowerCase().replaceAll(" ", "-")}`} key={option.name} value={option.name}>{option.name}</option>)}
          </select>
          <ChevronDown className="pointer-events-none absolute right-0 text-slate-400" size={13} />
        </div>
        <Link data-testid="header-dashboard-button" to="/dashboard" className={buttonVariants({ size: "sm", className: `hidden gap-1.5 bg-[#202124] text-white hover:bg-black sm:inline-flex ${isDashboard ? "ring-2 ring-[#F5B800]/40" : ""}` })}><LayoutDashboard size={15} /> <span className="hidden lg:inline">Dashboard</span></Link>
      </div>
      <nav data-testid="marketplace-navigation" className="hidden border-t border-slate-100 sm:block">
        <div className="mx-auto flex max-w-[1240px] items-center gap-6 px-4 py-2.5 text-xs text-slate-500 sm:px-6 lg:px-8"><Link data-testid="navigation-catalog-link" to="/#catalog" className="font-semibold text-slate-700 hover:text-[#B77900]">Katalog unit</Link><Link data-testid="navigation-sessions-link" to="/sessions" className="hover:text-[#B77900]">Jadwal lelang</Link>{!isAdmin && <><Link data-testid="navigation-how-it-works-link" to="/#how-it-works" className="hover:text-[#B77900]">Cara ikut lelang</Link><Link data-testid="navigation-register-link" to="/register" className="hover:text-[#B77900]">Daftar member</Link><Link data-testid="navigation-seller-link" to="/seller" className="hover:text-[#B77900]">Portal vendor</Link></>}{isAdmin && (adminRole === "super_admin" || adminRole === "reviewer") && <Link data-testid="navigation-admin-approvals-link" to="/admin/approvals" className="font-semibold text-[#B77900]">Approval legalitas</Link>}{isAdmin && adminRole === "super_admin" && <><Link data-testid="navigation-admin-operations-link" to="/admin/operations" className="font-semibold text-[#B77900]">Operasional</Link><Link data-testid="navigation-admin-inspections-link" to="/admin/inspections" className="font-semibold text-[#B77900]">Inspeksi</Link></>}{isAdmin && (adminRole === "super_admin" || adminRole === "finance") && <Link data-testid="navigation-admin-finance-link" to="/admin/finance" className="font-semibold text-[#B77900]">Finance</Link>}{isAdmin && adminRole === "inspector" && <Link data-testid="navigation-inspector-link" to="/admin/inspections" className="font-semibold text-[#B77900]">Tugas inspeksi</Link>}<span data-testid="marketplace-shipping-note" className="ml-auto flex items-center gap-1.5 text-slate-400"><Badge data-testid="marketplace-live-badge" className="bg-[#FFF4C2] px-1.5 py-0 text-[9px] text-[#8A5B00] hover:bg-[#FFF4C2]">LIVE</Badge> Selasa & Jumat</span></div>
      </nav>
    </header>
  );
}