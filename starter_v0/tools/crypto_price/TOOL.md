# crypto_price Tool

Tra cứu giá tiền mã hóa (Cryptocurrency) thời gian thực theo đơn vị tiền tệ quy đổi (USD, EUR, VND...).

## Implementation Details

- Endpoint: CoinGecko Free Simple Price API (`api.coingecko.com`).
- No API key required.

## Arguments

- `symbol` (str, required): Tên tiền mã hóa ID trên CoinGecko (ví dụ: "bitcoin", "ethereum", "solana", "cardano", "binancecoin").
- `currency` (str, optional, default="usd"): Đơn vị tiền tệ so sánh (ví dụ: "usd", "eur", "vnd").

## Returns

Object dạng `dict`:
- `symbol`: Tên loại tiền mã hóa
- `currency`: Đơn vị tiền tệ so sánh
- `price`: Giá hiện tại
- `items`: Danh sách dữ liệu chi tiết
- `error`: Chuỗi thông báo lỗi (nếu có) hoặc `None`
