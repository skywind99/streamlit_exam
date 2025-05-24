import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

st.set_page_config(page_title="웹 파서 개선판", layout="wide")
st.title("🔍 웹 파서 with 표 분석")

# 도움말
with st.expander("📘 태그를 어떻게 찾나요?"):
    st.markdown("""
    - 크롬에서 F12 누르거나, 오른쪽 클릭 > **검사**를 선택하세요.
    - 마우스로 원하는 부분을 클릭하면 HTML 태그가 보입니다.
    - 예: `<table class="info">`, `<div id="main">` 등을 확인해 입력하세요.
    - `table`, `div`, `img`, `a` 같은 태그를 많이 사용합니다.
    """)

# 입력
url = st.text_input("🔗 사이트 주소")
tag = st.text_input("🔖 HTML 태그 (예: table, div, p 등)")
attr = st.text_input("🎯 속성 필터 (선택, 예: class=info 또는 id=main)")

if st.button("파싱 시작") and url and tag:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 속성 필터
        if "=" in attr:
            key, val = attr.split("=")
            elements = soup.find_all(tag, {key.strip(): val.strip()})
        else:
            elements = soup.find_all(tag)

        if not elements:
            st.warning("해당 태그를 가진 요소가 없습니다.")
        else:
            st.success(f"🔍 {len(elements)}개의 `{tag}` 요소를 찾았습니다.")

            for i, el in enumerate(elements):
                st.markdown(f"---\n### ▶️ 요소 {i+1}")

                # table 태그의 경우: 각 tr, td 분석
                if tag == "table":
                    rows = el.find_all("tr")
                    data = []
                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        data.append([col.get_text(strip=True) for col in cols])
                    df = pd.DataFrame(data)
                    st.table(df)

                # 이미지 출력
                elif el.find("img"):
                    for img in el.find_all("img"):
                        src = img.get("src")
                        if src:
                            full_url = urljoin(url, src)
                            st.image(full_url)

                # 링크: 텍스트로만 표시
                elif el.find("a"):
                    links = [a.get("href") for a in el.find_all("a") if a.get("href")]
                    for l in links:
                        st.text(urljoin(url, l))

                # 일반 텍스트
                else:
                    text = el.get_text(strip=True)
                    st.text(text if text else "(빈 텍스트)")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
