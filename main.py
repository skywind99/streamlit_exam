import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

st.set_page_config(page_title="웹 파서 개선판", layout="wide")
st.title("🧩 HTML 파서 with 표 & 링크 텍스트 개선")

url = st.text_input("🔗 분석할 웹페이지 URL을 입력하세요:")
tag_options = ['table', 'img', 'a', 'div', 'p']
tag = st.selectbox("🔖 분석할 HTML 태그 선택", tag_options)

if url and tag and st.button("파싱 시작"):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.find_all(tag)

        st.success(f"{len(elements)}개의 `{tag}` 태그를 찾았습니다.")

        for idx, el in enumerate(elements):
            st.markdown(f"---\n### ▶️ {tag} 요소 {idx + 1}")

            # ✅ table 처리
            if tag == "table":
                rows = el.find_all("tr")
                data = []
                max_cols = 0

                for row in rows:
                    cols = row.find_all(["td", "th"])
                    row_data = []
                    for col in cols:
                        content = col.get_text(strip=True)
                        row_data.append(content)
                    max_cols = max(max_cols, len(row_data))
                    data.append(row_data)

                # 열 개수가 다를 경우 맞춰줌
                for row in data:
                    while len(row) < max_cols:
                        row.append("")

                df = pd.DataFrame(data)
                st.table(df)

            # ✅ a 태그 개선
            elif tag == "a":
                href = el.get("href")
                text = el.get_text(strip=True)

                if not text:
                    text = "(빈 텍스트 또는 span 내부 텍스트 없음)"

                st.markdown(f"🔗 URL: `{urljoin(url, href)}`")
                st.markdown(f"📝 텍스트: `{text}`")

            # ✅ 기타 태그: 텍스트 + 이미지 + 링크 분석
            else:
                text = el.get_text(strip=True)
                if text:
                    st.markdown(f"📝 텍스트: `{text}`")

                imgs = el.find_all("img")
                for img in imgs:
                    src = urljoin(url, img.get("src", ""))
                    st.markdown(f"🖼️ 이미지: `{src}`")

                links = el.find_all("a")
                for a in links:
                    href = urljoin(url, a.get("href", ""))
                    a_text = a.get_text(strip=True)
                    if not a_text:
                        a_text = "(링크 안에 텍스트 없음)"
                    st.markdown(f"🔗 링크: `{href}` / 📝 텍스트: `{a_text}`")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
