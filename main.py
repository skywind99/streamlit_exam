import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re

st.set_page_config(page_title="📊 테이블 파서", layout="wide")
st.title("📋 HTML Table 파싱 + 링크 추출 & 미리보기")

url = st.text_input("🔗 분석할 웹사이트 주소를 입력하세요")

# 변환할 링크 템플릿
LINK_TEMPLATE = (
    "https://www.seti.go.kr/common/bbs/management/selectCmmnBBSMgmtView.do"
    "?menuId=1000002747&pageIndex=1&bbscttId={}&bbsId=BBSMSTR_000000001070"
    "&searchKey=&searchWord=&etc=&searchKeyTxt=1&searchWordTxt=&perPage=10"
)

if url and st.button("🔍 테이블 파싱 시작"):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        tables = soup.find_all("table")
        st.success(f"✅ 총 {len(tables)}개의 `<table>` 태그가 발견되었습니다.")

        for table_idx, table in enumerate(tables):
            st.markdown(f"---\n## 📦 테이블 {table_idx + 1}")

            rows = table.find_all("tr")
            for row_idx, row in enumerate(rows):
                cols = row.find_all(["td", "th"])
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"### ▶️ Row {row_idx + 1}")
                    for col_idx, col in enumerate(cols):
                        st.markdown(f"- 셀 {col_idx + 1}:")
                        a = col.find("a")
                        span = a.find("span") if a else None
                        href = a.get("href", "") if a else None
                        text = span.get_text(strip=True) if span else col.get_text(strip=True)

                        # 링크 변환 처리
                        if href and re.search(r"\d{10}", href):
                            bbsctt_id = re.search(r"\d{10}", href).group()
                            converted_url = LINK_TEMPLATE.format(bbsctt_id)
                            st.text(f"📝 텍스트: {text}")
                            st.text(f"🔗 변환 링크: {converted_url}")
                            if st.button(f"🔎 링크 확인 - {table_idx}-{row_idx}-{col_idx}", key=f"preview_{table_idx}_{row_idx}_{col_idx}"):
                                st.session_state["preview_url"] = converted_url
                        else:
                            st.text(f"📝 텍스트: {text}")

                with col2:
                    key = "preview_url"
                    if key in st.session_state:
                        preview_url = st.session_state[key]
                        st.info(f"🔗 미리보기: {preview_url}")
                        try:
                            preview_res = requests.get(preview_url)
                            preview_soup = BeautifulSoup(preview_res.text, "html.parser")
                            title = preview_soup.find("h1") or preview_soup.find("title")
                            preview_text = title.get_text(strip=True) if title else "(제목 없음)"
                            st.markdown(f"**📝 제목:** {preview_text}")
                            first_p = preview_soup.find("p")
                            if first_p:
                                st.text(f"본문 예시: {first_p.get_text(strip=True)}")
                        except Exception as e:
                            st.error(f"❌ 미리보기 오류: {e}")

    except Exception as e:
        st.error(f"❌ 요청 또는 파싱 중 오류 발생: {e}")
