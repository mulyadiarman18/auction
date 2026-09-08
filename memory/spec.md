# LelangOto MVP Spec

## Product
Responsive online vehicle auction catalog for visitors and bidder participants. The MVP focuses on browsing lots, viewing lot detail, and placing simulated bids persisted in MongoDB.

## Data model
- `lots`: vehicle metadata, auction status/times, pricing, increment, inspection, image, and location.
- `bids`: lot id, bidder name/type, amount, timestamp, and validity status.

## Key flows
1. Visitor opens the editorial home/catalog, filters or searches lots, and opens a lot detail page.
2. Demo bidder persona is selected in the header; no real authentication or payment is used.
3. Bidder chooses a quick increment or enters a custom amount at least current bid plus the lot increment; the API stores the bid and updates the lot current bid.
4. Dashboard shows the selected bidder's bid history and summary.

## Roles and auth
The MVP has visitor and bidder personas only. Authentication is intentionally mocked by a local demo persona selector; there are no admin credentials, payment integrations, or third-party services.

## Seed data
Six demo lots are written by `backend/seed.py`: live Porsche 911 GT3 RS and Audi R8, upcoming Impala, Mercedes 280SL, Koenigsegg, and an ended Dodge Challenger.