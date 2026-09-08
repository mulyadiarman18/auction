import { Link, useLocation } from "react-router-dom";
import { ChevronDown, Gauge, LayoutDashboard, Menu, Radio, UserRound } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Bidder } from "@/types/auction";

interface AuctionHeaderProps {
  bidder: Bidder;
  onBidderChange: (bidder: Bidder) => void;
}

const bidderOptions: Bidder[] = [
  { name: "Budi Santoso", type: "Verified Bidder VIP" },
  { name: "Siti Rahma", type: "Collector Grade" },
];

export function AuctionHeader({ bidder, onBidderChange }: AuctionHeaderProps) {
  const location = useLocation();
  const isDashboard = location.pathname === "/dashboard";

  return (
    <header data-testid="auction-header" className="sticky top-0 z-40 border-b border-white/10 bg-[#060A17]/85 backdrop-blur-xl">
      <div className="mx-auto flex h-[72px] max-w-[1400px] items-center justify-between px-5 sm:px-8 lg:px-12">
        <Link to="/" data-testid="navbar-brand-logo" className="group flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#FF5E1F] text-[#060A17] shadow-lg shadow-orange-950/40">
            <Gauge size={18} strokeWidth={2.8} />
          </span>
          <span data-testid="navbar-brand-name" className="font-heading text-lg font-bold tracking-[-0.04em] text-[#FAF9F6]">
            LELANG<span className="text-[#FF5E1F]">OTO</span>
          </span>
        </Link>

        <nav data-testid="desktop-navigation" className="hidden items-center gap-8 md:flex">
          <Link data-testid="navigation-catalog-link" to="/#catalog" className="text-sm font-medium text-slate-300 transition-colors hover:text-white">
            Katalog Lot
          </Link>
          <Link data-testid="navigation-how-it-works-link" to="/#how-it-works" className="text-sm font-medium text-slate-300 transition-colors hover:text-white">
            Cara Ikut
          </Link>
          <Link data-testid="navigation-dashboard-link" to="/dashboard" className={isDashboard ? "text-sm font-semibold text-[#FF5E1F]" : "text-sm font-medium text-slate-300 transition-colors hover:text-white"}>
            Dashboard Saya
          </Link>
        </nav>

        <div data-testid="bidder-profile-controls" className="flex items-center gap-2 sm:gap-3">
          <div data-testid="bidder-persona-selector" className="group relative hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] py-1.5 pl-2 pr-3 sm:flex">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#F59E0B]/15 text-[#F59E0B]"><UserRound size={14} /></span>
            <label data-testid="bidder-persona-label" htmlFor="bidder-persona" className="sr-only">Pilih persona bidder</label>
            <select
              id="bidder-persona"
              data-testid="bidder-persona-select"
              value={bidder.name}
              onChange={(event) => {
                const next = bidderOptions.find((option) => option.name === event.target.value);
                if (next) onBidderChange(next);
              }}
              className="max-w-[124px] cursor-pointer appearance-none bg-transparent pr-4 text-xs font-semibold text-[#FAF9F6] outline-none"
            >
              {bidderOptions.map((option) => <option data-testid={`bidder-option-${option.name.toLowerCase().replaceAll(" ", "-")}`} key={option.name} value={option.name} className="bg-[#0B132B]">{option.name}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 text-slate-500" size={13} />
          </div>
          <Link data-testid="header-dashboard-button" to="/dashboard" className={buttonVariants({ variant: "outline", size: "sm", className: "hidden border-white/15 bg-white/[0.03] text-slate-200 hover:bg-white/10 hover:text-white sm:inline-flex" })}>
            <LayoutDashboard size={15} />
            <span>Dashboard</span>
          </Link>
          <Button data-testid="mobile-menu-button" variant="ghost" size="icon" className="text-slate-300 hover:bg-white/10 hover:text-white md:hidden" aria-label="Buka menu">
            <Menu size={20} />
          </Button>
        </div>
      </div>
      <div data-testid="live-auction-ticker" className="border-t border-white/5 bg-[#0B132B]/60">
        <div className="mx-auto flex max-w-[1400px] items-center gap-2 px-5 py-2 text-[10px] font-mono uppercase tracking-[0.16em] text-slate-400 sm:px-8 lg:px-12">
          <Radio size={12} className="text-emerald-400" />
          <span data-testid="live-auction-ticker-label">Live room aktif</span>
          <Badge data-testid="live-auction-ticker-badge" variant="outline" className="ml-1 border-emerald-500/30 bg-emerald-500/10 px-1.5 py-0 text-[9px] text-emerald-400">2 lot</Badge>
          <span data-testid="live-auction-ticker-message" className="hidden text-slate-500 sm:inline">· penawaran simulasi tersimpan real-time</span>
        </div>
      </div>
    </header>
  );
}