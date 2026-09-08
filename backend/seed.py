import asyncio
from datetime import datetime, timedelta, timezone

from lib.db import client, db, ensure_indexes


IMAGE_URLS = {
    "porsche": "https://images.unsplash.com/photo-1785422850431-330836f00286?crop=entropy&cs=srgb&fm=jpg&q=85",
    "impala": "https://images.unsplash.com/photo-1587750059638-e7e8c43b99fc?crop=entropy&cs=srgb&fm=jpg&q=85",
    "audi": "https://images.unsplash.com/photo-1567808291548-fc3ee04dbcf0?crop=entropy&cs=srgb&fm=jpg&q=85",
    "mercedes": "https://images.unsplash.com/photo-1523828446771-151afb8374f1?crop=entropy&cs=srgb&fm=jpg&q=85",
    "dodge": "https://images.unsplash.com/photo-1587750113469-d2ba0241e8f?crop=entropy&cs=srgb&fm=jpg&q=85",
    "koenigsegg": "https://images.unsplash.com/photo-1780901833117-86ade3ac08fc?crop=entropy&cs=srgb&fm=jpg&q=85",
}


async def seed() -> None:
    now = datetime.now(timezone.utc)
    lots = [
        {
            "id": "lot-001", "lot_number": "L-001", "title": "2022 Porsche 911 GT3 RS Touring Package",
            "category": "Supercar", "status": "LIVE", "location": "Jakarta Selatan", "image_url": IMAGE_URLS["porsche"],
            "gallery_urls": [IMAGE_URLS["porsche"]], "year": 2022, "mileage": "2.400 KM", "transmission": "PDK 7-Speed",
            "engine": "4.0L Atmospheric Flat-6 · 525 HP", "grade": "Grade A+", "inspection_score": 99,
            "seller_verified": True, "base_price": 4500000000, "current_bid": 4850000000, "minimum_increment": 50000000,
            "auction_start": now - timedelta(hours=1), "auction_end": now + timedelta(hours=2, minutes=18),
            "description": "Unit koleksi dengan spesifikasi Touring Package, dirawat penuh di authorized service center.",
            "features": ["Carbon bucket seats", "Sport Chrono Package", "Porsche Ceramic Composite Brake"], "vin": "WP0ZZZ99ZNS000001", "document_status": "BPKB & STNK lengkap",
        },
        {
            "id": "lot-002", "lot_number": "L-002", "title": "1964 Chevrolet Impala SS Convertible Black Edition",
            "category": "Classic / Vintage", "status": "UPCOMING", "location": "Bandung", "image_url": IMAGE_URLS["impala"],
            "gallery_urls": [IMAGE_URLS["impala"]], "year": 1964, "mileage": "45.000 Miles", "transmission": "Manual 4-Speed",
            "engine": "5.4L V8 Turbo-Thrift", "grade": "Collector Restoration", "inspection_score": 96,
            "seller_verified": True, "base_price": 1100000000, "current_bid": 1250000000, "minimum_increment": 25000000,
            "auction_start": now + timedelta(days=1), "auction_end": now + timedelta(days=1, hours=3),
            "description": "Convertible klasik dengan restorasi detail dan dokumentasi sejarah kendaraan yang rapi.",
            "features": ["Matching numbers", "Black leather interior", "Power convertible top"], "vin": "41467S000002", "document_status": "Dokumen historis tersedia",
        },
        {
            "id": "lot-003", "lot_number": "L-003", "title": "2023 Audi R8 V10 Performance Coupe",
            "category": "Supercar", "status": "LIVE", "location": "Surabaya", "image_url": IMAGE_URLS["audi"],
            "gallery_urls": [IMAGE_URLS["audi"]], "year": 2023, "mileage": "1.200 KM", "transmission": "S Tronic Dual-Clutch",
            "engine": "5.2L FSI V10 · 620 HP", "grade": "Grade A", "inspection_score": 98,
            "seller_verified": True, "base_price": 3300000000, "current_bid": 3600000000, "minimum_increment": 50000000,
            "auction_start": now - timedelta(minutes=35), "auction_end": now + timedelta(hours=4, minutes=7),
            "description": "R8 V10 Performance dengan kilometer rendah, siap untuk kolektor maupun driving experience.",
            "features": ["Laser headlights", "Bang & Olufsen audio", "Carbon exterior package"], "vin": "WUAZZZFXXPA000003", "document_status": "BPKB & STNK lengkap",
        },
        {
            "id": "lot-004", "lot_number": "L-004", "title": "1971 Mercedes-Benz 280SL Pagoda W113",
            "category": "Classic / Vintage", "status": "UPCOMING", "location": "Jakarta Barat", "image_url": IMAGE_URLS["mercedes"],
            "gallery_urls": [IMAGE_URLS["mercedes"]], "year": 1971, "mileage": "32.000 KM", "transmission": "Automatic 4-Speed",
            "engine": "2.8L Inline-6 M130", "grade": "Matching Numbers", "inspection_score": 97,
            "seller_verified": True, "base_price": 1950000000, "current_bid": 2100000000, "minimum_increment": 25000000,
            "auction_start": now + timedelta(days=2), "auction_end": now + timedelta(days=2, hours=3),
            "description": "Pagoda W113 dengan siluet ikonik dan kondisi mekanis yang telah melalui inspeksi menyeluruh.",
            "features": ["Pagoda hardtop", "Restored wood trim", "Period-correct wheels"], "vin": "11304412000004", "document_status": "Dokumen lengkap",
        },
        {
            "id": "lot-005", "lot_number": "L-005", "title": "2021 Dodge Challenger SRT Hellcat Widebody",
            "category": "Muscle Car", "status": "ENDED", "location": "BSD Tangerang", "image_url": IMAGE_URLS["dodge"],
            "gallery_urls": [IMAGE_URLS["dodge"]], "year": 2021, "mileage": "5.800 KM", "transmission": "TorqueFlite 8-Speed Auto",
            "engine": "6.2L Supercharged HEMI V8 · 717 HP", "grade": "Grade A", "inspection_score": 95,
            "seller_verified": True, "base_price": 2200000000, "current_bid": 2450000000, "minimum_increment": 50000000,
            "auction_start": now - timedelta(days=4), "auction_end": now - timedelta(days=3, hours=21),
            "description": "Muscle car modern dengan widebody stance dan karakter mesin supercharged yang agresif.",
            "features": ["Widebody fender", "Brembo performance brakes", "Launch control"], "vin": "2C3CDZC9XMH000005", "document_status": "Terjual · settlement berjalan",
        },
        {
            "id": "lot-006", "lot_number": "L-006", "title": "2024 Koenigsegg Hypercar Studio Concept",
            "category": "Hypercar", "status": "UPCOMING", "location": "Jakarta Selatan · Private Vault", "image_url": IMAGE_URLS["koenigsegg"],
            "gallery_urls": [IMAGE_URLS["koenigsegg"]], "year": 2024, "mileage": "150 KM", "transmission": "9-Speed LST",
            "engine": "5.0L Twin-Turbo V8 + E-Motor · 1.600 HP", "grade": "Showroom New", "inspection_score": 100,
            "seller_verified": True, "base_price": 17000000000, "current_bid": 18500000000, "minimum_increment": 100000000,
            "auction_start": now + timedelta(days=3), "auction_end": now + timedelta(days=3, hours=3),
            "description": "Unit eksklusif dengan alokasi private vault dan sesi viewing khusus berdasarkan appointment.",
            "features": ["Hybrid powertrain", "Carbon monocoque", "Private viewing available"], "vin": "YS3GNN0C8RA000006", "document_status": "Dokumen import tersedia",
        },
    ]
    await db.bids.delete_many({})
    await db.lots.delete_many({})
    await db.lots.insert_many(lots)
    await ensure_indexes()
    client.close()
    print(f"Seeded {len(lots)} auction lots")


if __name__ == "__main__":
    asyncio.run(seed())