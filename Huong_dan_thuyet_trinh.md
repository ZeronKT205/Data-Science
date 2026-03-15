# Hướng dẫn thuyết trình bài GK

(Đọc file này song song với notebook để chuẩn bị slide/thuyết trình.)

## 1. Mở đầu & phát biểu bài toán
- Giới thiệu đề tài: **phân tích các yếu tố ảnh hưởng đến rating của phim**.
- Giải thích: rating (Y) là biến số thực → **bài toán hồi quy (regression)**.
- Nêu 2 câu hỏi chính:
  - Dữ liệu hiện có có **đủ và phù hợp** để xây dựng mô hình dự đoán rating hay không?
  - Nếu khả thi, **những đặc trưng nào** nên dùng làm input cho mô hình học máy?

## 2. Thu thập dữ liệu (data crawling)
- Nguồn dữ liệu: website **TMDB (The Movie Database)**.
- Cách crawl (script scrape.py):
  - Lấy danh sách phim theo từng trang: https://www.themoviedb.org/movie?page=k.
  - Với mỗi phim, trích movie_id từ URL và gọi TMDB API /movie/{id}.
  - Thu thập các trường: Movie_name, Release_year, Rating, Voting_count, Genre, Run_time, Budget.
  - Loại bỏ các phim thiếu thông tin quan trọng (N/A).
- Kết quả: khoảng 1.8–2.0k phim, 7 cột dữ liệu ban đầu.

## 3. Khảo sát & thống kê mô tả (EDA đơn biến)
- Dùng df.info(), describe() để xem kiểu dữ liệu, khoảng giá trị, missing.
- Biểu đồ (matplotlib + seaborn):
  - Histogram + KDE + boxplot cho Rating.
  - Histogram cho Voting_count, Release_year, Runtime_min, Budget_num.
  - Barplot top các thể loại phổ biến.
- Nhận xét nhanh về phân bố của mỗi biến.

## 4. Làm sạch & chuẩn hóa dữ liệu
- Mục tiêu: đưa dữ liệu về dạng đủ, đúng kiểu, hợp lý.
- Bước chính:
  1. Chuẩn hóa Rating bằng hàm parse_rating → trích số thực (giữ phần thập phân).
  2. Ép kiểu Voting_count, Release_year về dạng số.
  3. Chuyển Run_time → Runtime_min, Budget → Budget_num.
  4. Lọc các bản ghi:
     - Có đủ Rating, Voting_count, Release_year.
     - Rating trong [0;10], Voting_count > 0, năm trong [1900; hiện tại].
     - Loại duplicate, chuẩn hóa chuỗi Movie_name, Genre.
- So sánh histogram Rating, log(Voting_count), Release_year trước/sau làm sạch và rút ra ý nghĩa.

## 5. Mã hóa & xây dựng đặc trưng (Encoding + Feature engineering)
- Mã hóa thể loại (Genre):
  - Tách chuỗi thể loại, chọn top thể loại phổ biến, tạo cột one-hot Genre_....
- Đặc trưng mới:
  - Num_genres – số thể loại mỗi phim.
  - Voting_count_log – log(1 + Voting_count).
  - Decade – thập kỷ phát hành.
  - Title_length – độ dài tên phim.
  - Budget_log – log(1 + Budget_num).
- Giải thích trực giác vì sao mỗi feature có thể liên quan đến Rating.

## 6. Trực quan hóa đa biến & mối quan hệ với Rating
- Correlation heatmap giữa các biến số.
- Scatter plot: Rating vs Voting_count_log, Release_year, Runtime_min, Budget_log.
- lmplot: Rating ~ Release_year.
- jointplot: Rating và Voting_count_log.
- **Clustermap** và **t-SNE** (xem mục 6.1 và 6.2 bên dưới).

### 6.1 Clustermap là gì?
- **Định nghĩa:** Clustermap = **Heatmap tương quan** + **Dendrogram** (cây phân cụm). Vừa xem được ma trận tương quan giữa các biến, vừa xem được **nhóm biến nào “giống nhau”** (tương quan cao) vì chúng được sắp xếp lại theo cây phân cấp.
- **Mục đích:** Giúp nhìn nhanh **nhóm biến** (vd: Voting_count và Voting_count_log gần nhau; Rating, Voting_count, Runtime_min có thể cùng một nhánh) và **cường độ tương quan** (màu đỏ = dương, xanh = âm).
- **Cách tạo:** Dùng **hierarchical clustering** (phân cụm phân cấp) trên ma trận tương quan để sắp xếp lại hàng/cột, rồi vẽ heatmap (trong notebook: `sns.clustermap(...)`).

**Sơ đồ ý tưởng Clustermap:**
```
  [Ma trận tương quan]     +     [Phân cụm phân cấp]
  (Rating, Vote, Year,...)          (dendrogram)
            |                              |
            +----------> Sắp xếp lại hàng/cột theo nhóm
                        |
                        v
            +-------------------+
            |  Heatmap + cây    |  → Biến “giống nhau” nằm gần nhau
            |  (clustermap)     |
            +-------------------+
```

### 6.2 t-SNE là gì?
- **Định nghĩa:** t-SNE (t-Distributed Stochastic Neighbor Embedding) là kỹ thuật **giảm chiều** (dimensionality reduction): từ nhiều đặc trưng (vd: 8 biến) nén xuống **2 trục** (t-SNE 1, t-SNE 2) để vẽ trên mặt phẳng.
- **Mục đích:** **Trực quan hóa cấu trúc cụm** của **từng bản ghi** (từng phim): phim “giống nhau” về các đặc trưng sẽ nằm gần nhau trên đồ thị 2D. Tô màu theo Rating để xem rating cao/thấp có tụ lại thành vùng hay không.
- **Khác với Clustermap:** Clustermap nhóm **biến** (cột); t-SNE nhóm **mẫu** (từng phim). Cả hai đều dùng để “nhìn” cấu trúc dữ liệu.
- **Tham số quan trọng:** `perplexity` (vd: 30) – cân bằng giữa cấu trúc “lân cận” và “toàn cục”; thường chọn 5–50.

**Sơ đồ ý tưởng t-SNE:**
```
  [Dữ liệu nhiều chiều]              [Không gian 2D]
  Mỗi phim = 1 điểm trong R^8        Mỗi phim = 1 điểm (x, y)
  (Rating, Vote, Year, Runtime,...)   (t-SNE 1, t-SNE 2)
            |                                  |
            |   t-SNE: giữ “khoảng cách”       |
            |   giữa các điểm (gần thì vẫn     |
            +----------> gần, xa thì vẫn xa) ---+
                        |
                        v
            Scatter plot 2D, tô màu theo Rating
            → Xem có cụm theo rating hay không
```

## 7. Kết luận về tính khả thi
- Dữ liệu sau làm sạch vẫn có đủ số lượng mẫu và nhiều biến mô tả hữu ích.
- Các biểu đồ cho thấy Rating có quan hệ với số vote, năm phát hành, thể loại, runtime, budget.
- Kết luận: bài toán dự đoán Rating từ các biến đã thu thập khả thi về mặt dữ liệu.
- Nêu 1–2 hạn chế chính (missing Budget/Runtime, Rating từ API,…).

## 8. Gợi ý chia phần cho từng thành viên
- SV1: Phần 1–2 (bài toán, crawl dữ liệu).
- SV2: Phần 3–4 (EDA, cleaning).
- SV3: Phần 5–6 (encoding, feature engineering, trực quan đa biến).
- SV4: Phần 7 (kết luận, hạn chế, hướng phát triển).
