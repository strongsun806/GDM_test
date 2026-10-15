# ⬡ 자율형 여행 아키텍트 (Autonomous Travel Architect)
> **Google DeepMind AI Hackathon Project** • *Silicon Valley SaaS (Vercel / Linear Level) Dashboard*

Gemini 3.8 Flash & 4 Argon의 **공간·예산 정밀 심층 추론(Deep Reasoning)**과 Vercel/Linear 급의 **하이엔드 다크 글래스모피즘 웹 대시보드**를 결합한 차세대 자율형 여행 청사진 플랫폼입니다.

---

## 🌟 핵심 특징 (Key Highlights)

1. **🏆 Vercel / Linear 급 하이엔드 글래스모피즘 대시보드**
   - Gradio 기본 테마의 한계를 무력화하고, 딥 오션 블랙(`#030712`, `#0b0f19`)과 반투명 프로스트 글래스(`border-radius: 20px`), 네온 시안/퍼플 보더라인으로 전면 재설계.
   - **가시성 100% 확보**: 모든 텍스트와 입력 필드를 선명한 고대비 화이트(`color: #FFFFFF`)와 시안 글로우 포커스 링으로 렌더링하여 어두운 배경에서도 가독성 완벽 보장.

2. **🌊 실시간 살아 숨 쉬는 인터랙티브 오로라 & 파도 캔버스**
   - 4중 유기적 하모닉 사인파 웨이브와 70개의 발광 스타더스트 입자.
   - 마우스 커서의 위치를 부드럽게 추적하는 래디얼 오로라 블룸 및 클릭 시 파동이 퍼지는 리플 시스템 (`pointer-events: none`으로 UI 클릭 100% 보장).

3. **📊 3D 다이내믹 예산 포트폴리오 매트릭스**
   - 숙박(35%), 식비(28%), 교통(15%), 액티비티(14%), 예비비(8%)를 한눈에 볼 수 있는 네온 프로그레스 바 대시보드 위젯.

4. **📄 1-클릭 정밀 한국어 PDF 리포트 다운로드**
   - ReportLab 기반의 맑은 고딕(Malgun Gothic) 폰트가 탑재되어, A4 규격의 고품질 여행 청사진 PDF를 즉시 생성 및 다운로드.

5. **🔗 실시간 원클릭 여행 예약 콘솔 & 지도 연동**
   - 스카이스캐너, 아고다, 에어비앤비, 클룩, 구글 지도 링크 상시 연동.
   - 일정표 내 모든 방문지, 식당, 카페마다 `[📍 구글 지도]`, `[🍽️ 맛집 정보]` 마크다운 링크 자동 탑재.

6. **⚡ 100% 무중단 안정성 (기본 모델: `gemini-3.8-flash` & 자율 Fallback)**
   - 무료 API 키에서도 쿼터 초과(429)나 가용성 오류(404) 없이 즉각 작동하며, 고사양 모델 선택 시에도 스마트 Fallback이 보호.

---

## 🚀 빠른 시작 가이드 (Quick Start)

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Gemini API Key 설정 (선택 사항)
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"
```
*(UI 입력창에서도 직접 입력할 수 있습니다.)*

### 3. 애플리케이션 실행
```bash
python app.py
```
브라우저에서 `http://localhost:7860`으로 접속합니다.
