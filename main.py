# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="웹 파서", layout="wide")

st.title("🔍 웹 페이지 파서")

# 사용자 입력
url = st.text_input("🔗 파싱할 사이트 URL을 입력하세요:")
tag = st.text_input("🔖 가져올 HTML 태그 (예: div, table, img 등):")
attr = st.text_input("🎯 특정 속성 (선택, 예: class=main 또는 id=content)")

if st.button("파싱 시작"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 태그 + 속성 필터링
        if "=" in attr:
            key, val = attr.split("=")
            elements = soup.find_all(tag, {key: val})
        else:
            elements = soup.find_all(tag)

        st.success(f"총 {len(elements)}개 요소를 찾았습니다.")

        for i, el in enumerate(elements):
            st.markdown(f"---\n### ▶️ 요소 {i+1}")

            # 이미지가 있으면 표시
            if el.find("img"):
                for img in el.find_all("img"):
                    src = img.get("src")
                    if src:
                        full_url = urljoin(url, src)
                        st.image(full_url, caption=full_url)

            # 링크가 있으면 표시
            if el.find("a"):
                for a in el.find_all("a"):
                    href = a.get("href")
                    if href:
                        full_url = urljoin(url, href)
                        st.markdown(f"[링크]({full_url})")

            # 텍스트 출력
            text = el.get_text(strip=True)
            if text:
                st.text(text)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
