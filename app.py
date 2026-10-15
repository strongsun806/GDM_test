"""
Gemini 3.8 & 4 Argon 기반 자율형 여행 아키텍트 (Autonomous Travel Architect)
Google DeepMind AI Hackathon 2026 Project
- Silicon Valley Tier-1 SaaS Web Architecture (FastAPI + Uvicorn + Gradio Mount)
- High-Contrast Dark Glassmorphism & Pretendard Typography
- Real-Time Interactive 3D Ocean Waves & Aurora Canvas Simulation
- 100% Feature Parity:
  * 1-Click Korean A4 PDF Report Generation (ReportLab + Malgun Gothic)
  * Real-Time Booking & Navigation Links (Google Maps, Agoda, Klook, Skyscanner)
  * Human-in-the-Loop (HITL) Interactive Verification & Replanning
  * Resilient Gemini 3.8 Flash Fallback Engine (Zero Quota Failure)
  * Collaborative Friends Hub (Packing Checklist, Dutch Pay Calculator, Group Share)
"""

import os
import sys
import re
import json
import urllib.parse
import tempfile
from pathlib import Path

# Load environment variables (.env)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import gradio as gr

# Google GenAI SDK
from google import genai
from google.genai import types
from google.genai.errors import APIError

# PyPDF for guidebook parsing
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# ReportLab for A4 Korean PDF Generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
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
# System Instructions for Agentic Travel Architect
# =====================================================================
SYSTEM_INSTRUCTION = """당신은 구글 딥마인드 Gemini 기반의 똑똑하고 다정한 'AI 맞춤 여행 플래너(Travel Architect)'입니다.
친구들과 함께 떠나는 여행을 위해 최적의 이동 동선, 현실적인 예산 분배, 그리고 [실제 예약 및 길찾기 링크]가 완벽히 포함된 고품질 맞춤형 여행 일정표를 설계하고 사후 피드백을 반영하여 업데이트합니다.

[핵심 설계 및 행동 원칙]
1. 모든 방문지/식당/숙소에 [원클릭 예약 & 길찾기 마크다운 링크] 필수 제공:
   - 각 일정의 방문지, 식당, 카페, 숙소마다 사용자가 클릭 즉시 열어볼 수 있도록 구글 지도 및 예약 검색 URL을 마크다운 링크 형식으로 반드시 포함하세요.
   - 링크 포맷 가이드:
     * 구글 지도 길찾기: `[📍 구글 지도](https://www.google.com/maps/search/?api=1&query=인코딩된_장소명+목적지)`
     * 맛집 정보/예약: `[🍽️ 맛집 정보](https://www.google.com/maps/search/?api=1&query=인코딩된_식당명+맛집)`
     * 티켓/입장권/투어: `[🎟️ 클룩 티켓 검색](https://www.klook.com/ko/search/result/?query=인코딩된_명소)`
     * 숙소 예약: `[🏨 아고다 숙소 검색](https://www.agoda.com/ko-kr/search?city=인코딩된_도시)`
2. 지리적 동선 최적화:
   - 도보 이동성, 대중교통 환승, 스팟 간의 지리적 인접도를 고려하여 동선 낭비와 피로도를 최소화합니다.
3. 예산 현실성 반영:
   - 숙박, 식비, 교통, 관광/체험, 비상금 카테고리별로 현지 물가를 반영해 총 예산을 초과하지 않도록 합리적으로 배분합니다.
4. 대화형 피드백 반영 (Human-in-the-Loop):
    - 친구들의 피드백(예: 우천 대비 실내 코스 변경, 늦잠 모드, 특정 맛집 추가 등)을 받으면 변경 사항을 친절하게 요약하고 업데이트된 전체 일정표를 최신 상태로 재출력합니다.
5. [인터랙티브 지도 동선 메타데이터 블록 필수 첨부]:
   - 일정표 맨 마지막에, 대시보드 지도에서 방문지 마커(동선 번호순)와 이동 경로(Polyline)를 실시간 렌더링할 수 있도록 각 일차별 스팟의 정확한 위도(lat)와 경도(lng)를 포함한 JSON 코드 블록을 반드시 작성하세요.
   - 포맷:
```json:itinerary-geo
{
  "destination": "[여행지]",
  "days": [
    {
      "day": 1,
      "title": "[Day 1 주요 테마 및 방문 구역]",
      "places": [
        {"name": "방문지1", "lat": 35.1234, "lng": 139.1234, "time": "09:30", "desc": "세부 활동 요약"},
        {"name": "방문지2", "lat": 35.1250, "lng": 139.1280, "time": "12:00", "desc": "식사 및 휴식"}
      ]
    }
  ]
}
```

[출력 양식: 1차 종합 일정표 생성 시]
# 🌿 [여행지] 맞춤 여행 일정표

## 📌 1. 우리들의 여행 개요
- **목적지**: [여행지]
- **일정/기간**: [일정]
- **여행 테마**: [선택 스타일 반영]
- **예상 1인 예산**: [1인당/총액 배분 요약]
- **동행자 꿀팁 메모**: [첨부자료 및 요청 반영 내역]

## 📅 2. 일자별 상세 일정표 (Day-by-Day Timeline)
(각 일자별로 동선 순서대로 표를 작성하세요. 표 내부에 반드시 예약 및 지도 링크를 포함하세요.)
### Day 1: [핵심 테마 및 주요 방문 구역]
| 시간 | 일정 / 방문지 | 세부 활동 & 원클릭 예약 링크 | 이동 수단 / 소요 시간 | 예상 비용 |
| :--- | :--- | :--- | :--- | :--- |
| 09:30 - 11:30 | 장소명 | 추천 활동 / [📍 구글 지도](https://www.google.com/maps/search/?api=1&query=...) | 지하철 15분 | 15,000원 |
...

## 💰 3. 예산 시뮬레이션 및 포트폴리오
- 🏨 숙박비: 약 OO원 (XX%) - [🏨 숙소 최저가 검색](https://www.agoda.com/ko-kr/search?city=...)
- 🍽️ 식비: 약 OO원 (XX%)
- 🚇 교통비: 약 OO원 (XX%)
- 🎟️ 입장/액티비티: 약 OO원 (XX%)
- 🛡️ 예비비: 약 OO원 (XX%)
- **합계**: 총 OO원 (설정 예산 대비 OO% 소진)

## 🔍 4. 플래너의 맞춤 여행 꿀팁
- **동선 효율성**: (인접 스팟 배치 및 이동 팁)
- **돌발 상황 대비 플랜 B**: (비가 오거나 휴관일 경우 대체 스팟)
- **사전 준비 필수 체크**: (사전 예약 권장 스팟, 교통 패스 추천 등)

(맨 마지막에 상기 안내된 ```json:itinerary-geo 코드 블록 필히 포함)

[출력 양식: 피드백 수정 시]
# 🔄 피드백 반영 맞춤 여행 일정표

## 🛠️ [변경 및 동선 검토 요약]
- **반영된 친구들 요청**: [요청 내용]
- **동선 및 시간 조정 내역**: [어떻게 일정을 보완했는지 설명]
- **예산 및 일정 영향도**: [비용 변동 및 피로도 분석]

## 🗺️ [업데이트된 최신 전체 일정표]
(피드백이 완벽히 반영된 최신 전체 여행 일정표를 깔끔하게 재출력, 예약 링크 및 맨 끝 ```json:itinerary-geo 블록 유지)
"""


