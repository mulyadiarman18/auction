export type LotStatus = "LIVE" | "UPCOMING" | "ENDED";

export interface Lot {
  id: string;
  lot_number: string;
  title: string;
  category: string;
  status: LotStatus;
  location: string;
  image_url: string;
  gallery_urls: string[];
  year: number;
  mileage: string;
  transmission: string;
  engine: string;
  grade: string;
  inspection_score: number;
  seller_verified: boolean;
  base_price: number;
  current_bid: number;
  minimum_increment: number;
  auction_start: string;
  auction_end: string;
  description: string;
  features: string[];
  vin: string;
  document_status: string;
}

export interface Bid {
  id: string;
  lot_id: string;
  bidder_name: string;
  bidder_type: string;
  amount: number;
  created_at: string;
  status: "VALID" | "OUTBID";
}

export interface Bidder {
  name: string;
  type: string;
}