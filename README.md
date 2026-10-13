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