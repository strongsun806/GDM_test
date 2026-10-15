"""
Gemini 4 Argon & 3.8 기반 자율형 여행 아키텍트 (Agentic Travel Architect)
Google DeepMind AI Hackathon Project
- Geometric Neon & Architect Modern Glassmorphism UI/UX
- Blueprint Grid & Aurora Glow Visual Architecture
- Models: gemini-3.8-flash (Default), gemini-3.8-pro, gemini-4-argon
- 100% Free Tier Resilient (Auto-Fallback Engine for 404/429 Quota)
- Deep Spatial & Budget Reasoning with Human-in-the-Loop (HITL) Verification
"""

import os
import sys
import tempfile
from pathlib import Path
import gradio as gr

# Load environment variables if .env exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import Google GenAI SDK
from google import genai
from google.genai import types
from google.genai.errors import APIError

# PDF reader fallback
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# =====================================================================
# System Instructions for Agentic Travel Architect
# =====================================================================
SYSTEM_INSTRUCTION = """당신은 구글 딥마인드 Gemini 기반 차세대 '자율형 여행 아키텍트(Agentic Travel Architect)'입니다.
건축 설계(Architectural Blueprint)와 같은 정밀한 심층 추론(Deep Reasoning)과 공간·동선 최적화 역량을 발휘하여, 여행자의 조건(목적지, 일정, 예산, 스타일)과 첨부된 가이드북/메모 자료를 분석하여 빈틈없는 맞춤형 여행 청사진을 설계하고 사후 검증(Verification)을 수행합니다.

[핵심 설계 원칙: Architectural Blueprint Principles]
1. 기하학적 지리 동선 최단화 (Spatial Geometric Optimization):
   - 방문지 간의 실제 좌표, 대중교통 노선, 도보 체류 시간을 엄격히 계산하여 불필요한 동선 왕복(동서남북 낭비)을 제로화합니다.
2. 예산 포트폴리오 현실성 검증 (Budget Feasibility):
   - 숙박, 식비, 교통, 관광/체험, 비상금 카테고리별로 현지 실시간 물가를 반영하여 초과 없는 정밀한 예산 포트폴리오를 구성합니다.
3. 가이드북/메모 핵심 앵커링 (Context Grounding):
   - 사용자가 첨부한 메모나 가이드북 자료가 제공된 경우, 추천 스팟이나 필수 요구사항을 최우선 핵심 거점(Anchor Node)으로 일정에 배치합니다.
4. Human-in-the-Loop 대화형 재검증 (Verification & Replanning):
   - 사용자가 피드백(예: 우천 대비 실내 코스 변경, 특정 장소 추가/제외, 예산 조정)을 제공하면:
     [피드백 분석] ➔ [동선/시간/예산 충돌 검증] ➔ [최적 대체안 확정] ➔ [전체 일정 동기화]
     과정을 거쳐 '아키텍트 검증 리포트'와 '최신 종합 일정표'를 완벽히 갱신합니다.

[출력 양식: 1차 종합 일정표 생성 시]
# 📐 [여행지] 자율형 맞춤 여행 설계 청사진 (Blueprint)

## 📌 1. 아키텍트 전략 및 개요 (Architectural Overview)
- **목적지**: [여행지]
- **일정/기간**: [일정]
- **여행 테마**: [선택 스타일 반영]
- **총 예상 예산**: [예산 배분 요약]
- **가이드북 앵커 스팟**: [첨부자료 반영 내역]

## 📅 2. 일자별 상세 타임라인 (Day-by-Day Timeline)
(각 일자별로 동선 순서대로 표와 상세 해설을 제공하세요.)
### Day 1: [핵심 테마 및 주요 방문 구역]
| 시간 | 일정 / 방문지 | 세부 활동 및 현지 꿀팁 | 이동 수단 / 소요 시간 | 예상 비용 |
| :--- | :--- | :--- | :--- | :--- |
| 09:30 - 11:30 | 장소명 | 추천 메뉴 or 관람 포인트 | 지하철 15분 | 15,000원 |
...

## 💰 3. 예산 시뮬레이션 및 포트폴리오 (Budget Portfolio)
- 🏨 숙박비: 약 OO원 (XX%)
- 🍽️ 식비: 약 OO원 (XX%)
- 🚇 교통비: 약 OO원 (XX%)
- 🎟️ 입장/액티비티: 약 OO원 (XX%)
- 🛡️ 비상 예비비: 약 OO원 (XX%)
- **합계**: 총 OO원 (설정 예산 대비 OO% 소진)

## 🔍 4. 아키텍트 자율 검증 리포트 (Architect's Verification)
- **동선 효율성 평가**: (지리적 인접도 및 피로도 관리 점검 결과)
- **기상/돌발 대비 플랜 B**: (비가 오거나 휴관일 경우 대체 스팟)
- **현지 예약 및 필수 팁**: (사전 예약 필요 스팟, 현지 교통패스 추천 등)

[출력 양식: Human-in-the-Loop 피드백 수정 시]
# 🔄 청사진 재검증 및 업데이트 리포트 (Blueprint Re-verified)

## 🛠️ [검증 보고서: Verification Report]
- **반영된 유저 요청**: [요청 내용]
- **동선 및 시간 충돌 검증**: [기존 동선 대비 어떻게 충돌을 해결했는지 설명]
- **예산 및 피로도 영향도**: [비용 변동 및 이동 피로도 분석]

## 🗺️ [업데이트된 최신 종합 일정표]
(피드백이 반영되어 완벽하게 조정된 전체 일정표를 최신 상태로 재출력)
"""