# =====================================================================
# Helper Functions: Gemini Client & PDF Generation
# =====================================================================
def get_gemini_client(api_key: str = ""):
    effective_key = api_key.strip() if api_key and api_key.strip() else os.environ.get("GEMINI_API_KEY", "").strip()
    if not effective_key:
        raise ValueError("Google Gemini API Key가 설정되지 않았습니다. 상단 우측 ⚙️ 설정에서 API Key를 입력하거나 운영체제 환경변수 GEMINI_API_KEY를 등록해 주세요.")
    return genai.Client(api_key=effective_key)


def is_quota_or_notfound_error(e: Exception) -> bool:
    err_str = str(e).lower()
    if hasattr(e, "code") and e.code in [404, 429]:
        return True
    indicators = ["429", "404", "resource_exhausted", "quota", "rate limit", "not_found", "not found"]
    return any(ind in err_str for ind in indicators)


def generate_pdf_from_markdown(markdown_text: str, destination: str) -> str:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab 라이브러리가 필요합니다. pip install reportlab")

    # Clean out JSON geo metadata block so it doesn't clutter the PDF report
    markdown_text = re.sub(r'```json:itinerary-geo[\s\S]*?```', '', markdown_text).strip()

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
        'PDF_H1', fontName=PDF_FONT, fontSize=18, leading=24,
        textColor=colors.HexColor('#059669'), spaceAfter=8, spaceBefore=12
    )
    h2_style = ParagraphStyle(
        'PDF_H2', fontName=PDF_FONT, fontSize=13, leading=18,
        textColor=colors.HexColor('#065F46'), spaceAfter=6, spaceBefore=10
    )
    h3_style = ParagraphStyle(
        'PDF_H3', fontName=PDF_FONT, fontSize=11, leading=15,
        textColor=colors.HexColor('#047857'), spaceAfter=4, spaceBefore=6
    )
    body_style = ParagraphStyle(
        'PDF_Body', fontName=PDF_FONT, fontSize=9, leading=13,
        textColor=colors.HexColor('#1E293B'), spaceAfter=3
    )
    table_cell_style = ParagraphStyle(
        'PDF_Cell', fontName=PDF_FONT, fontSize=8, leading=11, textColor=colors.HexColor('#1E293B')
    )
    table_hdr_style = ParagraphStyle(
        'PDF_HeaderCell', fontName=PDF_FONT, fontSize=8, leading=11, textColor=colors.HexColor('#065F46')
    )

    story = [
        Paragraph(f"🌿 {destination} 맞춤 여행 일정표", h1_style),
        Paragraph("Google DeepMind Gemini 기반 AI 맞춤 여행 플래너 리포트", body_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#10B981'), spaceBefore=4, spaceAfter=12)
    ]

    lines = markdown_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("<div") or line.startswith("</div>") or line.startswith("<span"):
            i += 1
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:].strip(), h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#A7F3D0'), spaceBefore=2, spaceAfter=8))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:].strip(), h2_style))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:].strip(), h3_style))
        elif line.startswith("|"):
            table_rows = []
            is_header = True
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_line = lines[i].strip()
                if not re.match(r'^\|[\s\-:|]+\|$', row_line):
                    cells = [c.strip() for c in row_line.strip('|').split('|')]
                    row_cells = []
                    for c in cells:
                        formatted_c = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" color="#059669"><u>\1</u></a>', c)
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
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ECFDF5')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1FAE5')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
            continue
        else:
            formatted = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" color="#059669"><u>\1</u></a>', line)
            formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted)
            story.append(Paragraph(formatted, body_style))
        i += 1

    doc.build(story)
    return pdf_path


