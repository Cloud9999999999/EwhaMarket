# 🌸 이화마켓 (Ewha Market)

> 이화인들을 위한 신뢰 기반 중고 거래 플랫폼 > 2025-2학기 오픈SW플랫폼 팀 프로젝트
> 

## 1. 프로젝트 소개 (Project Overview)

이화마켓은 학교 구성원들끼리 전공 서적, 자취 용품, 의류 등을 믿고 거래할 수 있는 커뮤니티형 중고 거래 웹 서비스입니다.
기존 중고 거래 플랫폼의 불확실성을 해소하고, 이화인이라는 공통된 신분을 바탕으로 안전하고 편리한 거래 환경을 제공합니다.

- **개발 기간:** 2025.09 ~ 2025.12
- **팀명:** Cloud9

## 2. 팀원 및 역할 (Team Members)

| **이름** | **역할** | **담당 업무** | **Github** |
| --- | --- | --- | --- |
| **윤가빈** | **Backend / Leader** | 상품 등록 및 조회(List, Detail) 구현, DB 설계, 페이징/정렬/필터링 로직 | [@](https://www.google.com/search?q=Link&authuser=1)yoongabin |
| **양승혜** | Frontend / Design | 전체 UI/UX 가이드라인, 마이페이지, Figma 디자인 총괄 | [@](https://www.google.com/search?q=Link&authuser=1)seunghye-rain |
| **구지원** | Backend | 마이페이지 백엔드 로직, 사용자 정보 수정 기능 | [@](https://www.google.com/search?q=Link&authuser=1)jeewon514 |
| **조승연** | Frontend | 리뷰 시스템(등록, 조회, 상세) 화면 구현 및 연동 | [@s](https://www.google.com/search?q=Link&authuser=1)erena2140 |
| **유아영** | Frontend | 회원가입, 로그인/로그아웃 인증 화면 및 로직 연결 | [@](https://www.google.com/search?q=Link&authuser=1)ahyoungyoo |

## 3. 기술 스택 (Tech Stack)

**Frontend**

- html + css + javascript

**Backend**

- python flask

**Database**

- firebase

## 4. 주요 기능 (Key Features)

### 👤 사용자 (User)

- **회원가입:** 아이디 중복 체크, 비밀번호 해싱(Hashing) 저장으로 보안 강화.
- **로그인/로그아웃:** Flask Session을 이용한 로그인 상태 관리.
- **마이페이지:** 내 정보 수정, 내가 찜한 상품 목록, 내가 쓴 리뷰 관리.

![image.png](attachment:86f22d01-9033-4fcb-9857-d2f123630b2c:image.png)

### 🛍️ 상품 (Item)

- **상품 등록:** 이미지 업로드 및 상품 상세 정보(가격, 카테고리, 상태 등) 입력.
- **상품 목록 조회:**
    - **Pagination:** 한 페이지당 8개씩 상품 노출.
    - **Sorting:** 신상품순, 인기순(찜 많은 순), 가격순 정렬.
- **상품 상세 조회:** 판매자 정보 확인 및 찜하기 기능.

![image.png](attachment:00b894c5-215f-4861-96da-e20b466ad1e0:image.png)

![image.png](attachment:1cd32407-0016-4f30-8ebd-30354cedf5c1:image.png)

### ⭐ 리뷰 & 찜 (Review & Like)

- **리뷰 시스템:** 구매한 상품에 대한 사진 리뷰 작성 및 별점 부여.
- **찜하기(Like):** AJAX를 활용하여 새로고침 없이 상품 찜/찜 취소 기능 구현 (하트 토글).

![image.png](attachment:2a6ec120-df2a-4cc6-988a-a7cb1492720f:image.png)

## 5. 데이터베이스 구조 (Database Structure)

Firebase Realtime Database (NoSQL)를 사용하여 데이터를 JSON 트리 구조로 관리합니다.

- `user`: 사용자 정보 (id, pw_hash, email, nickname 등)
- `item`: 등록된 상품 정보 (name, price, category, img_path, seller 등)
- `reviews`: 상품별 리뷰 데이터
- `favorites`: 사용자별 찜한 상품 목록

![image.png](attachment:364c2075-0d5c-4caa-a5a0-0165e2759eb9:image.png)

## 6. 설치 및 실행 방법 (Installation & Usage)

이 프로젝트를 로컬 환경에서 실행하기 위해서는 Python과 Anaconda가 필요합니다.

1. **Repository Clone**Bash
    
    `git clone(https://github.com/Cloud9999999999/EwhaMarket.git) https://github.com/Cloud9999999999/EwhaMarket.git
    cd EwhaMarket`
    
2. **가상환경 생성 및 활성화**Bash
    
    `conda create -n ewha_market python=3.8
    conda activate ewha_market`
    
3. 필수 라이브러리 설치Bash
    
    주의: pyrebase가 아닌 pyrebase4를 설치해야 합니다.
    
    `pip install flask
    pip install pyrebase4`
    
4. **Firebase 설정 파일 추가**
    - `authentication` 폴더 내에 `firebase_auth.json` 파일을 생성하고, 본인의 Firebase 프로젝트 설정 키(API Key 등)를 입력해야 합니다.
    - (보안상 깃허브에는 업로드되지 않았습니다.)
5. **서버 실행**Bash
    
    `flask --debug run`
    
    브라우저에서 `http://127.0.0.1:5000` 으로 접속합니다.
    

## 7. 폴더 구조 (Folder Structure)

`flask_project/
├── app.py                  # 메인 Flask 애플리케이션 파일 (라우팅 처리)
├── database.py             # DB 핸들링 모듈 (DBHandler 클래스)
├── authentication/         # Firebase 인증 키 보관 폴더
│   └── firebase_auth.json
├── static/                 # 정적 파일 (CSS, JS, Images)
│   ├── images/             # 업로드된 상품/리뷰 이미지
│   └── styles/
└── templates/              # HTML 템플릿 파일
    ├── index.html          # 메인 페이지
    ├── auth/               #로그인, 로그아웃, 회원가입
    ├── mypage/             #마이페이지
    ├── products/           #상품 전체조회, 상품 등록
    └── reviews/            #리뷰 전체조회, 리뷰 등록`