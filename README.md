# ClipMap · Vietflex Satellite Clip GIS

Ứng dụng WebGIS cắt hiển thị ảnh vệ tinh trực tiếp theo polygon với mặt nạ nghịch đảo.

- Trang chủ (sau khi GitHub Pages triển khai): https://xulytiengviet.github.io/clipmap/
- Cốt lõi: [vietflexmap@1.0.2](https://www.npmjs.com/package/vietflexmap/v/1.0.2), Leaflet và Leaflet.draw.
- Tải polygon GeoJSON EPSG:4326 hoặc vẽ trực tiếp; làm mờ vùng ngoài ranh giới và tô đường viền; xuất PNG và GeoJSON; giao diện responsive.
- Nguồn tham khảo ranh giới hành chính: [Vietflexmap/anhmap](https://github.com/Vietflexmap/anhmap). Dữ liệu từ ẢnhMap **chưa tự động nạp**; cần đưa GeoJSON vào công cụ. Không sử dụng ranh giới cho mục đích pháp lý trước khi xác minh.
- PNG yêu cầu ảnh tile có CORS cho phép và giấy phép sử dụng phù hợp. Bản đồ vệ tinh từ Esri World Imagery vẫn phải tuân thủ điều kiện Esri/nhà cung cấp; không hỗ trợ tải raster phân tích/GeoTIFF.
- Vietflexmap giữ nguyên lõi npm 1.0.2; nếu không khởi tạo được, hiển thị cảnh báo và dùng Leaflet dự phòng.

## Triển khai
Mã nguồn tĩnh tại `index.html`. Workflow `.github/workflows/pages.yml` tự triển khai nhánh `main`. Nếu chưa bật Pages, trong Settings → Pages, chọn **GitHub Actions**.

## Giấy phép
MIT © 2026 Long Ngo. Phần mềm bên thứ ba và dữ liệu nền tuân theo giấy phép riêng.

## Tối ưu ranh giới cấp xã trên Cloudflare R2

Ứng dụng hiện tải `index.json` trước và chỉ tải `provinces/<ma_tinh>.geojson` khi bấm **Cắt theo đơn vị đã chọn**. Không còn tải trực tiếp `VietnamWardBoundary2025.geojson` 193 MB vào trình duyệt.

### Chuẩn bị dữ liệu trên máy có Python

```bash
python -m pip install shapely
python tools/build_r2.py --provinces "Việt Nam (tỉnh thành) - 34.geojson" --wards "VietnamWardBoundary2025.geojson" --out dist-r2
```

Nếu kiểm tra đủ 34 tỉnh và 3.321 đơn vị thất bại, hãy kiểm tra dữ liệu gốc thay vì ép công cụ bỏ qua lỗi. Công cụ không tạo kết quả khi có xã không ghép được tỉnh. Chỉ dùng `--allow-count-mismatch` sau khi xác minh sự khác biệt.

Mở Cloudflare R2 → `ranhgioi` → Objects và tải **nội dung** của `dist-r2` (không bọc thêm thư mục): `index.json` và 34 file trong `provinces/`. Giữ nguyên tên object key và thiết lập CORS đọc GET/HEAD từ https://xulytiengviet.github.io.

**Lưu ý:** Việc cập nhật mã nguồn GitHub Pages không tự chuyển đổi hay tải các file R2. Chừng nào `index.json` chưa hiện diện trên public R2, ClipMap sẽ hiển thị lỗi thiếu chỉ mục, thay vì tải tệp 193 MB cũ.


## Bộ dữ liệu R2 đã chuẩn hóa (13/10/2026)

Hai GeoJSON nguồn được chuẩn hóa theo các trường `ma_tinh`, `ten_tinh`, `ma`, `tenhc`, `loai`, và xuất thành **34 shard cấp tỉnh** chứa tổng cộng **3.321** polygon cấp xã. Chỉ mục `index.json` theo schema `clipmap-r2-index-v1` liệt kê 34 tỉnh + 3.321 xã, tương thích mã hiện tại của ClipMap.

Cấu trúc Object Key trên Cloudflare R2 bucket `ranhgioi`:

```
index.json
provinces/01.geojson
provinces/04.geojson
...
provinces/96.geojson
```

Số hiệu file là `ma_tinh` của GeoJSON gốc, **không phải** số thứ tự 01–34. Giải nén gói ZIP rồi tải `index.json` lên gốc bucket và nội dung `provinces/` lên đúng prefix `provinces/`. Tệp nguồn `VietnamWardBoundary2025.geojson` cũ không còn được tải khi chọn đơn vị hành chính.

Các URL cần kiểm tra sau khi upload:
- https://pub-7dd53e3ae939474d8bbfe3cec7145b16.r2.dev/index.json
- https://pub-7dd53e3ae939474d8bbfe3cec7145b16.r2.dev/provinces/01.geojson

Không đưa API token hoặc secret của Cloudflare vào code front-end/GitHub.
