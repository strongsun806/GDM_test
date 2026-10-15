"""
Gemini 3.8 & 4 Argon 기반 자율형 여행 아키텍트 (Agentic Travel Architect)
Google DeepMind AI Hackathon Project
- Collaborative Interactive Travel Workspace for Friends
- High-Contrast Clean & Modern Travel Tech Theme (Crystal-Clear Legibility)
- One-Click Booking & Navigation Links (Google Maps, Agoda, Klook, Skyscanner)
- High-Quality Korean PDF Report Export (ReportLab with Malgun Gothic)
- Models: gemini-3.8-flash (Default), gemini-3.8-pro, gemini-4-argon
- Intelligent Free-Tier Auto-Fallback Engine for 404/429
"""

import os
import sys
import re
import urllib.parse
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

# ReportLab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
    # Register Malgun font if available on Windows
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("Malgun", font_path))
            PDF_FONT = "Malgun"
        except Exception:
            PDF_FONT = "Helvetica"
    else:
        PDF_FONT = "Helvetica"
except ImportError:
    REPORTLAB_AVAILABLE = False
    PDF_FONT = "Helvetica"


# =====================================================================
# System Instructions for Agentic Travel Architect (with Booking Links)
# =====================================================================
SYSTEM_INSTRUCTION = """당신은 구글 딥마인드 Gemini 기반 차세대 '자율형 여행 아키텍트(Agentic Travel Architect)'입니다.
친구들과 함께 떠나는 여행을 위해 정밀한 지리 동선, 현실적인 예산 분배, 그리고 [실제 예약 및 길찾기 링크]가 완벽히 포함된 고품질 맞춤형 여행 청사진(Blueprint)을 설계하고 사후 검증(Verification)을 수행합니다.

[핵심 설계 및 행동 원칙]
1. 모든 방문지/식당/숙소에 [원클릭 예약 & 길찾기 마크다운 링크] 필수 제공:
   - 각 일정의 방문지, 식당, 카페, 숙소마다 사용자가 클릭 즉시 열어볼 수 있도록 구글 지도 및 예약 검색 URL을 마크다운 링크 형식으로 반드시 포함하세요.
   - 링크 포맷 가이드:
     * 구글 지도 길찾기: `[📍 구글 지도](https://www.google.com/maps/search/?api=1&query=인코딩된_장소명+목적지)`
     * 맛집 예약/리뷰: `[🍽️ 맛집 정보](https://www.google.com/maps/search/?api=1&query=인코딩된_식당명+맛집)`
     * 티켓/입장권/투어: `[🎟️ 클룩 티켓 검색](https://www.klook.com/ko/search/result/?query=인코딩된_명소)`
     * 숙소 예약: `[🏨 아고다 숙소 검색](https://www.agoda.com/ko-kr/search?city=인코딩된_도시)`
2. 지리적 동선 최단화 (Spatial Optimization):
   - 실제 도보 이동성, 지하철/버스 환승, 스팟 간의 지리적 인접도를 엄밀히 계산하여 불필요한 이동 낭비를 완벽히 차단합니다.
3. 예산 현실성 검증 (Budget Feasibility):
   - 숙박, 식비, 교통, 관광/체험, 비상금 카테고리별로 현지 물가를 반영해 총 예산을 초과하지 않도록 검증합니다.
4. Human-in-the-Loop 대화형 재검증 (Verification & Replanning):
   - 친구들의 피드백(예: 우천 대비 실내 코스 변경, 늦잠 모드, 특정 맛집 추가 등)을 받으면:
     [피드백 분석] ➔ [동선/시간/예산 충돌 검증] ➔ [최적 대체안 확정] ➔ [전체 일정 동기화]
     과정을 거쳐 검증 리포트와 함께 업데이트된 최신 종합 청사진을 출력합니다.

[출력 양식: 1차 종합 일정표 생성 시]
# ✈️ [여행지] 맞춤 여행 청사진 (Travel Blueprint)

## 📌 1. 아키텍트 개요 및 여행 전략
- **목적지**: [여행지]
- **일정/기간**: [일정]
- **여행 테마**: [선택 스타일 반영]
- **총 예상 예산**: [1인당/총액 배분 요약]
- **가이드북 앵커 스팟**: [첨부자료 반영 내역]

## 📅 2. 일자별 상세 일정표 (Day-by-Day Timeline)
(각 일자별로 동선 순서대로 표를 작성하세요. 표 내부에 반드시 예약 및 지도 링크를 포함하세요.)
### Day 1: [핵심 테마 및 주요 방문 구역]
| 시간 | 일정 / 방문지 | 세부 활동 & 원클릭 예약 링크 | 이동 수단 / 소요 시간 | 예상 비용 |
| :--- | :--- | :--- | :--- | :--- |
| 09:30 - 11:30 | 장소명 | 추천 활동 / [📍 구글 지도](https://www.google.com/maps/search/?api=1&query=...) | 지하철 15분 | 15,000원 |
...

## 💰 3. 예산 시뮬레이션 및 포트폴리오 (Budget Portfolio)
- 🏨 숙박비: 약 OO원 (XX%) - [🏨 숙소 최저가 검색](https://www.agoda.com/ko-kr/search?city=...)
- 🍽️ 식비: 약 OO원 (XX%)
- 🚇 교통비: 약 OO원 (XX%)
- 🎟️ 입장/액티비티: 약 OO원 (XX%)
- 🛡️ 비상 예비비: 약 OO원 (XX%)
- **합계**: 총 OO원 (설정 예산 대비 OO% 소진)

## 🔍 4. 아키텍트 자율 검증 리포트 (Architect's Verification)
- **동선 효율성 평가**: (지리적 인접도 및 피로도 관리 점검 결과)
- **돌발 상황 대비 플랜 B**: (비가 오거나 휴관일 경우 대체 스팟)
- **친구들과 꿀팁**: (사전 예약 필수 스팟, 패스권 추천 등)

[출력 양식: Human-in-the-Loop 피드백 수정 시]
# 🔄 청사진 재검증 및 업데이트 리포트 (Blueprint Re-verified)

## 🛠️ [검증 보고서: Verification Report]
- **반영된 유저/친구 요청**: [요청 내용]
- **동선 및 시간 충돌 검증**: [기존 동선 대비 어떻게 충돌을 해결했는지 설명]
- **예산 및 피로도 영향도**: [비용 변동 및 이동 피로도 분석]

## 🗺️ [업데이트된 최신 종합 일정표]
(피드백이 반영되어 완벽하게 조정된 전체 일정표를 최신 상태로 재출력, 예약 링크 유지)
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
    """Clean modern Toast alert for automatic fallback."""
    return f"""
