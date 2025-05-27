import streamlit as st
import fitz  # PyMuPDF
import random

# PDF에서 단어와 뜻을 추출하는 함수
def extract_words_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    words = []
    for page in doc:
        text = page.get_text("text")
        # 단어와 뜻을 추출하는 로직 (PDF 형식에 따라 달라질 수 있음)
        for line in text.split("\n"):
            parts = line.split(" - ")
            if len(parts) == 2:
                word, meaning = parts
                words.append({"word": word.strip(), "meaning": meaning.strip()})
    return words

# PDF 파일 경로 설정
pdf_path = 'pdf_files/english.pdf'  # 'pdf_files' 폴더에 'english.pdf' 파일이 있다고 가정
words = extract_words_from_pdf(pdf_path)

# 랜덤으로 단어 10개 추출 (단, 리스트 크기보다 큰 수를 요구할 수 없게 수정)
def get_random_words(words, num=10):
    num = min(num, len(words))  # num이 words의 크기보다 크면 조정
    return random.sample(words, num)

# Streamlit 앱 UI
st.title("영단어 학습 앱")

# '오늘의 단어' 버튼 클릭 시 랜덤 10개 단어 제공
if st.button("오늘의 단어"):
    random_words = get_random_words(words)
    st.session_state.random_words = random_words  # 세션에 저장하여 상태 유지
    st.session_state.current_index = 0  # 처음 단어부터 시작

if 'random_words' in st.session_state:
    # current_index가 random_words의 길이를 초과하지 않도록 보호
    current_index = st.session_state.current_index
    random_words = st.session_state.random_words
    if current_index < len(random_words):
        word = random_words[current_index]
        
        # 뜻 보기
        if st.button("뜻 보기"):
            st.session_state.show_meaning = True
            st.write(f"뜻: {word['meaning']}")

        # 단어 보기
        if st.button("단어 보기"):
            st.session_state.show_meaning = False
            st.write(f"단어: {word['word']}")

        # '다음' 버튼으로 다음 단어로 넘어가기
        if st.button("다음"):
            if current_index < len(random_words) - 1:
                st.session_state.current_index += 1  # 다음 단어로 인덱스 증가
                st.session_state.show_meaning = False  # 단어가 보이게 초기화
            else:
                st.write("단어 학습이 끝났습니다.")
    else:
        st.write("목록에 더 이상 단어가 없습니다.")