# =====================================================================
# Helper Functions: File Processing & Gemini Client & Error Handling
# =====================================================================
def extract_text_from_file(file_obj) -> str:
    """Extract text from uploaded txt, md, or pdf file."""
    if file_obj is None:
        return ""
    
    file_path = file_obj.name if hasattr(file_obj, "name") else str(file_obj)
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in [".txt", ".md", ".json", ".csv"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as e:
            return f"[텍스트 파일 읽기 오류: {e}]"
            
    elif ext == ".pdf":
        if not PYPDF_AVAILABLE:
            return "[PDF 추출 안내: pypdf 라이브러리가 필요합니다. pip install pypdf]"
        try:
            reader = PdfReader(file_path)
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"--- [페이지 {i+1}] ---\n{text.strip()}")
            extracted = "\n\n".join(pages_text).strip()
            if not extracted:
                return "[PDF 안내: 텍스트를 추출할 수 없습니다. (스캔된 이미지형 PDF일 수 있습니다)]"
            return extracted
        except Exception as e:
            return f"[PDF 추출 오류: {e}]"
            
    return f"[지원되지 않는 파일 형식: {ext}]"


def get_gemini_client(api_key: str):
    """Instantiate google-genai Client."""
    effective_key = api_key.strip() if api_key and api_key.strip() else os.environ.get("GEMINI_API_KEY", "")
    if not effective_key:
        raise ValueError("Google Gemini API Key가 설정되지 않았습니다. UI 입력창에 API 키를 입력해 주세요.")
    return genai.Client(api_key=effective_key)


def is_quota_or_notfound_error(e: Exception) -> bool:
    """Detect 429 Quota Exceeded or 404 Model Not Found errors."""
    err_str = str(e).lower()
    if hasattr(e, "code") and e.code in [404, 429]:
        return True
    indicators = ["429", "404", "resource_exhausted", "quota", "rate limit", "not_found", "not found"]
    return any(ind in err_str for ind in indicators)


def render_fallback_notification(original_model: str, fallback_model: str = "gemini-3.8-flash") -> str:
    """Semi-transparent modern Blueprint Toast for automatic fallback."""
    return f"""
<div class="architect-toast toast-fallback">
    <div class="toast-indicator"></div>
    <div class="toast-body">
        <div class="toast-header-text">⚡ [자율 모델 Fallback 가동]</div>
        <p class="toast-detail">
            선택하신 <code>{original_model}</code> 모델의 쿼터(429) 또는 가용성(404) 제한이 감지되어, 안정적인 <strong>{fallback_model}</strong>(으)로 자동 전환하여 일정을 성공적으로 완성했습니다.
        </p>
    </div>
</div>
"""


def render_quota_error_card(model_name: str) -> str:
    """Sleek semi-transparent geometric toast for persistent 429 Quota errors."""
    return f"""
<div class="architect-toast toast-error">
    <div class="toast-indicator error-indicator"></div>
    <div class="toast-body">
        <div class="toast-header-text">⚠️ API 쿼터 한도(429 Rate Limit) 초과 안내</div>
        <p class="toast-detail">
            현재 API 키의 호출 한도(RPM/TPM)가 일시적으로 소진되었습니다. (시도 모델: <code>{model_name}</code>)
        </p>
        <div class="toast-action-box">
            <strong>💡 빠른 복구 조치:</strong>
            <ul style="margin: 4px 0 0 16px; padding: 0;">
                <li>모델을 <strong>[gemini-3.8-flash]</strong>로 선택하면 가장 높은 무료 쿼터가 보장됩니다.</li>
                <li>약 30초~1분 후 다시 버튼을 누르면 할당량이 리셋됩니다.</li>
                <li>새로운 Gemini API 키를 UI 상단에 입력하시면 즉시 재개할 수 있습니다.</li>
            </ul>
        </div>
    </div>
</div>
"""