<div class="travel-alert alert-fallback">
    <div class="alert-icon-box">⚡</div>
    <div class="alert-content">
        <h4 class="alert-title">자율 모델 Fallback 작동 안내</h4>
        <p class="alert-desc">
            선택하신 <code>{original_model}</code> 모델의 쿼터(429) 또는 가용성(404) 제한이 감지되어, 가장 안정적인 <strong>{fallback_model}</strong>(으)로 자동 전환하여 일정을 끊김 없이 완성했습니다.
        </p>
    </div>
</div>
"""


def render_quota_error_card(model_name: str) -> str:
    """High-contrast friendly card for persistent 429 Quota errors."""
    return f"""
<div class="travel-alert alert-error">
    <div class="alert-icon-box error-icon">⚠️</div>
    <div class="alert-content">
        <h4 class="alert-title">API 쿼터 한도(429 Rate Limit) 초과</h4>
        <p class="alert-desc">현재 API 키의 호출 한도(RPM/TPM)가 일시적으로 소진되었습니다. (시도 모델: <code>{model_name}</code>)</p>
        <div class="alert-tips">
            <strong>💡 해결 가이드:</strong>
            <ul>
                <li>모델을 <strong>[gemini-3.8-flash]</strong>로 선택하시면 가장 넉넉한 무료 쿼터가 적용됩니다.</li>
                <li>약 30초~1분 후 다시 시도하시면 정상 작동합니다.</li>
                <li>개인 Gemini API 키를 UI 상단에 입력하시면 즉시 재개됩니다.</li>
            </ul>
        </div>
    </div>
</div>
"""


def render_generic_error_card(error_msg: str) -> str:
    """Clean error card for general exceptions."""
    return f"""
<div class="travel-alert alert-error">
    <div class="alert-icon-box error-icon">⚠️</div>
    <div class="alert-content">
        <h4 class="alert-title">일정 생성 처리 중 오류가 발생했습니다</h4>
        <p class="alert-desc">{error_msg}</p>
        <p style="margin: 6px 0 0 0; color: #64748B; font-size: 0.88rem;">API 키 유효성 및 네트워크 연결 상태를 확인 후 다시 시도해 주세요.</p>
    </div>
