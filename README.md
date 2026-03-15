# Phân tích các yếu tố ảnh hưởng đến rating của phim

Bài thi GK môn Khoa học dữ liệu — Dữ liệu phim crawl từ The Movie Database (TMDB).

## Cấu trúc thư mục

```
GK_KHDL/
├── README.md                 # File này — hướng dẫn chạy
├── scrape.py                 # Mã nguồn crawl dữ liệu từ TMDB
├── raw data/                 # Dữ liệu thô sau khi crawl (chưa làm sạch)
│   └── data.xlsx
├── clean data/               # Dữ liệu đã làm sạch (sau bước tiền xử lý)
│   └── movies_clean.xlsx
└── notebooks/                # Notebook phân tích
    └── 01_phan_tich_rating_phim.ipynb
```

## Trình tự chạy chương trình

### 1. Thu thập dữ liệu thô (đã thực hiện / cần chạy lại)

- **Công cụ:** Python 3, thư viện: `requests`, `beautifulsoup4`, `pandas`, `openpyxl`, `lxml`
- **Cài đặt:**  
  `pip install requests beautifulsoup4 pandas openpyxl lxml`
- **Chạy crawl:**  
  `python scrape.py`  
  Nhập trang bắt đầu và trang kết thúc (vd: 1 và 50 để lấy >1000 phim). Kết quả lưu ra file `data.xlsx` (hoặc data1.xlsx, data2.xlsx nếu đã tồn tại).
- **Lưu dữ liệu thô:** Copy file `data.xlsx` vào thư mục **`raw data/`**.

### 2. Phân tích và làm sạch dữ liệu

- Cài thư viện: `pip install pandas numpy matplotlib seaborn scikit-learn jupyter openpyxl`
- Mở Jupyter từ **thư mục gốc** của project (GK_KHDL): `jupyter notebook`  
  Hoặc mở **`notebooks/01_phan_tich_rating_phim.ipynb`**.
- Chạy **toàn bộ cell** theo thứ tự từ trên xuống (Run All):
  - Load dữ liệu từ `raw data/data.xlsx`.
  - Thống kê mô tả, trực quan đơn biến, làm sạch, mã hóa thể loại, feature engineering, trực quan đa biến (heatmap, scatter, lmplot, jointplot, clustermap, t-SNE), kết luận.
  - Ô cuối cùng lưu dữ liệu đã làm sạch ra **`clean data/movies_clean.xlsx`**.

### 3. Kết quả cần có

- **raw data:** Chứa file Excel/csv thô từ crawl.
- **clean data:** Chứa file đã làm sạch (vd: `movies_clean.xlsx`).
- **notebook:** Đủ các phần: phát biểu bài toán, EDA, làm sạch, encoding, feature engineering, trực quan đa biến, kết luận, tài liệu tham khảo.

## Nguồn dữ liệu

- **Website:** https://www.themoviedb.org  
- **API:** The Movie Database (TMDB) API — dùng để lấy thông tin chi tiết phim (rating, thể loại, runtime, budget, …).  
- Cách thu thập: crawl danh sách phim theo trang từ TMDB, sau đó gọi API theo `movie_id` để lấy từng bản ghi.

## Yêu cầu môi trường

- Python >= 3.8
- Cài đặt: `pip install -r requirements.txt`  
  Hoặc: `pip install pandas numpy matplotlib seaborn scikit-learn jupyter openpyxl requests beautifulsoup4 lxml`

## Nộp bài

- Đặt tên folder: **"STTnhom - Tên đề tài"** (vd: `02 - Phan tich cac yeu to anh huong den rating phim`).
- Trong folder gồm: notebook(s), README, `scrape.py`, thư mục `raw data`, thư mục `clean data` (kích thước tối đa 20 MB).