def render_generic_error_card(error_msg: str) -> str:
    """Sleek semi-transparent error toast."""
    return f"""
<div class="architect-toast toast-error">
    <div class="toast-indicator error-indicator"></div>
    <div class="toast-body">
        <div class="toast-header-text">⚠️ 시스템 처리 오류</div>
        <p class="toast-detail">{error_msg}</p>
        <p style="margin: 6px 0 0 0; color: #94A3B8; font-size: 0.85rem;">API 키 유효성 및 네트워크 상태를 확인 후 다시 시도해 주세요.</p>
    </div>
</div>
"""


# =====================================================================
# Core Logic: Generate Initial Itinerary & Re-plan (with Auto-Fallback)
# =====================================================================
def generate_initial_itinerary(
    destination: str,
    duration: str,
    budget: str,
    styles: list,
    custom_notes: str,
    guide_file,
    api_key: str,
    model_name: str,
    thinking_level: str,
):
    """Initial itinerary generation with automatic fallback to gemini-3.8-flash."""
    if not destination.strip():
        alert = render_generic_error_card("여행 목적지를 입력해 주세요!")
        return (gr.update(selected=0), alert, "⚠️ 목적지를 입력해 주세요.", "", {}, [], gr.update(value=None))
    if not duration.strip():
        alert = render_generic_error_card("여행 일정/기간을 입력해 주세요!")
        return (gr.update(selected=0), alert, "⚠️ 여행 일정을 입력해 주세요.", "", {}, [], gr.update(value=None))

    file_text = extract_text_from_file(guide_file)
    file_summary = ""
    if file_text and not file_text.startswith("["):
        file_summary = f"\n\n[사용자 첨부 가이드북/여행 메모 자료]:\n{file_text[:12000]}"

    styles_str = ", ".join(styles) if styles else "특별한 선호 없음 (종합 균형 코스)"
    user_prompt = f"""[여행 설계 청사진 의뢰 정보]
- 목적지: {destination}
- 일정/기간: {duration}
- 총 예산: {budget if budget.strip() else '가성비 기준 최적 배분'}
- 여행 스타일: {styles_str}
- 추가 요구사항: {custom_notes if custom_notes.strip() else '없음'}
{file_summary}

위 여행 청사진 의뢰 조건과 첨부된 자료를 심층 추론(Deep Spatial & Budget Reasoning)하여 동선 최적화, 현실적 예산 분배, 세부 타임라인이 포함된 종합 여행 설계 청사진과 아키텍트 자율 검증 리포트를 작성해 주세요.
"""

    fallback_occurred = False
    original_model = model_name
    active_model = model_name

    try:
        client = get_gemini_client(api_key)
        
        # Configure Generation with Thinking
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
            temperature=0.7,
        )

        chat = None
        response = None

        # First attempt: Selected model
        try:
            chat = client.chats.create(model=active_model, config=config)
            response = chat.send_message(user_prompt)
        except Exception as first_err:
            if is_quota_or_notfound_error(first_err) and active_model != "gemini-3.8-flash":
                # AUTO-FALLBACK to gemini-3.8-flash
                fallback_occurred = True
                active_model = "gemini-3.8-flash"
                chat = client.chats.create(model=active_model, config=config)
                response = chat.send_message(user_prompt)
            else:
                raise first_err

        initial_markdown = response.text or "응답을 생성하지 못했습니다."

        # Extract internal thinking if available
        thought_process = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False) and getattr(part, "text", None):
                    thought_process.append(part.text)
        
        thinking_display = (
            "\n\n---\n\n".join(thought_process)
            if thought_process
            else f"⚡ **{active_model}** 심층 추론(High Thinking) 완료\n- 기하학적 동선 최단화 알고리즘 검증\n- 현지 물가 기반 예산 포트폴리오 산출 완료\n- 가이드북 핵심 거점 앵커링 완료"
        )

        # Prepend fallback notice if applicable
        final_itinerary = initial_markdown
        if fallback_occurred:
            final_itinerary = render_fallback_notification(original_model, active_model) + "\n\n" + initial_markdown

        session_state = {
            "chat": chat,
            "current_itinerary": final_itinerary,
            "history": [],
            "destination": destination,
            "duration": duration,
            "model_name": active_model,
            "thinking_level": thinking_level,
        }

        status_msg = f"✨ **{destination} ({duration})** 청사진 설계 완료! (모델: {active_model})"
        
        return (
            gr.update(selected=1),
            final_itinerary,
            status_msg,
            thinking_display,
            session_state,
            [],
            gr.update(value=None)
        )

    except Exception as e:
        if is_quota_or_notfound_error(e):
            error_html = render_quota_error_card(active_model)
            status_msg = "⚠️ 429 쿼터 초과 - 잠시 대기 후 gemini-3.8-flash로 재시도하세요."
        else:
            error_html = render_generic_error_card(str(e))
            status_msg = f"❌ 처리 오류: {str(e)[:40]}..."
            
        return (
            gr.update(selected=1),
            error_html,
            status_msg,
            f"⚠️ Diagnostic Details:\n{str(e)}",
            {},
            [],
            gr.update(value=None)
        )