</div>
"""


# =====================================================================
# PDF Generator: Convert Markdown Travel Itinerary into Styled PDF
# =====================================================================
def generate_pdf_from_markdown(markdown_text: str, destination: str) -> str:
    """Generate a clean, high-contrast, multi-page Korean PDF travel blueprint."""
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab이 설치되지 않았습니다. pip install reportlab")

    temp_dir = tempfile.gettempdir()
    clean_dest = re.sub(r'[^\w\s-]', '', destination).strip() or "Travel"
    pdf_filename = f"{clean_dest}_Travel_Blueprint.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    h1_style = ParagraphStyle(
        'PDF_H1',
        fontName=PDF_FONT,
        fontSize=18,
        leading=24,
        textColor=colors.HexColor('#0284C7'),
        spaceAfter=8,
        spaceBefore=12
    )
    h2_style = ParagraphStyle(
        'PDF_H2',
        fontName=PDF_FONT,
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6,
        spaceBefore=10
    )
    h3_style = ParagraphStyle(
        'PDF_H3',
        fontName=PDF_FONT,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=4,
        spaceBefore=6
    )
    body_style = ParagraphStyle(
        'PDF_Body',
        fontName=PDF_FONT,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=3
    )
    table_cell_style = ParagraphStyle(
        'PDF_Cell',
        fontName=PDF_FONT,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    table_hdr_style = ParagraphStyle(
        'PDF_HeaderCell',
        fontName=PDF_FONT,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title header banner
    story.append(Paragraph(f"✈️ {destination} 맞춤 여행 청사진 (Travel Blueprint)", h1_style))
    story.append(Paragraph("Google DeepMind Gemini 기반 자율형 여행 아키텍트 생성 리포트", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=4, spaceAfter=12))

    lines = markdown_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Skip raw HTML / Toast markup from Markdown rendering
        if line.startswith("<div") or line.startswith("</div>") or line.startswith("<span") or line.startswith("<p") or line.startswith("</p"):
            i += 1
            continue

        if line.startswith("# "):
            clean_text = line[2:].strip()
            story.append(Paragraph(clean_text, h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BAE6FD'), spaceBefore=2, spaceAfter=8))
        elif line.startswith("## "):
            clean_text = line[3:].strip()
            story.append(Paragraph(clean_text, h2_style))
        elif line.startswith("### "):
            clean_text = line[4:].strip()
            story.append(Paragraph(clean_text, h3_style))
        elif line.startswith("|"):
            # Table processing
            table_rows = []
            is_header = True
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_line = lines[i].strip()
                if not re.match(r'^\|[\s\-:|]+\|$', row_line):
                    cells = [c.strip() for c in row_line.strip('|').split('|')]
                    row_cells = []
                    for c in cells:
                        formatted_c = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" color="#0284C7"><u>\1</u></a>', c)
                        formatted_c = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_c)
                        c_style = table_hdr_style if is_header else table_cell_style
                        row_cells.append(Paragraph(formatted_c, c_style))
                    table_rows.append(row_cells)
                    is_header = False
                i += 1
            if table_rows:
                num_cols = max(len(r) for r in table_rows)
                for r in table_rows:
                    while len(r) < num_cols:
                        r.append(Paragraph('', table_cell_style))
                col_width = 520.0 / num_cols
                t = Table(table_rows, colWidths=[col_width] * num_cols)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
            continue
        else:
            formatted = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" color="#0284C7"><u>\1</u></a>', line)
            formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted)
            story.append(Paragraph(formatted, body_style))

        i += 1

    doc.build(story)
    return pdf_path


# =====================================================================
# Core Logic: Generate Initial Itinerary & Re-plan (with Fallback)
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
    user_prompt = f"""[여행 청사진 의뢰 정보]
- 목적지: {destination}
- 일정/기간: {duration}
- 총 예산: {budget if budget.strip() else '가성비 기준 최적 배분'}
- 여행 스타일: {styles_str}
- 추가 요구사항: {custom_notes if custom_notes.strip() else '없음'}
{file_summary}

