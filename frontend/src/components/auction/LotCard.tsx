import { motion } from "motion/react";
import { ArrowUpRight, Clock3, MapPin, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import type { Lot } from "@/types/auction";

interface LotCardProps { lot: Lot; featured?: boolean }

const money = (value: number) => `Rp ${(value / 1_000_000).toLocaleString("id-ID", { maximumFractionDigits: 0 })} jt`;

function countdown(end: string, status: Lot["status"]): string {
  if (status === "ENDED") return "Selesai";
  const distance = new Date(end).getTime() - Date.now();
  if (distance <= 0) return "Ditutup";
  const hours = Math.floor(distance / 3_600_000);
  const minutes = Math.floor((distance % 3_600_000) / 60_000);
  const seconds = Math.floor((distance % 60_000) / 1_000);
  return `${String(hours).padStart(2, "0")} : ${String(minutes).padStart(2, "0")} : ${String(seconds).padStart(2, "0")}`;
}

export function LotCard({ lot, featured = false }: LotCardProps) {
  return (
    <motion.article data-testid={`lot-card-${lot.id}`} whileHover={{ y: -6 }} transition={{ duration: 0.2, ease: "easeOut" }} className={`group overflow-hidden rounded-2xl border border-white/10 bg-[#111A33]/70 shadow-[0_8px_32px_rgba(0,0,0,0.2)] ${featured ? "lg:col-span-2" : ""}`}>
      <Link data-testid={`lot-card-link-${lot.id}`} to={`/lots/${lot.id}`} className="block">
        <div className={`relative overflow-hidden ${featured ? "aspect-[16/9]" : "aspect-[4/3]"}`}>
          <img data-testid={`lot-image-${lot.id}`} src={lot.image_url} alt={lot.title} className="h-full w-full object-cover transition duration-700 group-hover:scale-105" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#060A17] via-[#060A17]/15 to-transparent" />
          <div data-testid={`lot-status-${lot.id}`} className="absolute left-4 top-4 flex items-center gap-2">
            <Badge variant="outline" className={lot.status === "LIVE" ? "border-emerald-400/30 bg-emerald-500/15 text-emerald-300" : lot.status === "UPCOMING" ? "border-[#FF5E1F]/30 bg-[#FF5E1F]/15 text-[#ff9a74]" : "border-white/15 bg-[#0B132B]/80 text-slate-400"}>
              {lot.status === "LIVE" ? "● Live sekarang" : lot.status === "UPCOMING" ? "Segera dibuka" : "Lelang selesai"}
            </Badge>
          </div>
          <div data-testid={`lot-number-${lot.id}`} className="absolute right-4 top-5 font-mono text-[10px] tracking-[0.2em] text-white/60">{lot.lot_number}</div>
          <div className="absolute inset-x-4 bottom-4 flex items-end justify-between gap-3">
            <div>
              <p data-testid={`lot-category-${lot.id}`} className="mb-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[#F59E0B]">{lot.category}</p>
              <h3 data-testid={`lot-title-${lot.id}`} className="max-w-[440px] font-heading text-xl font-bold leading-tight text-[#FAF9F6] sm:text-2xl">{lot.title}</h3>
            </div>
            <span data-testid={`lot-open-link-${lot.id}`} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-white/20 bg-white/10 text-white backdrop-blur-sm transition group-hover:border-[#FF5E1F] group-hover:bg-[#FF5E1F]"><ArrowUpRight size={17} /></span>
          </div>
        </div>
        <div className="space-y-4 p-4 sm:p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p data-testid={`lot-current-label-${lot.id}`} className="text-[10px] uppercase tracking-[0.14em] text-slate-500">{lot.status === "ENDED" ? "Harga akhir" : "Bid tertinggi"}</p>
              <p data-testid={`lot-current-bid-${lot.id}`} className="mt-1 font-mono text-xl font-bold tracking-tight text-[#F59E0B]">{money(lot.current_bid)}</p>
            </div>
            <div data-testid={`lot-countdown-${lot.id}`} className="text-right">
              <p className="flex items-center justify-end gap-1 text-[10px] uppercase tracking-[0.14em] text-slate-500"><Clock3 size={11} /> {lot.status === "LIVE" ? "Berakhir dalam" : "Jadwal"}</p>
              <p className={`mt-1 font-mono text-sm font-semibold ${lot.status === "LIVE" ? "text-[#FAF9F6]" : "text-slate-300"}`}>{countdown(lot.auction_end, lot.status)}</p>
            </div>
          </div>
          <div className="flex items-center justify-between border-t border-white/10 pt-3 text-xs text-slate-400">
            <span data-testid={`lot-location-${lot.id}`} className="flex items-center gap-1.5"><MapPin size={13} className="text-[#FF5E1F]" /> {lot.location}</span>
            <span data-testid={`lot-verified-${lot.id}`} className="flex items-center gap-1 text-emerald-400"><ShieldCheck size={13} /> Terverifikasi</span>
          </div>
        </div>
      </Link>
    </motion.article>
  );
}