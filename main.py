import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

st.set_page_config(page_title="웹 구조 파서", layout="wide")
st.title("🧩 HTML 구조 파서 with 표 + 링크 + 이미지 분석")

# 입력
url = st.text_input("🔗 분석할 웹페이지 URL을 입력하세요:")
tag_options = ['table', 'img', 'a', 'div', 'p']
tag = st.selectbox("🔖 분석할 HTML 태그 선택", tag_options)

if url and tag and st.button("파싱 시작"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        elements = soup.find_all(tag)
        st.success(f"🔎 {len(elements)}개의 `{tag}` 태그가 감지되었습니다.")

        for idx, el in enumerate(elements):
            st.markdown(f"---\n### ▶️ {tag} 요소 {idx + 1}")

            # ✅ TABLE 분석
            if tag == "table":
                rows = el.find_all("tr")
                data = []
                max_cols = 0

                for row in rows:
                    cols = row.find_all(["td", "th"])
                    row_data = []
                    for col in cols:
                        # a 태그 + span 처리
                        if a := col.find("a"):
                            href = a.get("href", "").strip()
                            span = a.find("span")
                            text = span.get_text(strip=True) if span else a.get_text(strip=True)
                            if href:
                                content = f"{text} ({urljoin(url, href)})" if text else f"(링크: {urljoin(url, href)})"
                            else:
                                content = text
                        else:
                            # 일반 텍스트
                            content = col.get_text(strip=True)
                        row_data.append(content)
                    max_cols = max(max_cols, len(row_data))
                    data.append(row_data)

                # 열 정렬
                for row in data:
                    while len(row) < max_cols:
                        row.append("")

                df = pd.DataFrame(data)
                st.table(df)

            # ✅ IMG 분석
            elif tag == "img":
                src = el.get("src")
                if src:
                    full_src = urljoin(url, src)
                    st.image(full_src, caption=full_src)

            # ✅ A 분석
            elif tag == "a":
                href = el.get("href", "")
                span = el.find("span")
                text = span.get_text(strip=True) if span else el.get_text(strip=True)
                if not text:
                    text = "(텍스트 없음)"
                full_url = urljoin(url, href)
                st.text(f"📝 텍스트: {text}")
                st.text(f"🔗 URL: {full_url}")

            # ✅ 기타 (div, p 등)
            else:
                text = el.get_text(strip=True)
                if text:
                    st.text(f"📝 텍스트: {text}")

                imgs = el.find_all("img")
                for img in imgs:
                    src = img.get("src", "")
                    st.text(f"🖼️ 이미지 URL: {urljoin(url, src)}")

                links = el.find_all("a")
                for a in links:
                    href = a.get("href", "")
                    span = a.find("span")
                    a_text = span.get_text(strip=True) if span else a.get_text(strip=True)
                    if not a_text:
                        a_text = "(링크 텍스트 없음)"
                    st.text(f"🔗 링크: {a_text} ({urljoin(url, href)})")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
