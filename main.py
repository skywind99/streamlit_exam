import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re

st.set_page_config(page_title="링크 분석기", layout="wide")
st.title("🔗 링크 추출 + 미리보기")

url = st.text_input("📥 분석할 웹페이지 주소:")
tag = st.selectbox("🔖 분석할 태그 선택", ['a'])

# 링크 템플릿
LINK_TEMPLATE = (
    "https://www.seti.go.kr/common/bbs/management/selectCmmnBBSMgmtView.do"
    "?menuId=1000002747&pageIndex=1&bbscttId={}&bbsId=BBSMSTR_000000001070"
    "&searchKey=&searchWord=&etc=&searchKeyTxt=1&searchWordTxt=&perPage=10"
)

if url and st.button("🔍 파싱 시작"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        a_tags = soup.find_all("a")
        st.success(f"🔗 a 태그 {len(a_tags)}개 발견")

        for idx, a in enumerate(a_tags):
            href = a.get("href", "")
            span = a.find("span")
            text = span.get_text(strip=True) if span else a.get_text(strip=True)
            if not text:
                text = "(텍스트 없음)"

            # 숫자 10자리 추출
            match = re.search(r"\d{10}", href)
            if match:
                bbsctt_id = match.group()
                converted_url = LINK_TEMPLATE.format(bbsctt_id)
            else:
                converted_url = None

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{text}**")
                if converted_url:
                    st.text(f"{converted_url}")
                    if st.button(f"🔎 링크 확인 {idx+1}", key=f"preview_{idx}"):
                        st.session_state[f"preview_link_{idx}"] = converted_url
                else:
                    st.warning("❌ 숫자 10자리(bbscttId) 없음")

            with col2:
                if f"preview_link_{idx}" in st.session_state:
                    preview_url = st.session_state[f"preview_link_{idx}"]
                    st.info(f"🔗 미리보기: {preview_url}")
                    try:
                        preview_resp = requests.get(preview_url)
                        preview_resp.raise_for_status()
                        preview_soup = BeautifulSoup(preview_resp.text, "html.parser")

                        # 예시: 페이지의 제목을 표시
                        title_tag = preview_soup.find("h1") or preview_soup.find("title")
                        preview_text = title_tag.get_text(strip=True) if title_tag else "(제목 없음)"
                        st.markdown(f"**📝 페이지 제목:** {preview_text}")

                        # 일부 텍스트 내용 예시 표시
                        first_p = preview_soup.find("p")
                        if first_p:
                            st.text(f"본문 예시: {first_p.get_text(strip=True)}")
                    except Exception as e:
                        st.error(f"❌ 미리보기 불가: {e}")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