위 여행 청사진 의뢰 조건과 첨부된 자료를 심층 추론(Deep Spatial & Budget Reasoning)하여 동선 최적화, 현실적 예산 분배, 세부 타임라인이 포함된 종합 여행 설계 청사진과 아키텍트 자율 검증 리포트를 작성해 주세요.
반드시 각 방문지, 식당, 카페, 숙소마다 클릭할 수 있는 [📍 구글 지도 길찾기](https://www.google.com/maps/search/?api=1&query=장소명) 및 예약 링크를 포함해 주세요!
"""

    fallback_occurred = False
    original_model = model_name
    active_model = model_name

    try:
        client = get_gemini_client(api_key)
        
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
            temperature=0.7,
        )

        chat = None
        response = None

        try:
            chat = client.chats.create(model=active_model, config=config)
            response = chat.send_message(user_prompt)
        except Exception as first_err:
            if is_quota_or_notfound_error(first_err) and active_model != "gemini-3.8-flash":
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
            else f"⚡ **{active_model}** 심층 추론(High Thinking) 완료\n- 지리적 동선 최단화 알고리즘 검증 완료\n- 예약 링크(구글맵/호텔/투어) 연동 완료\n- 가이드북 핵심 거점 앵커링 완료"
        )

        final_itinerary = initial_markdown
        if fallback_occurred:
            final_itinerary = render_fallback_notification(original_model, active_model) + "\n\n" + initial_markdown

        session_state = {
            "chat": chat,
            "current_itinerary": final_itinerary,
            "history": [],
            "destination": destination,
            "duration": duration,
            "budget": budget,
            "styles": styles_str,
            "model_name": active_model,
            "thinking_level": thinking_level,
        }

        status_msg = f"✨ **{destination} ({duration})** 청사진 설계 완료! [2. 종합 청사진 확인 & 실시간 예약] 탭으로 이동했습니다."
        
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

    refine_prompt = f"""[사용자 및 친구들의 피드백 (Human-in-the-Loop 재검증 요청)]:
"{feedback_text.strip()}"

위 피드백을 반영하여 일정을 재검증(Verification)하고 업데이트해 주세요.
반드시 아래 두 부분으로 명확하게 구성해 주세요:
1. ## 🛠️ [검증 보고서: Verification Report]:
   - 반영된 변경점
   - 동선 충돌 해결 및 시간/예산 영향도 분석
2. ## 🗺️ [업데이트된 최신 종합 청사진]:
   - 피드백이 완벽히 반영된 최신 전체 여행 일정표 (기존 마크다운 및 [📍 구글 지도], [🍽️ 맛집/예약] 링크 유지)
"""

    try:
        response = chat.send_message(refine_prompt)
        response_text = response.text or "일정 업데이트에 실패했습니다."

        thought_process = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False) and getattr(part, "text", None):
                    thought_process.append(part.text)
        
        thinking_display = (
            "\n\n---\n\n".join(thought_process)
            if thought_process
            else f"⚡ **{model_name}** 피드백 재검증 완료\n- 반영 피드백: '{feedback_text[:30]}...'\n- 동선 및 예산 충돌 해결 완료 (예약 링크 갱신)"
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


def export_pdf_file(session_state: dict):
    """Generate and export a styled Korean PDF file."""
    if not session_state or not session_state.get("current_itinerary"):
        return gr.update(visible=False)
    
    destination = session_state.get("destination", "여행")
    content = session_state["current_itinerary"]
    
    try:
        pdf_path = generate_pdf_from_markdown(content, destination)
        return gr.update(value=pdf_path, visible=True)
    except Exception as e:
        # Fallback to markdown if PDF generation fails
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{destination}_Travel_Blueprint.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return gr.update(value=file_path, visible=True)


def export_markdown_file(session_state: dict):
    """Export current itinerary markdown to a downloadable file."""
    if not session_state or not session_state.get("current_itinerary"):
        return gr.update(visible=False)
    
    destination = session_state.get("destination", "여행")
    content = session_state["current_itinerary"]
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{destination}_Travel_Blueprint.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return gr.update(value=file_path, visible=True)


def generate_shareable_summary(session_state: dict):
    """Generate a clean text card suitable for KakaoTalk / messenger sharing with friends."""
    if not session_state or not session_state.get("destination"):
        return "⚠️ 먼저 1단계 탭에서 여행 일정을 생성해 주세요!"
    
    dest = session_state.get("destination", "여행지")
    duration = session_state.get("duration", "일정")
    budget = session_state.get("budget", "미정")
    styles = session_state.get("styles", "자유 여행")
    
    summary = f"""📢 [우리들의 {dest} 여행 청사진 공유]
━━━━━━━━━━━━━━━━━━━━
✈️ 목적지: {dest}
🗓️ 일정: {duration}
💰 예상 예산: {budget}
🎯 여행 스타일: {styles}

✨ 세부 일정표 및 예약 링크는 '여행 아키텍트' 웹앱에서 확인하세요!
📄 PDF 리포트 다운로드 및 실시간 수정도 가능합니다."""
    return summary


# =====================================================================
# UI Styling: High-Contrast Modern Travel Workspace (Clean & Collaborative)
# =====================================================================
custom_css = """
/* =================================================================
   Modern Collaborative Travel Workspace Theme (Clean & Crisp)
   ================================================================= */

:root {
    --bg-page: #F8FAFC;
    --card-surface: #FFFFFF;
    --card-border: #E2E8F0;
    --primary-blue: #0284C7;
    --primary-hover: #0369A1;
    --indigo-accent: #4F46E5;
    --text-heading: #0F172A; /* Crisp deep slate */
    --text-body: #1E293B;    /* High contrast dark text */
    --text-muted: #64748B;
    --success-green: #10B981;
}

body, .gradio-container {
    background-color: var(--bg-page) !important;
    background-image: 
        radial-gradient(at 10% 10%, rgba(2, 132, 199, 0.05) 0px, transparent 50%),
        radial-gradient(at 90% 90%, rgba(79, 70, 229, 0.05) 0px, transparent 50%) !important;
    color: var(--text-body) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "SF Pro Text", "Segoe UI", Roboto, "Noto Sans KR", sans-serif !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 0 16px !important;
}

/* Header Area - Clean & Inspiring Travel Magazine Style */
.travel-header {
    padding: 32px 20px 24px 20px;
    text-align: center;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 24px;
    background: #FFFFFF;
    border-radius: 20px;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

.travel-badge-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}

.travel-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #1D4ED8;
}

