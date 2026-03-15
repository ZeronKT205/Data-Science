import os

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.themoviedb.org"
MOVIE_LIST_URL = "https://www.themoviedb.org/movie?page="
TMDB_API_URL = "https://api.themoviedb.org/3/movie/"
TMDB_API_KEY = "754eab4d73415830cdc442a529421c60"  

headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_movie_links(page):
    """Lấy link phim từ trang danh sách"""

    url = MOVIE_LIST_URL + str(page)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    movie_cards = soup.find_all("div", class_="card style_1")

    links = []
    for card in movie_cards:
        content = card.find("div", class_="content")
        if not content:
            continue
        a_tag = content.find("a")
        if not a_tag or not a_tag.get("href"):
            continue
        link = a_tag["href"]
        links.append(BASE_URL + link)

    return links


def extract_movie_id(url: str) -> str | None:
    """
    Lấy movie_id từ URL dạng https://www.themoviedb.org/movie/238-the-godfather
    """
    try:
        path = url.split(BASE_URL)[-1]  # /movie/238-the-godfather
        parts = path.strip("/").split("/")  # ["movie", "238-the-godfather"]
        if len(parts) < 2:
            return None
        id_and_slug = parts[1]  # "238-the-godfather"
        movie_id = id_and_slug.split("-")[0]
        return movie_id if movie_id.isdigit() else None
    except Exception:
        return None


def get_movie_details(url):
    """Lấy thông tin chi tiết của phim (ưu tiên dùng TMDB API cho chính xác)."""

    movie_id = extract_movie_id(url)

    movie_name = "N/A"
    release_year = "N/A"
    rating = "N/A"
    voting_count = "N/A"
    genres = "N/A"
    runtime = "N/A"
    budget = "N/A"

    # Nếu có API key và movie_id thì gọi TMDB API để lấy dữ liệu chuẩn
    if TMDB_API_KEY and movie_id:
        try:
            api_url = f"{TMDB_API_URL}{movie_id}"
            params = {
                "api_key": TMDB_API_KEY,
                "language": "en-US",
            }
            resp = requests.get(api_url, params=params)
            resp.raise_for_status()
            data = resp.json()

            movie_name = data.get("title") or data.get("name") or movie_name

            release_date = data.get("release_date")
            if release_date:
                release_year = release_date.split("-")[0]

            vote_average = data.get("vote_average")
            if vote_average is not None:
                # TMDB vote_average là thang 0-10, bạn có thể đổi sang % nếu muốn
                rating = f"{vote_average:.1f}"

            vote_count = data.get("vote_count")
            if vote_count is not None:
                voting_count = str(vote_count)

            genres_list = data.get("genres") or []
            if genres_list:
                genres = ", ".join(g.get("name", "") for g in genres_list if g.get("name"))

            runtime_val = data.get("runtime")
            if runtime_val:
                runtime = f"{runtime_val} min"

            budget_val = data.get("budget")
            if budget_val:
                budget = f"${budget_val:,.0f}"
        except Exception:
            # Nếu API lỗi thì fallback sang scraping HTML
            pass

    # Fallback: nếu một số trường vẫn N/A thì thử scrape HTML (phòng trường hợp thiếu API key)
    if any(v == "N/A" for v in [movie_name, release_year, genres, runtime, budget]) or rating == "N/A":
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            if movie_name == "N/A":
                title_h2 = soup.find("h2")
                if title_h2:
                    a_tag = title_h2.find("a")
                    if a_tag and a_tag.text:
                        movie_name = a_tag.text.strip()

            if release_year == "N/A":
                # Nhiều layout: năm trong tiêu đề hoặc bên cạnh ngày phát hành
                release_span = soup.find("span", class_="tag release_date")
                if release_span and release_span.text:
                    release_year = release_span.text.strip().strip("()")

            if genres == "N/A":
                genre_span = soup.find("span", class_="genres")
                if genre_span:
                    genres = ", ".join(g.text.strip() for g in genre_span.find_all("a") if g.text.strip()) or genres

            if runtime == "N/A":
                runtime_span = soup.find("span", class_="runtime")
                if runtime_span and runtime_span.text:
                    runtime = runtime_span.text.strip()

            if budget == "N/A":
                for bdi in soup.find_all("bdi"):
                    if "Budget" in bdi.text:
                        parent_p = bdi.find_parent("p")
                        if parent_p:
                            text = parent_p.text.replace("Budget", "").strip()
                            if text and text != "-":
                                budget = text
                        break
        except Exception:
            pass

    return {
        "Movie_name": movie_name,
        "Release_year": release_year,
        "Rating": rating,
        "Voting_count": voting_count,
        "Genre": genres,
        "Run_time": runtime,
        "Budget": budget,
    }


def scrape_movies(start_page: int, end_page: int):
    """Scrape nhiều trang phim từ start_page đến end_page (bao gồm)."""

    all_movies = []

    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}...")

        links = get_movie_links(page)

        for link in links:
            movie_data = get_movie_details(link)

            # Làm sạch ngay từ bước crawl:
            # - Loại bỏ mọi bản ghi có bất kỳ trường nào là "N/A" hoặc rỗng
            values = list(movie_data.values())
            if any(v is None or v == "" or v == "N/A" for v in values):
                continue

            all_movies.append(movie_data)

    return all_movies


if __name__ == "__main__":
    # Hỏi người dùng muốn crawl từ trang nào đến trang nào
    while True:
        try:
            start_input = input("Nhập trang bắt đầu (>=1): ").strip()
            end_input = input("Nhập trang kết thúc (>= trang bắt đầu): ").strip()

            start_page = int(start_input)
            end_page = int(end_input)

            if start_page < 1 or end_page < 1:
                print("Vui lòng nhập số nguyên >= 1 cho cả hai trang.")
                continue
            if end_page < start_page:
                print("Trang kết thúc phải >= trang bắt đầu.")
                continue
            break
        except ValueError:
            print("Giá trị không hợp lệ, hãy nhập số nguyên cho cả hai trang.")

    movies = scrape_movies(start_page, end_page)

    df = pd.DataFrame(movies)
    df.index += 1

    # Tìm tên file chưa tồn tại: data.xlsx, data1.xlsx, data2.xlsx, ...
    base_name = "data"
    ext = ".xlsx"
    file_name = base_name + ext
    counter = 1
    while os.path.exists(file_name):
        file_name = f"{base_name}{counter}{ext}"
        counter += 1

    df.to_excel(file_name, index=True)

    print(f"Done! File saved to {file_name}.")