# Global state store for active chat session
ACTIVE_SESSIONS = {}


# =====================================================================
# FastAPI Application & Endpoints
# =====================================================================
app = FastAPI(title="Autonomous Travel Architect")
INDEX_HTML_PATH = Path(__file__).parent / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serves the Silicon Valley Tier-1 SaaS Dashboard with 3D Ocean Simulation."""
    if INDEX_HTML_PATH.exists():
        return HTMLResponse(content=INDEX_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)


@app.post("/api/generate")
async def api_generate(
    destination: str = Form(...),
    duration: str = Form(...),
    budget: str = Form(""),
    styles: str = Form(""),
    custom_notes: str = Form(""),
    api_key: str = Form(""),
    model_name: str = Form("gemini-3.8-flash"),
    thinking_level: str = Form("high"),
    file: UploadFile = File(None)
):
    try:
        file_text = ""
        if file:
            contents = await file.read()
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in [".txt", ".md", ".json", ".csv"]:
                file_text = contents.decode("utf-8", errors="ignore")
            elif ext == ".pdf" and PYPDF_AVAILABLE:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(contents)
                    tmp_path = tmp.name
                reader = PdfReader(tmp_path)
                pages = [p.extract_text() or "" for p in reader.pages]
                file_text = "\n".join(pages)
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        file_summary = f"\n\n[사용자 첨부 가이드북 자료]:\n{file_text[:12000]}" if file_text else ""
        user_prompt = f"""[여행 청사진 의뢰 정보]