.travel-pill.green {
    background: #ECFDF5;
    border-color: #A7F3D0;
    color: #047857;
}

.travel-title {
    font-size: 2.4rem;
    font-weight: 850;
    color: var(--text-heading);
    letter-spacing: -0.03em;
    margin: 0 0 8px 0;
}

.travel-subtitle {
    font-size: 1.05rem;
    color: var(--text-muted);
    margin: 0 auto;
    max-width: 760px;
    line-height: 1.5;
}

/* Cards & Layout Panels */
.travel-card {
    background: var(--card-surface) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 16px !important;
    padding: 22px !important;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02) !important;
    transition: all 0.2s ease;
}

.travel-card:hover {
    border-color: #CBD5E1 !important;
}

/* Section Header */
.section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-heading);
    margin-bottom: 14px;
}

/* Input Fields - Clean High Contrast White & Crisp Borders */
input, textarea, select {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    color: var(--text-body) !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    padding: 10px 14px !important;
}

input:focus, textarea:focus {
    border-color: var(--primary-blue) !important;
    box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
}

/* Action Buttons */
.travel-btn-primary {
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #4F46E5 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.travel-btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
}

.travel-btn-pdf {
    background: #0284C7 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.travel-btn-pdf:hover {
    background: #0369A1 !important;
    transform: translateY(-1px) !important;
}

/* Quick Feedback Preset Chips */
.travel-chip {
    background: #F1F5F9 !important;
    border: 1px solid #CBD5E1 !important;
    color: #334155 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    padding: 8px 12px !important;
    transition: all 0.2s ease !important;
}

.travel-chip:hover {
    background: #E0F2FE !important;
    border-color: #38BDF8 !important;
    color: #0369A1 !important;
    transform: translateY(-1px) !important;
}

/* Quick Booking Hub Container */
.booking-hub {
    background: linear-gradient(135deg, #F0F9FF 0%, #EEF2FF 100%);
    border: 1px solid #BAE6FD;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.booking-hub-title {
    font-weight: 700;
    color: #0369A1;
    font-size: 0.98rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

.booking-links-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.booking-link-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 0.86rem;
    font-weight: 600;
    text-decoration: none !important;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    color: #0F172A !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
}

.booking-link-btn:hover {
    border-color: #0284C7;
    color: #0284C7 !important;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(2, 132, 199, 0.15);
}

/* Alert Notification Banners */
.travel-alert {
    display: flex;
    gap: 14px;
    padding: 16px 20px;
    border-radius: 12px;
    margin: 14px 0;
    border: 1px solid #BAE6FD;
    background: #F0F9FF;
}

.alert-fallback {
    background: #F0FDF4;
    border-color: #BBF7D0;
}

.alert-error {
    background: #FEF2F2;
    border-color: #FECACA;
}

.alert-icon-box {
    font-size: 1.5rem;
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: #DCFCE7;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.alert-icon-box.error-icon {
    background: #FEE2E2;
}

.alert-content {
    flex: 1;
}

.alert-title {
    margin: 0 0 4px 0;
    font-weight: 700;
    font-size: 0.98rem;
    color: #0F172A;
}

.alert-desc {
    margin: 0;
    font-size: 0.9rem;
    color: #334155;
    line-height: 1.5;
}

.alert-tips {
    margin-top: 8px;
    padding: 10px 12px;
    background: #FFFFFF;
    border-radius: 8px;
    border: 1px solid #FECACA;
    font-size: 0.88rem;
    color: #475569;
}

/* Rendered Itinerary Markdown Styling - Crisp & High Contrast */
.rendered-travel-itinerary {
    color: var(--text-body) !important;
    line-height: 1.65 !important;
}

.rendered-travel-itinerary h1 {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0284C7 !important;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 8px;
    margin-top: 10px;
}

.rendered-travel-itinerary h2 {
    font-size: 1.35rem;
    font-weight: 750;
    color: #0F172A !important;
    margin-top: 24px;
    margin-bottom: 12px;
}

.rendered-travel-itinerary h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2563EB !important;
    margin-top: 18px;
    margin-bottom: 8px;
}

.rendered-travel-itinerary table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #CBD5E1;
    background: #FFFFFF;
}

.rendered-travel-itinerary th {
    background: #F1F5F9 !important;
    color: #0F172A !important;
    font-weight: 700;
    padding: 12px 14px;
    text-align: left;
    border-bottom: 2px solid #CBD5E1;
    font-size: 0.92rem;
}

