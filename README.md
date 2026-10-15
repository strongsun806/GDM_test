# 📐 자율형 여행 아키텍트 (Agentic Travel Architect)
> **Google DeepMind AI Hackathon Project** • *Architect Blueprint & Geometric Neon Glassmorphism*

Gemini 3.8 & 4 Argon의 **정밀 지리·예산 심층 추론(Deep Spatial & Budget Reasoning)**과 **Human-in-the-Loop(HITL) 청사진 재검증**을 결합한 차세대 자율형 여행 아키텍처 웹 애플리케이션입니다.

---

## 🌟 핵심 특징 (Key Highlights)

1. **건축 청사진 기법의 정밀 동선 & 예산 심층 추론**
   - **기본 모델**: `gemini-3.8-flash` (무료 API 키에서도 초고속·안정적 구동)
   - **추가 지원 모델**: `gemini-3.8-pro`, `gemini-4-argon`
   - **추론 옵션**: `thinking_level="high"` 적용
   - 공간 기하학 알고리즘을 통한 최단 동선 설계 및 카테고리별 현실적 예산 포트폴리오 산출

2. **지능형 자동 Fallback 엔진 (100% 무중단 안정성)**
   - 고사양 모델(`gemini-4-argon`, `gemini-3.8-pro`) 호출 시 무료 쿼터 초과(429) 또는 가용성 제한(404)이 발생하면, **즉시 `gemini-3.8-flash`로 자율 폴백하여 일정을 끊김 없이 완성**합니다.

3. **기하학적 네온 & 아키텍트 모던 Glassmorphism UI**
   - 딥 스페이스 차콜 기반의 36px 블루프린트 그리드 & 오로라 앰비언트 글로우
   - 얇은 지오메트릭 보더와 블러 효과가 적용된 글래스모피즘 패널
   - 시안-인디고 네온 그래디언트 인터랙션 버튼 및 1 : 1.2 황금비 레이아웃
   - 화면을 가리지 않는 세미 트랜스페어런트 인-UI 토스트 알림

4. **멀티모달 가이드북/메모 앵커링 & HITL 실시간 재검증**
   - 가이드북(PDF/TXT/MD) 업로드 시 핵심 스팟을 앵커 거점으로 자동 배치
   - 사용자 피드백(우천 대비 실내 코스 변경 등) 입력 시 동선 및 예산 충돌을 재검증하여 종합 일정표를 실시간 동기화

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