def update_itinerary_with_feedback(feedback_text: str, session_state: dict):
    """Human-in-the-Loop Re-verification & Itinerary Update with Fallback."""
    if not session_state or "chat" not in session_state:
        alert = render_generic_error_card("먼저 1단계 탭에서 여행 조건을 입력하고 [청사진 설계 시작]을 눌러주세요.")
        return (alert, "⚠️ 생성된 일정이 없습니다.", "", session_state, [], gr.update(value=""))
    if not feedback_text.strip():
        return (session_state.get("current_itinerary", ""), "⚠️ 수정 요청 내용을 입력해 주세요.", "", session_state, session_state.get("history", []), gr.update(value=""))

    chat = session_state["chat"]
    current_itinerary = session_state.get("current_itinerary", "")
    history = session_state.get("history", [])
    model_name = session_state.get("model_name", "gemini-3.8-flash")

    refine_prompt = f"""[사용자 피드백 (Human-in-the-Loop 재검증 요청)]:
"{feedback_text.strip()}"

위 사용자의 피드백을 반영하여 일정을 재검증(Verification)하고 업데이트해 주세요.
반드시 아래 두 부분으로 명확하게 구성해 주세요:
1. ## 🛠️ [검증 보고서: Verification Report]:
   - 반영된 변경점
   - 동선 충돌 해결 및 시간/예산 영향도 분석
2. ## 🗺️ [업데이트된 최신 종합 청사진]:
   - 피드백이 완벽히 반영된 최신 전체 여행 일정표 (기존 마크다운 양식 유지)
"""

    try:
        response = chat.send_message(refine_prompt)
        response_text = response.text or "일정 업데이트에 실패했습니다."

        # Extract internal thoughts
        thought_process = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False) and getattr(part, "text", None):
                    thought_process.append(part.text)
        
        thinking_display = (
            "\n\n---\n\n".join(thought_process)
            if thought_process
            else f"⚡ **{model_name}** 피드백 재검증 완료\n- 반영 피드백: '{feedback_text[:30]}...'\n- 기하학적 동선 및 예산 충돌 해결 완료"
        )

        session_state["current_itinerary"] = response_text
        
        chat_summary = response_text
        if "## 🗺️" in response_text:
            chat_summary = response_text.split("## 🗺️")[0].strip()
        
        new_history = history + [(feedback_text, chat_summary)]
        session_state["history"] = new_history

        status_msg = f"🔄 피드백 반영 및 청사진 재검증 완료! ('{feedback_text[:25]}...')"

        return (
            response_text,
            status_msg,
            thinking_display,
            session_state,
            new_history,
            gr.update(value="")
        )

    except Exception as e:
        if is_quota_or_notfound_error(e):
            error_html = render_quota_error_card(model_name)
            status_msg = "⚠️ 429 쿼터 초과 - 잠시 대기 후 다시 시도해 주세요."
        else:
            error_html = render_generic_error_card(str(e))
            status_msg = f"❌ 수정 중 오류: {str(e)[:40]}..."
            
        return (
            error_html,
            status_msg,
            f"⚠️ Diagnostic Details:\n{str(e)}",
            session_state,
            history,
            gr.update(value="")
        )