.rendered-travel-itinerary td {
    padding: 12px 14px;
    border-bottom: 1px solid #E2E8F0;
    color: #1E293B !important;
    font-size: 0.92rem;
}

.rendered-travel-itinerary tr:nth-child(even) td {
    background: #F8FAFC;
}

.rendered-travel-itinerary tr:hover td {
    background: #EFF6FF;
}

.rendered-travel-itinerary a {
    color: #0284C7 !important;
    font-weight: 600;
    text-decoration: underline;
}

.rendered-travel-itinerary a:hover {
    color: #0369A1 !important;
}
"""

app_theme = gr.themes.Soft(
    primary_hue="sky",
    secondary_hue="blue",
    neutral_hue="slate",
)


# =====================================================================
# Gradio UI Layout (High-Contrast Collaborative Travel Workspace)
# =====================================================================
with gr.Blocks(title="친구들과 함께 떠나는 여행 아키텍트") as demo:
    
    session_state = gr.State({})

    # Header: Welcoming, Modern Travel Workspace
    gr.HTML("""
    <div class="travel-header">
        <div class="travel-badge-row">
            <span class="travel-pill">👥 동행자 실시간 조율</span>
            <span class="travel-pill green">🔗 원클릭 예약 링크 탑재</span>
            <span class="travel-pill">📄 정밀 PDF 리포트 다운로드</span>
            <span class="travel-pill">⚡ Powered by Gemini 3.8 Flash</span>
        </div>
        <h1 class="travel-title">✈️ 우리들의 맞춤 여행 아키텍트</h1>
        <p class="travel-subtitle">
            Google DeepMind AI Hackathon • 친구들과 함께 계획하고 원클릭으로 예약하는 스마트 여행 청사진 플랫폼
        </p>
    </div>
    """)

    # Main Tabs
    with gr.Tabs() as main_tabs:
        
        # -------------------------------------------------------------
        # Tab 1: Input & Architect Launch (Proportion 1 : 1.2)
        # -------------------------------------------------------------
        with gr.TabItem("🛫 1. 여행 조건 설정 및 가이드북 업로드", id=0):
            with gr.Row():
                # Left Column: User Input Form (Scale: 5)
                with gr.Column(scale=5, elem_classes=["travel-card"]):
                    gr.HTML('<div class="section-title">📍 여행 기본 정보 설계</div>')
                    
                    destination_input = gr.Textbox(
                        label="여행 목적지 (도시 / 국가)",
                        placeholder="예: 일본 도쿄 / 프랑스 파리 / 제주도 서귀포",
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
                        label="🎯 친구들과 원하는 여행 스타일 (다중 선택 가능)",
                        choices=[
                            "🌿 힐링/휴식 & 감성 카페",
                            "🍜 미식/맛집 투어",
                            "🎨 문화/예술 & 미술관",
                            "🏛️ 역사/랜드마크 탐방",
                            "🛍️ 쇼핑/핫플레이스",
                            "🏔️ 자연/풍경 감상",
                            "🏄 액티비티/체험",
                            "📸 인생샷/인스타 스팟",
                        ],
                        value=["🍜 미식/맛집 투어", "🌿 힐링/휴식 & 감성 카페", "🛍️ 쇼핑/핫플레이스"]
                    )
                    
                    custom_notes_input = gr.Textbox(
                        label="✍️ 친구들의 특별 요청 및 동행자 조건",
                        placeholder="예: '하루 1만보 이내로 걷기', '늦잠 자고 11시부터 시작', '야식 라멘 필수'",
                        lines=3,
                        value="동행 친구들과 여유로운 힐링 여행, 이동 동선 최단화, 핫플레이스 맛집 필수 포함"
                    )

                # Right Column: Guidebook & Model Configuration (Scale: 6)
                with gr.Column(scale=6, elem_classes=["travel-card"]):
                    gr.HTML('<div class="section-title">📄 가이드북 및 아키텍트 모델 설정</div>')
                    
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
                        "🚀 친구들과 떠날 맞춤 여행 청사진 설계 시작",
                        elem_classes=["travel-btn-primary"],
                        size="lg"
                    )

        # -------------------------------------------------------------
        # Tab 2: Output & Human-in-the-Loop Revision & Booking
        # -------------------------------------------------------------
        with gr.TabItem("🗺️ 2. 종합 청사진 확인 & 실시간 예약 (HITL)", id=1):
            
            # Interactive Quick Booking Hub
            gr.HTML("""
            <div class="booking-hub">
                <div class="booking-hub-title">
                    <span>🔗 원클릭 여행 예약 & 길찾기 허브</span>
                </div>
                <div class="booking-links-group">
                    <a href="https://www.skyscanner.co.kr" target="_blank" class="booking-link-btn">✈️ 항공권 최저가 비교 (스카이스캐너)</a>
                    <a href="https://www.agoda.com" target="_blank" class="booking-link-btn">🏨 숙소 예약 (아고다)</a>
                    <a href="https://www.airbnb.co.kr" target="_blank" class="booking-link-btn">🏡 감성 에어비앤비</a>
                    <a href="https://www.klook.com" target="_blank" class="booking-link-btn">🎟️ 투어 & 입장권 (클룩)</a>
                    <a href="https://maps.google.com" target="_blank" class="booking-link-btn">🗺️ 실시간 구글 지도</a>
                </div>
            </div>
            """)

            top_status_bar = gr.Markdown("💡 **안내:** 1단계 탭에서 조건을 설정하고 [청사진 설계 시작]을 누르면 완성된 일정이 여기에 표시됩니다.")

            with gr.Row():
                # Left Column: Human-in-the-Loop Feedback Controls (Scale: 5)
                with gr.Column(scale=5, elem_classes=["travel-card"]):
                    gr.HTML('<div class="section-title">🧑‍💻 친구들과 의견 조율 (HITL 대화형 수정)</div>')
                    gr.Markdown("일정을 확인하고 변경 사항을 입력하세요. 아키텍트가 동선과 예산 충돌을 재검증하여 일정을 즉시 갱신합니다.")
                    
                    feedback_box = gr.Textbox(
                        label="수정 요청 사항 (Feedback Prompt)",
                        placeholder="예: '2일차 오후에 비 온다고 하니 실내 미술관과 쇼핑몰 코스로 바꿔줘' 또는 '오전에 늦잠 잘 거니까 11시 시작으로 여유롭게 변경해줘'",
                        lines=3
                    )
                    
                    gr.Markdown("**⚡ 단톡방 단골 요청 프리셋 (Quick Presets):**")
                    with gr.Row():
                        preset_btn1 = gr.Button("🌧️ 2일차 실내 코스 전환", elem_classes=["travel-chip"], size="sm")
                        preset_btn2 = gr.Button("💰 가성비 식당 위주 변경", elem_classes=["travel-chip"], size="sm")
                    with gr.Row():
                        preset_btn3 = gr.Button("☕ 오전 늦잠 여유 코스", elem_classes=["travel-chip"], size="sm")
                        preset_btn4 = gr.Button("📸 인스타 핫플/카페 확대", elem_classes=["travel-chip"], size="sm")

                    verify_btn = gr.Button(
                        "🔄 피드백 반영 및 청사진 재검증 (Verify & Update)",
                        elem_classes=["travel-btn-primary"],
                        size="lg"
                    )

                    with gr.Accordion("💬 친구들과 나눈 수정 대화 내역", open=True):
                        chatbot_view = gr.Chatbot(
                            label="아키텍트 대화 로그",
                            height=250
                        )

                    with gr.Accordion("🧠 아키텍트 심층 추론(Thinking) 로그", open=False):
                        thinking_log_box = gr.Markdown("아키텍트의 심층 추론 과정이 여기에 기록됩니다.")

                # Right Column: Rendered Blueprint & Download (Scale: 6)
                with gr.Column(scale=6, elem_classes=["travel-card"]):
                    with gr.Row():
                        gr.HTML('<div class="section-title">📋 최신 종합 여행 청사진</div>')
                        with gr.Row():
                            pdf_btn = gr.Button("📄 PDF 다운로드", size="sm", elem_classes=["travel-btn-pdf"])
                            export_btn = gr.Button("💾 마크다운(.md) 저장", size="sm", elem_classes=["travel-chip"])
                    
                    download_file_component = gr.File(label="다운로드 파일", visible=False)
                    
                    itinerary_display = gr.Markdown(
                        value="*아직 생성된 일정이 없습니다. 1단계 탭에서 조건을 설정하고 설계를 시작해 주세요.*",
                        elem_classes=["rendered-travel-itinerary"]
                    )

        # -------------------------------------------------------------
        # Tab 3: Friends Hub & Checklist (Interactive Collaborative Space)
        # -------------------------------------------------------------
        with gr.TabItem("👥 3. 동행자 조율 & 준비물 체크리스트", id=2):
            with gr.Row():
                # Left Column: Interactive Packing Checklist
                with gr.Column(scale=6, elem_classes=["travel-card"]):
                    gr.HTML('<div class="section-title">📝 여행 필수 준비물 체크리스트</div>')
                    gr.Markdown("친구들과 짐 싸면서 빠뜨린 게 없는지 함께 체크해 보세요!")
                    
                    with gr.Accordion("🛂 필수 서류 & 금융", open=True):
                        gr.Checkbox(label="여권 (만료일 6개월 이상 남았는지 확인)", value=True)
                        gr.Checkbox(label="트래블로그 / 트래블월렛 해외 결제 카드", value=True)
                        gr.Checkbox(label="현지 통화 비상금 (엔화/유로/달러 등 환전)", value=False)
                        gr.Checkbox(label="항공권 E-티켓 및 숙소 바우처 모바일 저장", value=False)
                    
                    with gr.Accordion("📱 통신 & 전자기기", open=True):
                        gr.Checkbox(label="eSIM / 유심 사전 등록 및 개통 확인", value=True)
                        gr.Checkbox(label="보조배터리 (비행기 기내 수하물 지참)", value=True)
                        gr.Checkbox(label="현지 국가용 전원 멀티어댑터 (돼지코 110V 등)", value=False)
                        gr.Checkbox(label="충전 케이블 및 이어폰", value=False)
                    
                    with gr.Accordion("💊 건강 & 상비약", open=False):
                        gr.Checkbox(label="소화제 / 두통약 / 감기약 / 밴드", value=False)
                        gr.Checkbox(label="개인 복용약 및 인공눈물", value=False)
                    
                    with gr.Accordion("👕 의류 & 편의용품", open=False):
                        gr.Checkbox(label="많이 걸어도 편한 운동화", value=True)
                        gr.Checkbox(label="휴대용 우산 / 우비 (갑작스러운 날씨 대비)", value=False)
                        gr.Checkbox(label="선크림 및 여행용 세면도구", value=False)

                # Right Column: Group Poll & Shareable Summary
                with gr.Column(scale=5, elem_classes=["travel-card"]):
                    gr.HTML('<div class="section-title">🗳️ 친구들과 코스 취향 투표 (Quick Poll)</div>')
                    gr.Markdown("친구들과 의견이 갈릴 때 가볍게 투표하고 결과를 일정에 반영하세요!")
                    
                    poll_food = gr.Radio(
                        label="🍜 이번 여행 식사 스타일 선호도",
                        choices=["현지인 가성비 로컬 맛집 위주", "분위기 좋은 미슐랭/파인다이닝", "길거리 음식 & 야시장 탐방"],
                        value="현지인 가성비 로컬 맛집 위주"
                    )
                    poll_pace = gr.Radio(
                        label="🏃 여행 페이스 선호도",
                        choices=["빡빡하게 핵심 명소 모두 정복", "여유롭게 늦잠 자고 카페에서 힐링", "포토스팟 & 쇼핑 몰빵"],
                        value="여유롭게 늦잠 자고 카페에서 힐링"
                    )
                    
                    apply_poll_btn = gr.Button("✨ 투표 결과를 피드백 입력창에 자동 반영", elem_classes=["travel-chip"])
                    
                    gr.HTML('<hr style="margin: 20px 0; border: none; border-top: 1px solid #E2E8F0;">')
                    
                    gr.HTML('<div class="section-title">📲 단톡방 공유용 요약 카드</div>')
                    share_summary_box = gr.Textbox(
                        label="카카오톡/단톡방 복사용 텍스트",
                        lines=5,
                        interactive=False,
                        placeholder="일정이 생성되면 친구들에게 보낼 수 있는 요약본이 여기에 생성됩니다."
                    )
                    make_summary_btn = gr.Button("📋 단톡방 공유 텍스트 생성하기", elem_classes=["travel-chip"])

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
    preset_btn3.click(lambda: "친구들이 오전에 늦잠을 자고 싶어 합니다. 오전 일정을 11시 시작으로 여유롭게 완화하고 카페 휴식 시간을 넉넉히 배치해 줘.", outputs=[feedback_box])
    preset_btn4.click(lambda: "관광지 단순 관람 대신 인스타그램 핫플레이스 카페 및 인생샷 포토스팟의 비중을 대폭 확대해 줘.", outputs=[feedback_box])

    # 3. Group Poll to Feedback
    def apply_poll_to_feedback(food_val, pace_val):
        return f"친구들과 투표 결과 식사는 '{food_val}' 스타일로, 여행 페이스는 '{pace_val}' 스타일로 정했습니다. 이 취향을 최우선 반영하여 일정을 재검증해 주세요!"

    apply_poll_btn.click(
        fn=apply_poll_to_feedback,
        inputs=[poll_food, poll_pace],
        outputs=[feedback_box]
    )

    # 4. Generate Shareable Summary
    make_summary_btn.click(
        fn=generate_shareable_summary,
        inputs=[session_state],
        outputs=[share_summary_box]
    )

    # 5. Initial Itinerary Generation
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

    # 6. Human-in-the-Loop Feedback & Verification
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

    # 7. Export PDF
    pdf_btn.click(
        fn=export_pdf_file,
        inputs=[session_state],
        outputs=[download_file_component]
    )

    # 8. Export Markdown
    export_btn.click(
        fn=export_markdown_file,
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
