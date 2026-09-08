import asyncio
from datetime import datetime, timedelta, timezone

from lib.db import client, db, ensure_indexes


IMAGE_URLS = {
    "excavator": "https://static.prod-images.emergentagent.com/jobs/60f06dda-eac4-468a-b91c-af503649b221/images/41c0f53f1f68842a25117fa3224c51e3e4c651d3789bf99261c9943d06d90632.jpeg",
    "dump_truck": "https://static.prod-images.emergentagent.com/jobs/60f06dda-eac4-468a-b91c-af503649b221/images/e3bbc5ee0b244f14f1af793c0ada1f7ae4e6b0dd8bbcd6d0c9ed2d9553ab7ad5.jpeg",
    "grader": "https://static.prod-images.emergentagent.com/jobs/60f06dda-eac4-468a-b91c-af503649b221/images/d93e32d28862ed28d6497129256605a62da45ae0e1a94b42e05272ceb18acfae.jpeg",
    "bulldozer": "https://static.prod-images.emergentagent.com/jobs/60f06dda-eac4-468a-b91c-af503649b221/images/e2e98628b6eeb8d6277d6174d633cb40423f97641a4bbe31b8b6231f2bf28bc0.jpeg",
    "articulated_truck": "https://static.prod-images.emergentagent.com/jobs/60f06dda-eac4-468a-b91c-af503649b221/images/36658c2985aff6fedceb6cec0cd311d3c6104e4962d35e0048e39517c94d4ec2.jpeg",
    "wheel_loader": "https://static.prod-images.emergentagent.com/jobs/60f06dda-eac4-468a-b91c-af503649b221/images/c6cd05d2e224d979ef66cc5a03523170be82c7e429ea3af3b04eef7e876dbd5a.jpeg",
}