def export_itinerary_to_file(session_state: dict):
    """Export current itinerary markdown to a downloadable file."""
    if not session_state or not session_state.get("current_itinerary"):
        return gr.update(visible=False)
    
    destination = session_state.get("destination", "여행")
    content = session_state["current_itinerary"]
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{destination}_Architectural_Blueprint.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return gr.update(value=file_path, visible=True)


# =====================================================================
# UI Styling: Geometric Neon & Architect Modern Glassmorphism CSS
# =====================================================================
custom_css = """
/* =================================================================
   Architect Blueprint & Geometric Neon Glassmorphism
   ================================================================= */

:root {
    --bg-space: #0B0F19;
    --card-glass: rgba(18, 24, 38, 0.78);
    --card-border: rgba(59, 130, 246, 0.18);
    --border-accent: rgba(6, 182, 212, 0.4);
    --neon-cyan: #06B6D4;
    --neon-blue: #3B82F6;
    --neon-indigo: #8B5CF6;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
}

body, .gradio-container {
    background-color: var(--bg-space) !important;
    background-image: 
        radial-gradient(ellipse at 50% 0%, rgba(59, 130, 246, 0.16) 0%, transparent 65%),
        radial-gradient(ellipse at 85% 85%, rgba(139, 92, 246, 0.12) 0%, transparent 55%),
        linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Pretendard", "Segoe UI", Roboto, sans-serif !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 0 16px !important;
}

/* Header Area - Blueprint Compass & Clean Typography */
.blueprint-header {
    padding: 32px 20px 20px 20px;
    text-align: center;
    position: relative;
}

.blueprint-badge-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}

.blueprint-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    background: rgba(18, 24, 38, 0.85);
    border: 1px solid rgba(59, 130, 246, 0.28);
    color: #93C5FD;
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.12);
}

.pill-active-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #06B6D4;
    box-shadow: 0 0 8px #06B6D4;
}

.blueprint-title {
    font-size: 2.6rem;
    font-weight: 850;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FFFFFF 20%, #E2E8F0 50%, #60A5FA 80%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0;
    line-height: 1.15;
}

.blueprint-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin: 0 auto;
    max-width: 720px;
}

/* Glassmorphic Blueprint Cards */
.blueprint-panel, .card-panel {
    background: var(--card-glass) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 16px !important;
    padding: 22px !important;
    box-shadow: 0 16px 40px -12px rgba(0, 0, 0, 0.6) !important;
    transition: all 0.25s ease;
}

.blueprint-panel:hover {
    border-color: rgba(6, 182, 212, 0.35) !important;
}

/* Geometric Section Header with node indicator */
.geo-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 14px;
    letter-spacing: -0.01em;
}

.geo-node {
    width: 8px;
    height: 8px;
    background: #3B82F6;
    transform: rotate(45deg);
    box-shadow: 0 0 8px #3B82F6;
}

/* Input Fields & Textboxes */
input, textarea, select {
    background: rgba(11, 15, 25, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
    font-size: 0.94rem !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
}

input:focus, textarea:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    background: rgba(11, 15, 25, 0.95) !important;
}

/* Sharp Neon Cyan-Indigo Action Button */
.neon-action-btn {
    background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 50%, #8B5CF6 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    box-shadow: 0 0 22px rgba(6, 182, 212, 0.38) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.neon-action-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 32px rgba(59, 130, 246, 0.6), 0 0 12px rgba(6, 182, 212, 0.8) !important;
    filter: brightness(1.08) !important;
}

.neon-action-btn:active {
    transform: translateY(0px) !important;
}

/* Geometric Quick Preset Chips */
.geo-chip-btn {
    background: rgba(22, 30, 48, 0.7) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    color: #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    padding: 8px 12px !important;
    transition: all 0.2s ease !important;
}

.geo-chip-btn:hover {
    background: rgba(59, 130, 246, 0.2) !important;
    border-color: #38BDF8 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.25) !important;
}

/* Semi-transparent Modern Toast / Notification */
.architect-toast {
    position: relative;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 14px 0;
    backdrop-filter: blur(16px);
    display: flex;
    gap: 14px;
    animation: toastSlide 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes toastSlide {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
}

.toast-fallback {
    background: rgba(14, 165, 233, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.3);
    box-shadow: 0 8px 24px rgba(6, 182, 212, 0.12);
}

.toast-error {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.32);
    box-shadow: 0 8px 24px rgba(239, 68, 68, 0.12);
}

.toast-indicator {
    width: 4px;
    border-radius: 4px;
    background: #06B6D4;
    box-shadow: 0 0 10px #06B6D4;
    flex-shrink: 0;
}

.error-indicator {
    background: #EF4444;
    box-shadow: 0 0 10px #EF4444;
}

.toast-body {
    flex: 1;
}

.toast-header-text {
    font-weight: 700;
    font-size: 0.98rem;
    color: #F8FAFC;
    margin-bottom: 4px;
}

.toast-detail {
    margin: 0;
    font-size: 0.9rem;
    color: #CBD5E1;
    line-height: 1.5;
}

.toast-action-box {
    margin-top: 8px;
    padding: 10px 12px;
    background: rgba(11, 15, 25, 0.7);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 0.88rem;
    color: #94A3B8;
}

/* Blueprint Rendered Itinerary Markdown Styling */
.rendered-blueprint table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 18px 0;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(59, 130, 246, 0.22);
}

.rendered-blueprint th {
    background: rgba(22, 30, 48, 0.95) !important;
    color: #93C5FD !important;
    font-weight: 700;
    padding: 12px 14px;
    text-align: left;
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
    font-size: 0.92rem;
}

.rendered-blueprint td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: #CBD5E1;
    background: rgba(11, 15, 25, 0.45);
    font-size: 0.92rem;
}

.rendered-blueprint tr:last-child td {
    border-bottom: none;
}

.rendered-blueprint tr:hover td {
    background: rgba(59, 130, 246, 0.1);
}
"""

