import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="웹 구조 분석기", layout="wide")
st.title("🧩 HTML 구조 파서 (테이블, 이미지, 링크 자동 분석)")

url = st.text_input("🔗 분석할 웹페이지 URL을 입력하세요:")

if url:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 자동 태그 종류 추천
        tag_options = ['table', 'img', 'div', 'a', 'p', 'ul']
        tag = st.selectbox("🔖 분석할 HTML 태그 선택", tag_options)

        elements = soup.find_all(tag)
        st.success(f"총 {len(elements)}개의 `{tag}` 태그가 감지되었습니다.")

        for idx, el in enumerate(elements):
            st.markdown(f"---\n### ▶️ {tag} 요소 {idx + 1}")

            if tag == 'table':
                rows = el.find_all('tr')
                for row_idx, row in enumerate(rows):
                    cols = row.find_all(['td', 'th'])
                    st.markdown(f"**Row {row_idx + 1}**:")
                    for col_idx, col in enumerate(cols):
                        content = col.get_text(strip=True)
                        images = col.find_all('img')
                        links = col.find_all('a')

                        if images:
                            for img in images:
                                src = urljoin(url, img.get("src", ""))
                                st.markdown(f"🖼️ 이미지: `{src}`")
                        elif links:
                            for a in links:
                                href = urljoin(url, a.get("href", ""))
                                st.markdown(f"🔗 링크 (URL): `{href}`")
                        elif content:
                            st.markdown(f"📝 텍스트 {col_idx + 1}: `{content}`")
                        else:
                            st.markdown(f"❗ 빈 셀 {col_idx + 1}")

            elif tag == 'img':
                src = el.get("src")
                if src:
                    img_url = urljoin(url, src)
                    st.image(img_url, caption=img_url)

            elif tag == 'a':
                href = el.get("href")
                text = el.get_text(strip=True)
                if href:
                    full_url = urljoin(url, href)
                    st.markdown(f"🔗 URL: `{full_url}` / 📝 텍스트: `{text}`")

            elif tag in ['div', 'p', 'ul']:
                text = el.get_text(strip=True)
                images = el.find_all('img')
                links = el.find_all('a')

                if images:
                    for img in images:
                        src = urljoin(url, img.get("src", ""))
                        st.markdown(f"🖼️ 포함 이미지: `{src}`")
                if links:
                    for a in links:
                        href = urljoin(url, a.get("href", ""))
                        st.markdown(f"🔗 포함 링크: `{href}`")
                if text:
                    st.markdown(f"📝 텍스트: `{text}`")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