async def seed() -> None:
    now = datetime.now(timezone.utc)
    lots = [
        {
            "id": "lot-001", "lot_number": "LLG-20260910-01-L001", "title": "Komatsu PC400LC-8 Hydraulic Excavator",
            "category": "Excavator", "status": "LIVE", "location": "Pool Sangatta, Kalimantan Timur", "image_url": IMAGE_URLS["excavator"],
            "gallery_urls": [IMAGE_URLS["excavator"]], "year": 2019, "mileage": "12.480 HM", "transmission": "Hydrostatic",
            "engine": "Komatsu SAA6D125E-5 · 345 HP", "grade": "Grade B", "inspection_score": 87,
            "seller_verified": True, "base_price": 1850000000, "current_bid": 2050000000, "minimum_increment": 25000000,
            "auction_start": now - timedelta(hours=1), "auction_end": now + timedelta(hours=2, minutes=18),
            "description": "Excavator produksi tambang dengan riwayat preventive maintenance terdokumentasi dan undercarriage dalam kondisi operasional.",
            "features": ["Bucket 2,2 m³", "Auto lubrication", "ROPS cabin", "Service history tersedia"], "vin": "KMTPC210H019001", "document_status": "Faktur & Form A tersedia",
            "auction_code": "LLG-20260910-01", "unit_number": "EXC-041", "hull_number": "PC400-041", "registration_code": "MPI-ORI-041", "brand": "Komatsu", "model_type": "PC400LC-8", "operating_hours": "12.480 HM", "seller_name": "PT Karya Mineral Nusantara", "pool_location": "Pool Sangatta", "document_completeness": ["Faktur", "Form A", "Laporan inspeksi"],
        },
        {
            "id": "lot-002", "lot_number": "LLG-20260910-01-L002", "title": "Komatsu HD785-7 Rigid Dump Truck",
            "category": "Dump Truck", "status": "UPCOMING", "location": "Pool Berau, Kalimantan Timur", "image_url": IMAGE_URLS["dump_truck"],
            "gallery_urls": [IMAGE_URLS["dump_truck"]], "year": 2018, "mileage": "18.210 HM", "transmission": "Automatic Powershift",
            "engine": "Komatsu SAA12V140E-3 · 1.200 HP", "grade": "Grade B", "inspection_score": 84,
            "seller_verified": True, "base_price": 3200000000, "current_bid": 3200000000, "minimum_increment": 50000000,
            "auction_start": now + timedelta(days=1), "auction_end": now + timedelta(days=1, hours=3),
            "description": "Rigid dump truck kapasitas 91 ton, siap inspeksi di pool dengan catatan perawatan powertrain lengkap.",
            "features": ["Payload 91 ton", "Retarder control", "Payload meter", "ROPS/FOPS cabin"], "vin": "KMTHD785J018002", "document_status": "Faktur & Form A tersedia",
            "auction_code": "LLG-20260910-01", "unit_number": "HDT-112", "hull_number": "HD785-112", "registration_code": "KY-HDT-112", "brand": "Komatsu", "model_type": "HD785-7", "operating_hours": "18.210 HM", "seller_name": "PT Bara Kaltim Abadi", "pool_location": "Pool Berau", "document_completeness": ["Faktur", "Form A", "Manual book"],
        },
        {
            "id": "lot-003", "lot_number": "LLG-20260910-01-L003", "title": "Caterpillar 16M Motor Grader",
            "category": "Motor Grader", "status": "LIVE", "location": "Pool Satui, Kalimantan Selatan", "image_url": IMAGE_URLS["grader"],
            "gallery_urls": [IMAGE_URLS["grader"]], "year": 2020, "mileage": "9.760 HM", "transmission": "Direct Drive Powershift",
            "engine": "CAT C13 ACERT · 297 HP", "grade": "Grade A", "inspection_score": 91,
            "seller_verified": True, "base_price": 2750000000, "current_bid": 2925000000, "minimum_increment": 25000000,
            "auction_start": now - timedelta(minutes=35), "auction_end": now + timedelta(hours=4, minutes=7),
            "description": "Motor grader untuk maintenance haul road, articulation dan circle drive telah melalui pemeriksaan fungsi.",
            "features": ["14 ft moldboard", "Auto articulation", "Ripper attachment", "Air-conditioned cabin"], "vin": "CAT0016MJT900003", "document_status": "Faktur tersedia",
            "auction_code": "LLG-20260910-01", "unit_number": "GRD-027", "hull_number": "16M-027", "registration_code": "MPI-ORI-027", "brand": "Caterpillar", "model_type": "16M", "operating_hours": "9.760 HM", "seller_name": "PT Mitra Tambang Sejahtera", "pool_location": "Pool Satui", "document_completeness": ["Faktur", "Laporan inspeksi"],
        },
        {
            "id": "lot-004", "lot_number": "LLG-20260912-01-L001", "title": "Komatsu D155A-6 Crawler Dozer",
            "category": "Bulldozer", "status": "UPCOMING", "location": "Pool Balikpapan, Kalimantan Timur", "image_url": IMAGE_URLS["bulldozer"],
            "gallery_urls": [IMAGE_URLS["bulldozer"]], "year": 2019, "mileage": "11.350 HM", "transmission": "TORQFLOW Powershift",
            "engine": "Komatsu SAA6D140E-5 · 354 HP", "grade": "Grade B", "inspection_score": 86,
            "seller_verified": True, "base_price": 2400000000, "current_bid": 2400000000, "minimum_increment": 25000000,
            "auction_start": now + timedelta(days=2), "auction_end": now + timedelta(days=2, hours=3),
            "description": "Crawler dozer heavy-duty dengan semi-U blade dan ripper, sesuai untuk ripping serta overburden push.",
            "features": ["Semi-U blade", "Multi-shank ripper", "ROPS canopy", "Undercarriage 72%"], "vin": "KMTD155A0190004", "document_status": "Faktur & Form A tersedia",
            "auction_code": "LLG-20260912-01", "unit_number": "DZR-063", "hull_number": "D155-063", "registration_code": "TK-063", "brand": "Komatsu", "model_type": "D155A-6", "operating_hours": "11.350 HM", "seller_name": "PT Karya Mineral Nusantara", "pool_location": "Pool Balikpapan", "document_completeness": ["Faktur", "Form A", "Service record"],
        },
        {
            "id": "lot-005", "lot_number": "LLG-20260905-01-L008", "title": "Volvo A40G Articulated Hauler",
            "category": "Articulated Truck", "status": "ENDED", "location": "Pool Morowali, Sulawesi Tengah", "image_url": IMAGE_URLS["articulated_truck"],
            "gallery_urls": [IMAGE_URLS["articulated_truck"]], "year": 2018, "mileage": "14.920 HM", "transmission": "Volvo PowerTronic",
            "engine": "Volvo D13J · 469 HP", "grade": "Grade C", "inspection_score": 78,
            "seller_verified": True, "base_price": 1950000000, "current_bid": 2175000000, "minimum_increment": 25000000,
            "auction_start": now - timedelta(days=4), "auction_end": now - timedelta(days=3, hours=21),
            "description": "Articulated hauler kapasitas 39 ton, unit terjual dan sedang menunggu proses pelunasan serta BAST.",
            "features": ["Payload 39 ton", "Automatic traction control", "On-board weighing", "Tailgate"], "vin": "VCE0A40GK003005", "document_status": "Faktur tersedia · BAST diproses",
            "auction_code": "LLG-20260905-01", "unit_number": "ADT-019", "hull_number": "A40G-019", "registration_code": "LV-ADT-019", "brand": "Volvo", "model_type": "A40G", "operating_hours": "14.920 HM", "seller_name": "PT Mineral Industri Timur", "pool_location": "Pool Morowali", "document_completeness": ["Faktur", "BAST proses"],
        },
        {
            "id": "lot-006", "lot_number": "LLG-20260912-01-L002", "title": "Caterpillar 980M Wheel Loader",
            "category": "Wheel Loader", "status": "UPCOMING", "location": "Pool Banjarmasin, Kalimantan Selatan", "image_url": IMAGE_URLS["wheel_loader"],
            "gallery_urls": [IMAGE_URLS["wheel_loader"]], "year": 2020, "mileage": "8.640 HM", "transmission": "Planetary Powershift",
            "engine": "CAT C13 ACERT · 386 HP", "grade": "Grade A", "inspection_score": 92,
            "seller_verified": True, "base_price": 2850000000, "current_bid": 2850000000, "minimum_increment": 25000000,
            "auction_start": now + timedelta(days=3), "auction_end": now + timedelta(days=3, hours=3),
            "description": "Wheel loader produksi dengan general purpose bucket dan kondisi powertrain sangat baik berdasarkan inspeksi terakhir.",
            "features": ["5,4 m³ bucket", "Ride control", "Payload system", "ROPS/FOPS cabin"], "vin": "CAT0980MJKT30006", "document_status": "Faktur, Form A, dan manual tersedia",
            "auction_code": "LLG-20260912-01", "unit_number": "WLD-034", "hull_number": "980M-034", "registration_code": "MPI-ORI-034", "brand": "Caterpillar", "model_type": "980M", "operating_hours": "8.640 HM", "seller_name": "PT Mitra Tambang Sejahtera", "pool_location": "Pool Banjarmasin", "document_completeness": ["Faktur", "Form A", "Manual book", "Laporan inspeksi"],
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