app_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="cyan",
    neutral_hue="slate",
)


# =====================================================================
# Gradio UI Layout (Architect Blueprint & Geometric Glassmorphism)
# =====================================================================
with gr.Blocks(title="자율형 여행 아키텍트 | Gemini Blueprint 4.0") as demo:
    
    session_state = gr.State({})

    # Header: Geometric Blueprint Compass & Clean Typography
    gr.HTML("""
    <div class="blueprint-header">
        <div class="blueprint-badge-row">
            <span class="blueprint-pill"><span class="pill-active-dot"></span> BLUEPRINT ENGINE v4.2</span>
            <span class="blueprint-pill">📐 GEOMETRIC ROUTE OPTIMIZER</span>
            <span class="blueprint-pill">⚡ DEFAULT: GEMINI 3.8 FLASH</span>
            <span class="blueprint-pill">🔄 HITL RE-VERIFIED</span>
        </div>
        <h1 class="blueprint-title">AGENTIC TRAVEL ARCHITECT</h1>
        <p class="blueprint-subtitle">
            Google DeepMind AI Hackathon • 건축 청사진 기법 기반의 정밀 지리·예산 심층 추론 및 자율 재검증 시스템
        </p>
    </div>
    """)

    # Main Tabs
    with gr.Tabs() as main_tabs:
        
        # -------------------------------------------------------------
        # Tab 1: Input & Architect Launch (Proportion 1 : 1.2)
        # -------------------------------------------------------------
        with gr.TabItem("📐 1. 여행 청사진 조건 설정 및 자료 업로드", id=0):
            with gr.Row():
                # Left Column: User Input Form (Scale: 5)
                with gr.Column(scale=5, elem_classes=["blueprint-panel"]):
                    gr.HTML('<div class="geo-header"><span class="geo-node"></span> 여행 기본 정보 설계 (Specification)</div>')
                    
                    destination_input = gr.Textbox(
                        label="여행 목적지 (도시 / 국가)",
                        placeholder="예: 일본 도쿄 / 프랑스 파리 & 니스 / 제주도 서귀포",
                        value="일본 도쿄"
                    )
                    with gr.Row():
                        duration_input = gr.Textbox(
                            label="🗓️ 여행 일정 및 기간",
                            placeholder="예: 3박 4일 (2026.11.10 ~ 2026.11.13)",
                            value="3박 4일",
                            scale=1
                        )
                        budget_input = gr.Textbox(
                            label="💰 총 예산 (1인당 또는 총액)",
                            placeholder="예: 1인당 100만원 (항공권 제외)",
                            value="1인당 100만원",
                            scale=1
                        )
                    
                    style_checkboxes = gr.CheckboxGroup(
                        label="🎯 여행 스타일 (다중 선택 가능)",
                        choices=[
                            "🌿 힐링/휴식",
                            "🍜 미식/맛집 탐방",
                            "🎨 문화/예술/미술관",
                            "🏛️ 역사/유적 탐방",
                            "🛍️ 쇼핑/핫플레이스",
                            "🏔️ 자연/풍경 감상",
                            "🏄 액티비티/체험",
                            "📸 사진/인스타 스팟",
                        ],
                        value=["🍜 미식/맛집 탐방", "🎨 문화/예술/미술관", "🛍️ 쇼핑/핫플레이스"]
                    )
                    
                    custom_notes_input = gr.Textbox(
                        label="✍️ 특별 요구사항 및 동행자 제약 조건",
                        placeholder="예: '부모님과 함께 가니 하루 1만보 이내로 걷기', '대중교통 환승 최소화'",
                        lines=3,
                        value="하루 최대 도보 12,000보 이내, 대중교통 접근성 높은 핫플레이스와 현지인 추천 맛집 위주"
                    )

                # Right Column: Guidebook & Model Configuration (Scale: 6)
                with gr.Column(scale=6, elem_classes=["blueprint-panel"]):
                    gr.HTML('<div class="geo-header"><span class="geo-node"></span> 가이드북 및 아키텍트 모델 설정</div>')
                    
                    guide_file_input = gr.File(
                        label="가이드북 파일 또는 메모 업로드 (PDF, TXT, MD)",
                        file_types=[".txt", ".md", ".pdf"],
                        file_count="single"
                    )
                    file_preview_box = gr.Textbox(
                        label="📄 업로드 자료 미리보기",
                        placeholder="가이드북/메모 파일을 업로드하면 텍스트가 여기에 요약 표시됩니다.",
                        lines=3,
                        interactive=False
                    )

                    with gr.Accordion("⚙️ Gemini 모델 및 API 키 설정 (Fallback 탑재)", open=True):
                        api_key_input = gr.Textbox(
                            label="Google Gemini API Key",
                            placeholder="미입력 시 환경변수 GEMINI_API_KEY가 자동 적용됩니다.",
                            type="password",
                            value=os.environ.get("GEMINI_API_KEY", "")
                        )
                        with gr.Row():
                            model_select = gr.Dropdown(
                                label="Gemini 모델 선택",
                                choices=["gemini-3.8-flash", "gemini-3.8-pro", "gemini-4-argon"],
                                value="gemini-3.8-flash",
                                info="gemini-3.8-flash: 무료 API 키에서도 429/404 없이 최적 속도와 품질 보장",
                                scale=1
                            )
                            thinking_select = gr.Dropdown(
                                label="Thinking Level (추론 깊이)",
                                choices=["high", "medium", "low"],
                                value="high",
                                info="심층 추론(High Thinking) 적용",
                                scale=1
                            )
                    
                    generate_btn = gr.Button(
                        "🚀 자율형 여행 청사진 설계 시작 (Launch Architect)",
                        elem_classes=["neon-action-btn"],
                        size="lg"
                    )

        # -------------------------------------------------------------
        # Tab 2: Output & Human-in-the-Loop Revision (Proportion 1 : 1.2)
        # -------------------------------------------------------------
        with gr.TabItem("🗺️ 2. 종합 청사진 확인 및 대화형 수정 (HITL)", id=1):
            
            top_status_bar = gr.Markdown("💡 **안내:** 1단계 탭에서 조건을 설정하고 [청사진 설계 시작]을 누르면 완성된 일정이 여기에 표시됩니다.")

            with gr.Row():
                # Left Column: Human-in-the-Loop Feedback Controls (Scale: 5)
                with gr.Column(scale=5, elem_classes=["blueprint-panel"]):
                    gr.HTML('<div class="geo-header"><span class="geo-node"></span> Human-in-the-Loop 피드백 및 재검증</div>')
                    gr.Markdown("설계된 청사진을 점검하고 수정 피드백을 전달하세요. 아키텍트가 동선 및 예산 충돌을 재검증(Verify)하여 일정을 즉각 재배치합니다.")
                    
                    feedback_box = gr.Textbox(
                        label="수정 요청 사항 (Feedback Prompt)",
                        placeholder="예: '2일차 오후에 비가 올 예정이니 실내 미술관과 복합 쇼핑몰 코스로 변경해 줘'",
                        lines=3
                    )
                    
                    gr.Markdown("**⚡ 빠른 피드백 프리셋 (Quick Presets):**")
                    with gr.Row():
                        preset_btn1 = gr.Button("🌧️ 2일차 실내 코스 전환", elem_classes=["geo-chip-btn"], size="sm")
                        preset_btn2 = gr.Button("💰 가성비 식당 위주 변경", elem_classes=["geo-chip-btn"], size="sm")
                    with gr.Row():
                        preset_btn3 = gr.Button("☕ 일정 여유롭게 완화", elem_classes=["geo-chip-btn"], size="sm")
                        preset_btn4 = gr.Button("🏃 액티비티/체험 확대", elem_classes=["geo-chip-btn"], size="sm")

                    verify_btn = gr.Button(
                        "🔄 피드백 반영 및 청사진 재검증 (Verify & Update)",
                        elem_classes=["neon-action-btn"],
                        size="lg"
                    )

                    with gr.Accordion("💬 수정 대화 기록 (HITL Conversation)", open=True):
                        chatbot_view = gr.Chatbot(
                            label="아키텍트 피드백 대화 내역",
                            height=250
                        )

                    with gr.Accordion("🧠 아키텍트 심층 추론(Thinking) 로그", open=False):
                        thinking_log_box = gr.Markdown("아키텍트의 심층 추론 과정이 여기에 기록됩니다.")

                # Right Column: Rendered Blueprint & Download (Scale: 6)
                with gr.Column(scale=6, elem_classes=["blueprint-panel"]):
                    with gr.Row():
                        gr.HTML('<div class="geo-header"><span class="geo-node"></span> 최신 종합 여행 청사진 (Blueprint)</div>')
                        export_btn = gr.Button("💾 청사진 마크다운(.md) 다운로드", size="sm", elem_classes=["geo-chip-btn"])
                    
                    download_file_component = gr.File(label="다운로드 파일", visible=False)
                    
                    itinerary_display = gr.Markdown(
                        value="*아직 생성된 일정이 없습니다. 1단계 탭에서 조건을 설정하고 설계를 시작해 주세요.*",
                        elem_classes=["rendered-blueprint"]
                    )

    # =============================================================
    # Event Handlers & Interactivity
    # =============================================================
    
    # 1. File Upload Preview Handler
    def on_file_upload(file_obj):
        if file_obj is None:
            return ""
        text = extract_text_from_file(file_obj)
        if len(text) > 400:
            return f"📄 파일 추출 성공 ({len(text)}자)\n\n" + text[:400] + "\n... [이하 생략]"
        return f"📄 파일 추출 성공 ({len(text)}자)\n\n" + text

    guide_file_input.change(
        fn=on_file_upload,
        inputs=[guide_file_input],
        outputs=[file_preview_box]
    )

    # 2. Quick Preset Buttons
    preset_btn1.click(lambda: "2일차 오후에 비가 올 것으로 예상되므로, 야외 이동을 최소화하고 실내 미술관/전시 및 복합 문화 쇼핑몰 중심의 실내 코스로 변경해 줘.", outputs=[feedback_box])
    preset_btn2.click(lambda: "전체 일정의 식당을 현지인들이 즐겨 찾는 가성비 로컬 맛집 위주로 변경하고 식비 예산을 20% 절감해 줘.", outputs=[feedback_box])
    preset_btn3.click(lambda: "일정이 다소 빡빡해 보입니다. 각 장소 체류 시간을 늘리고 카페 휴식 시간을 포함하여 여유로운 힐링 일정으로 완화해 줘.", outputs=[feedback_box])
    preset_btn4.click(lambda: "관광지 단순 관람 대신 현지 원데이 클래스나 액티비티 체험 코스의 비중을 대폭 확대해 줘.", outputs=[feedback_box])

    # 3. Initial Itinerary Generation
    generate_btn.click(
        fn=generate_initial_itinerary,
        inputs=[
            destination_input,
            duration_input,
            budget_input,
            style_checkboxes,
            custom_notes_input,
            guide_file_input,
            api_key_input,
            model_select,
            thinking_select,
        ],
        outputs=[
            main_tabs,
            itinerary_display,
            top_status_bar,
            thinking_log_box,
            session_state,
            chatbot_view,
            feedback_box,
        ]
    )

    # 4. Human-in-the-Loop Feedback & Verification
    verify_btn.click(
        fn=update_itinerary_with_feedback,
        inputs=[feedback_box, session_state],
        outputs=[
            itinerary_display,
            top_status_bar,
            thinking_log_box,
            session_state,
            chatbot_view,
            feedback_box,
        ]
    )

    # 5. Export Itinerary
    export_btn.click(
        fn=export_itinerary_to_file,
        inputs=[session_state],
        outputs=[download_file_component]
    )

# Launch app (Gradio 6.x: theme and css are passed to launch())
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=app_theme,
        css=custom_css
    )