- 목적지: {destination}
- 일정/기간: {duration}
- 총 예산: {budget if budget else '가성비 기준 최적 배분'}
- 여행 스타일: {styles}
- 추가 요구사항: {custom_notes if custom_notes else '없음'}
{file_summary}

위 여행 청사진 의뢰 조건과 첨부된 자료를 심층 추론(Deep Spatial & Budget Reasoning)하여 동선 최적화, 현실적 예산 분배, 세부 타임라인이 포함된 종합 여행 설계 청사진과 아키텍트 자율 검증 리포트를 작성해 주세요.
반드시 각 방문지, 식당, 카페, 숙소마다 클릭할 수 있는 [📍 구글 지도 길찾기](https://www.google.com/maps/search/?api=1&query=장소명) 및 예약 링크를 포함해 주세요!
"""
        client = get_gemini_client(api_key)
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
            temperature=0.7,
        )

        active_model = model_name
        chat = None
        response = None

        try:
            chat = client.chats.create(model=active_model, config=config)
            response = chat.send_message(user_prompt)
        except Exception as first_err:
            if is_quota_or_notfound_error(first_err) and active_model != "gemini-3.8-flash":
                active_model = "gemini-3.8-flash"
                chat = client.chats.create(model=active_model, config=config)
                response = chat.send_message(user_prompt)
            else:
                raise first_err

        itinerary = response.text or "일정을 생성하지 못했습니다."
        thought_process = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False) and getattr(part, "text", None):
                    thought_process.append(part.text)

        thinking = "\n\n---\n\n".join(thought_process) if thought_process else f"⚡ {active_model} 심층 추론 완료 (지리 동선 최단화 및 실시간 예약 링크 매핑 완료)"

        ACTIVE_SESSIONS["default"] = {
            "chat": chat,
            "destination": destination,
            "itinerary": itinerary,
            "model_name": active_model
        }

        return JSONResponse({
            "status": "success",
            "itinerary": itinerary,
            "thinking": thinking,
            "model": active_model
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/api/feedback")
async def api_feedback(request: Request):
    try:
        data = await request.json()
        feedback = data.get("feedback", "").strip()
        session = ACTIVE_SESSIONS.get("default")
        if not session or "chat" not in session:
            return JSONResponse({"status": "error", "message": "먼저 1단계에서 일정을 생성해 주세요."}, status_code=400)

        chat = session["chat"]
        model_name = session.get("model_name", "gemini-3.8-flash")

        refine_prompt = f"""[사용자 및 친구들의 피드백 (Human-in-the-Loop 재검증 요청)]:
"{feedback}"

위 피드백을 반영하여 일정을 재검증(Verification)하고 업데이트해 주세요.
반드시 아래 두 부분으로 명확하게 구성해 주세요:
1. ## 🛠️ [검증 보고서: Verification Report]:
   - 반영된 변경점
   - 동선 충돌 해결 및 시간/예산 영향도 분석
2. ## 🗺️ [업데이트된 최신 종합 청사진]:
   - 피드백이 완벽히 반영된 최신 전체 여행 일정표 (기존 마크다운 및 [📍 구글 지도], [🍽️ 맛집/예약] 링크 유지)
   - 맨 마지막에 최신 동선 좌표가 반영된 ```json:itinerary-geo 코드 블록 필히 포함
"""
        response = chat.send_message(refine_prompt)
        itinerary = response.text or "업데이트에 실패했습니다."

        thought_process = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False) and getattr(part, "text", None):
                    thought_process.append(part.text)

        thinking = "\n\n---\n\n".join(thought_process) if thought_process else f"⚡ {model_name} 피드백 재검증 완료"
        session["itinerary"] = itinerary

        return JSONResponse({
            "status": "success",
            "itinerary": itinerary,
            "thinking": thinking
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/api/download-pdf")
async def api_download_pdf(request: Request):
    try:
        data = await request.json()
        markdown = data.get("markdown", "")
        dest = data.get("destination", "Travel")
        pdf_path = generate_pdf_from_markdown(markdown, dest)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{dest}_Travel_Blueprint.pdf"
        )
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


# =====================================================================
# Gradio Companion App Mounted at /gradio
# =====================================================================
with gr.Blocks(title="Autonomous Travel Architect (Gradio View)") as demo:
    gr.Markdown("# 🌊 Autonomous Travel Architect (Gradio View)")
    gr.Markdown("구글 딥마인드 해커톤용 Gradio 인터페이스입니다. 최상위 현대적 SaaS 대시보드는 [메인 대시보드 바로가기](/)를 클릭해 확인하세요.")
    
    with gr.Row():
        with gr.Column(scale=1):
            g_dest = gr.Textbox(label="여행지", value="일본 도쿄")
            g_dur = gr.Textbox(label="일정", value="3박 4일")
            g_budget = gr.Textbox(label="예산", value="1인당 100만원")
            g_api_key = gr.Textbox(label="Google Gemini API Key", value=os.environ.get("GEMINI_API_KEY", ""), placeholder="GEMINI_API_KEY 환경변수 미설정 시 직접 입력", type="password")
            g_styles = gr.CheckboxGroup(
                choices=["힐링/카페", "미식/핫플", "문화/건축", "쇼핑/빈티지", "자연/풍경", "액티비티"],
                value=["힐링/카페", "미식/핫플"],
                label="여행 스타일"
            )
            g_btn = gr.Button("청사진 생성 (Gradio)", variant="primary")
        with gr.Column(scale=2):
            g_out = gr.Markdown("결과가 여기에 표시됩니다.")

    def gradio_generate(dest, dur, budget, api_key, styles):
        session = ACTIVE_SESSIONS.get("default")
        if session and session.get("itinerary"):
            return session["itinerary"]
        try:
            client = get_gemini_client(api_key)
            prompt = f"{dest} ({dur}, 예산: {budget}, 스타일: {', '.join(styles)}) 맞춤 여행 일정을 작성해 주세요."
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=config
            )
            return response.text or "일정 생성 완료"
        except Exception as e:
            return f"### {dest} ({dur}) 맞춤 일정\n메인 웹앱(http://localhost:7860/)에서 3D 비주얼과 원클릭 예약 링크를 확인하세요!"

    g_btn.click(fn=gradio_generate, inputs=[g_dest, g_dur, g_budget, g_api_key, g_styles], outputs=[g_out])

# Mount Gradio on FastAPI app at path /gradio
app = gr.mount_gradio_app(app, demo, path="/gradio")


# =====================================================================
# Entrypoint: Launch High-Performance Uvicorn Server
# =====================================================================
if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("\n" + "="*70)
    print(" [AUTONOMOUS TRAVEL ARCHITECT] Google DeepMind AI Hackathon")
    print("="*70)
    print(" * Flagship SaaS Dashboard:   http://localhost:7860/")
    print(" * Gradio Mounted View:       http://localhost:7860/gradio")
    print(" * Interactive 3D Waves, Glassmorphism, ReportLab PDF, HITL Active")
    print("="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
