import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowUpRight, CheckCircle2, Gavel, LockKeyhole, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError, apiPost } from "@/lib/api";
import type { Bid, Bidder, Lot } from "@/types/auction";

interface BidPanelProps { lot: Lot; bids: Bid[]; bidder: Bidder }

const money = (value: number) => `Rp ${value.toLocaleString("id-ID")}`;

export function BidPanel({ lot, bids, bidder }: BidPanelProps) {
  const queryClient = useQueryClient();
  const minimum = useMemo(() => lot.current_bid + lot.minimum_increment, [lot.current_bid, lot.minimum_increment]);
  const [amount, setAmount] = useState(String(minimum));

  useEffect(() => setAmount(String(minimum)), [minimum]);

  const mutation = useMutation({
    mutationFn: (bidAmount: number) => apiPost<Bid>(`/lots/${lot.id}/bids`, { bidder_name: bidder.name, bidder_type: bidder.type, amount: bidAmount }),
    onSuccess: async (bid) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["lot", lot.id] }),
        queryClient.invalidateQueries({ queryKey: ["lot-bids", lot.id] }),
        queryClient.invalidateQueries({ queryKey: ["my-bids", bidder.name] }),
      ]);
      toast.success("Penawaran berhasil dicatat", { description: `${bidder.name} kini memimpin di ${money(bid.amount)}` });
    },
    onError: (error) => {
      const message = error instanceof ApiError && typeof error.body === "object" && error.body !== null && "detail" in error.body ? String(error.body.detail) : "Penawaran belum dapat diproses.";
      toast.error("Bid belum berhasil", { description: message });
    },
  });

  const submitBid = (rawAmount: number) => {
    if (lot.status !== "LIVE" || mutation.isPending) return;
    mutation.mutate(rawAmount);
  };

  return (
    <aside data-testid="bid-panel" className="relative overflow-hidden rounded-2xl border border-[#FF5E1F]/30 bg-[#111A33]/90 p-5 shadow-[0_18px_60px_rgba(0,0,0,0.32)] sm:p-6">
      <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-[#FF5E1F]/15 blur-3xl" />
      <div className="relative">
        <div data-testid="bid-panel-heading" className="flex items-center justify-between border-b border-white/10 pb-4">
          <div>
            <p className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-[#FF8e68]"><Gavel size={13} /> Bidder room</p>
            <h2 data-testid="bid-panel-title" className="mt-2 font-heading text-xl font-bold text-[#FAF9F6]">Ajukan penawaran</h2>
          </div>
          <span data-testid="bidder-identity-badge" className="rounded-full border border-emerald-500/25 bg-emerald-500/10 px-2.5 py-1 text-[10px] font-semibold text-emerald-300">{bidder.name}</span>
        </div>

        <div data-testid="bid-current-value" className="py-5">
          <p className="text-xs text-slate-400">Bid tertinggi saat ini</p>
          <p className="mt-1 font-mono text-3xl font-bold tracking-tight text-[#F59E0B]">{money(lot.current_bid)}</p>
          <p data-testid="bid-minimum-hint" className="mt-2 text-xs text-slate-500">Minimum berikutnya <span className="font-mono text-slate-300">{money(minimum)}</span></p>
        </div>

        <div data-testid="quick-bid-actions" className="grid grid-cols-3 gap-2">
          {[5_000_000, 10_000_000, 25_000_000].map((increment) => (
            <Button key={increment} data-testid={`quick-bid-increment-${increment / 1_000_000}m`} type="button" variant="outline" size="sm" disabled={lot.status !== "LIVE" || mutation.isPending} onClick={() => submitBid(minimum + increment)} className="border-white/10 bg-white/[0.03] text-xs text-slate-200 hover:border-[#FF5E1F]/60 hover:bg-[#FF5E1F]/10 hover:text-white">
              <Plus size={12} /> {increment / 1_000_000} jt
            </Button>
          ))}
        </div>
        <div className="mt-4 flex gap-2">
          <label data-testid="bid-amount-label" htmlFor="bid-amount-input" className="sr-only">Nominal bid</label>
          <Input id="bid-amount-input" data-testid="bid-amount-input" inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value.replace(/\D/g, ""))} className="h-12 border-white/10 bg-[#060A17]/80 font-mono text-sm text-white focus:border-[#FF5E1F] focus:ring-[#FF5E1F]/30" />
          <Button data-testid={`place-bid-button-${lot.id}`} type="button" disabled={lot.status !== "LIVE" || mutation.isPending || Number(amount) < minimum} onClick={() => submitBid(Number(amount))} className="h-12 shrink-0 bg-[#FF5E1F] px-4 font-bold text-white shadow-lg shadow-orange-950/40 hover:bg-[#E0480C]">
            {mutation.isPending ? "Mengirim..." : "Bid sekarang"} <ArrowUpRight size={16} />
          </Button>
        </div>

        <div data-testid="bidder-security-note" className="mt-4 flex items-center gap-2 text-[11px] leading-relaxed text-slate-500"><LockKeyhole size={13} className="shrink-0 text-slate-400" /> Simulasi aman · bid tersimpan untuk riwayat bidder ini</div>

        <div data-testid="recent-bid-list" className="mt-6 border-t border-white/10 pt-4">
          <div className="mb-3 flex items-center justify-between"><p data-testid="recent-bid-list-title" className="text-xs font-semibold text-slate-300">Aktivitas terakhir</p><span data-testid="recent-bid-count" className="font-mono text-[10px] text-slate-500">{bids.length} bid</span></div>
          {bids.slice(0, 3).map((bid) => <div data-testid={`bid-history-item-${bid.id}`} key={bid.id} className="flex items-center justify-between border-b border-white/5 py-2 text-xs last:border-0"><span data-testid={`bid-history-bidder-${bid.id}`} className="text-slate-400">{bid.bidder_name}</span><span data-testid={`bid-history-amount-${bid.id}`} className="font-mono font-semibold text-slate-200">{money(bid.amount)}</span></div>)}
          {bids.length === 0 && <p data-testid="bid-history-empty" className="text-xs text-slate-500">Belum ada bid. Jadilah yang pertama.</p>}
        </div>
        {mutation.isSuccess && <p data-testid="bid-success-confirmation" className="mt-3 flex items-center gap-2 text-xs text-emerald-300"><CheckCircle2 size={14} /> Penawaran terakhir tersimpan</p>}
      </div>
    </aside>
  );
}