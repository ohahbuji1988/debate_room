import streamlit as st
import os
import time
import json
import re
import datetime
from dotenv import load_dotenv

# ----------------------------------------------------
# 1. 환경 설정 & 세션 상태
# ----------------------------------------------------
load_dotenv()
ENV_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
ENV_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="Debate Room Pro | Executive Decision Simulator",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Apple 미학 CSS & 우측 완벽 고정 플로팅 타이머
# ----------------------------------------------------
st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css");

    html, body, p, div, span, label, input, textarea, button, h1, h2, h3, h4 {
        font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "SF Pro Text", "Apple SD Gothic Neo", sans-serif !important;
        letter-spacing: -0.025em;
    }

    /* Streamlit 아이콘 폰트 보호 */
    [data-testid="stIconMaterial"], 
    [class*="material-symbols"], 
    [class*="material-icons"], 
    .material-symbols-rounded, 
    .material-icons-outlined,
    [data-testid="stSidebarCollapseButton"] span {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

    .stApp {
        background-color: #000000 !important;
        color: #f5f5f7 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #121214 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* 상단 슬림 헤더 */
    .apple-mini-header {
        background: rgba(22, 22, 24, 0.8);
        backdrop-filter: blur(25px) saturate(180%);
        -webkit-backdrop-filter: blur(25px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 9999px;
        padding: 8px 20px;
        margin: -15px auto 14px auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 98%;
    }
    .apple-header-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f5f5f7;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 우측 고정 플로팅 타이머 패널 (스크롤을 내려도 항상 화면 우측 상단에 고정) */
    div[data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }
    div[data-testid="stColumn"]:nth-of-type(2),
    div[data-testid="column"]:nth-of-type(2),
    .stColumn:nth-of-type(2) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 20px !important;
        align-self: flex-start !important;
        height: fit-content !important;
        z-index: 999 !important;
    }
    div[data-testid="stColumn"]:nth-of-type(2) > div,
    div[data-testid="column"]:nth-of-type(2) > div {
        position: sticky !important;
        top: 20px !important;
    }

    /* 애플워치 스타일 데스크 클락 모듈 */
    .apple-watch-face {
        background: radial-gradient(circle at top, #1e1e22 0%, #101012 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 12px 14px 10px 14px;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255, 255, 255, 0.15);
        max-width: 190px;
        margin: 0 auto;
    }
    .apple-watch-time {
        font-size: 1.75rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        color: #ffffff;
        letter-spacing: -1px;
        margin: 2px 0;
        text-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
    }
    .apple-watch-status {
        font-size: 0.68rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 6px;
    }

    /* 우측 시계 영역 전용 슬림 버튼 & 인풋 */
    div[data-testid="stColumn"]:nth-of-type(2) div.stButton > button,
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        padding: 4px 10px !important;
        font-size: 0.78rem !important;
        height: 30px !important;
        min-height: 30px !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        margin-top: 3px !important;
    }
    div[data-testid="stColumn"]:nth-of-type(2) .stNumberInput > div > div > input,
    div[data-testid="column"]:nth-of-type(2) .stNumberInput > div > div > input {
        height: 28px !important;
        min-height: 28px !important;
        font-size: 0.8rem !important;
        padding: 2px 8px !important;
        text-align: center !important;
        border-radius: 10px !important;
        background-color: #141416 !important;
    }
    div[data-testid="stColumn"]:nth-of-type(2) .stNumberInput label,
    div[data-testid="column"]:nth-of-type(2) .stNumberInput label {
        font-size: 0.72rem !important;
        color: #86868b !important;
        margin-bottom: 2px !important;
    }

    /* iMessage 스타일 발언 버블 */
    .apple-bubble-incoming {
        background-color: #1c1c1e;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px 18px 18px 6px;
        padding: 14px 18px;
        margin-bottom: 10px;
        max-width: 92%;
    }
    .apple-bubble-outgoing {
        background: linear-gradient(135deg, #0071e3 0%, #0056b3 100%);
        border-radius: 18px 18px 6px 18px;
        padding: 14px 20px;
        margin-bottom: 12px;
        max-width: 92%;
        margin-left: auto;
        color: #ffffff;
        box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
    }

    .apple-tag {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 600;
    }

    /* CEO 임원 보고용 벤토 카드 */
    .executive-card {
        background: #141416;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }

    /* 좌측 메인 입력 필드 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #18181a !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        color: #f5f5f7 !important;
        font-size: 0.92rem !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2997ff !important;
        box-shadow: 0 0 0 2px rgba(41, 151, 255, 0.25) !important;
    }

    /* 좌측 액션 버튼들 */
    div[data-testid="stColumn"]:nth-of-type(1) div.stButton > button,
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background: #1c1c1e !important;
        color: #f5f5f7 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        padding: 7px 16px !important;
        font-size: 0.84rem !important;
        transition: all 0.2s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. 부서 페르소나 (실무 전문 용어 자연스러운 반영)
# ----------------------------------------------------
DEFAULT_DEPARTMENTS = {
    "💼 설비구매": {
        "accent": "#2997ff", "bg": "rgba(41, 151, 255, 0.15)",
        "role": "TCO 절감, 납기 Delay에 따른 LD(지체상금) 조항 검토, 단독 벤더 리스크 관리, SLA 및 Spares 단가 협상, 추가 항공 운임(Air Freight) 벤더 부담 관철."
    },
    "🏭 생산": {
        "accent": "#ff9f0a", "bg": "rgba(255, 159, 10, 0.15)",
        "role": "상업용 Batch 생산 마일스톤 준수, 조작 직관성(OEE), 가동 중단에 따른 Batch 폐기 리스크 방어, 세척 및 CIP/SIP 용이성 확보."
    },
    "🧬 MSAT": {
        "accent": "#bf5af2", "bg": "rgba(191, 90, 242, 0.15)",
        "role": "공정 동등성(Process Comparability), CQA 유지, 스케일업 파라미터 일치, 소모품 및 Single-use 부품 호환성 검증."
    },
    "🛡️ QA": {
        "accent": "#ff453a", "bg": "rgba(255, 69, 58, 0.15)",
        "role": "cGMP 및 Data Integrity(21 CFR Part 11) 규정 준수, Change Control(변경관리) 승인 절차, 현지 FAT 생략 불가 원칙, IQ/OQ/PQ 밸리데이션 적격성 사수."
    },
    "⚙️ 엔지니어링": {
        "accent": "#30d158", "bg": "rgba(48, 209, 88, 0.15)",
        "role": "Clean/Black Utility(WFI, Clean Steam 등) 공급 용량 검토, Hook-up 공기 단축, 예방정비(PM) 동선 확보, 비상 인터락 안전성."
    },
    "🏗️ 건설": {
        "accent": "#98989d", "bg": "rgba(152, 152, 157, 0.15)",
        "role": "클린룸 패널 간섭 방지, 설비 반입 Rigging Path 확보, 바닥 슬래브 하중 검토, MC(기계 완공) 마일스톤과 설비 인입 일정 정합성."
    },
    "🎯 프로젝트 PM": {
        "accent": "#5e5ce6", "bg": "rgba(94, 92, 230, 0.15)",
        "role": "RFE(Ready for Equipment) 마일스톤, Critical Path 공정 사수, 라인 가동 지연에 따른 고객사 페널티 리스크 방어."
    },
    "💰 재경": {
        "accent": "#64d2ff", "bg": "rgba(100, 210, 255, 0.15)",
        "role": "당해 연도 CAPEX 집행률 관리, 예산 Overrun 방지, 대금 지급(Cash-out) 마일스톤 분산, 관세 감면 최적화."
    },
    "⚖️ 감사": {
        "accent": "#ff375f", "bg": "rgba(255, 55, 95, 0.15)",
        "role": "업체 선정의 공정성, 단독 수의계약 타당성 사유서 검증, 내부 구매 규정 준수, 향후 정기 감사 지적 리스크 사전 차단."
    }
}

if "departments" not in st.session_state:
    st.session_state.departments = DEFAULT_DEPARTMENTS.copy()

if "debate_history" not in st.session_state:
    st.session_state.debate_history = []

if "ai_suggestion" not in st.session_state:
    st.session_state.ai_suggestion = None

if "debate_status" not in st.session_state:
    st.session_state.debate_status = "idle"

if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0

if "session_duration_min" not in st.session_state:
    st.session_state.session_duration_min = 3

if "summary_analysis" not in st.session_state:
    st.session_state.summary_analysis = None

# ----------------------------------------------------
# 4. 실시간 가용 모델 자동 검증 엔진
# ----------------------------------------------------
@st.cache_data(ttl=600)
def get_verified_groq_models(key):
    if not key or key.startswith("gsk_여기에"):
        return ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    try:
        from groq import Groq
        client = Groq(api_key=key)
        all_ids = [m.id for m in client.models.list().data if not any(x in m.id.lower() for x in ["whisper", "embed", "tts", "orpheus", "guard", "vision"])]
        verified = []
        preferred = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b", "meta-llama/llama-4-scout-17b-16e-instruct", "llama-3.1-8b-instant"]
        candidate_list = [p for p in preferred if p in all_ids] + [m for m in all_ids if m not in preferred]
        for cand in candidate_list[:4]:
            try:
                _ = client.chat.completions.create(model=cand, messages=[{"role": "user", "content": "hi"}], max_tokens=2)
                verified.append(cand)
            except Exception:
                continue
        return verified if verified else ["openai/gpt-oss-120b"]
    except Exception:
        return ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]

@st.cache_data(ttl=600)
def get_verified_gemini_models(key):
    if not key or key.startswith("AIzaSy_기존"):
        return ["gemini-2.5-flash", "gemini-2.0-flash"]
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        models = [m.name.replace("models/", "") for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        verified = []
        pref = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        cand_list = [p for p in pref if p in models] + [m for m in models if m not in pref]
        for cand in cand_list[:3]:
            try:
                gm = genai.GenerativeModel(cand)
                _ = gm.generate_content("hi")
                verified.append(cand)
            except Exception:
                continue
        return verified if verified else ["gemini-2.5-flash"]
    except Exception:
        return ["gemini-2.5-flash", "gemini-2.0-flash"]

def safe_parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    clean = re.sub(r'```(?:json)?\s*', '', text)
    clean = re.sub(r'```\s*', '', clean).strip()
    try:
        return json.loads(clean)
    except Exception:
        return {}

# ----------------------------------------------------
# 5. 사이드바 (설정 패널)
# ----------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 16px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #f5f5f7; display: flex; align-items: center; gap: 8px;">
            <span style="color: #2997ff; font-size: 1.2rem;">⌘</span> Debate Room Pro
        </div>
        <div style="font-size: 0.75rem; color: #86868b; margin-top: 2px;">
            Cross-Functional Decision Simulator
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #86868b; margin-bottom: 6px;'>AI Engine</p>", unsafe_allow_html=True)
    engine_choice = st.radio(
        "엔진 선택",
        ["Groq (초고속 / 완전무료 권장)", "Google Gemini"],
        label_visibility="collapsed",
        index=0
    )
    
    if "Groq" in engine_choice:
        selected_engine = "groq"
        api_key = st.text_input("Groq API Key", value=ENV_GROQ_KEY, type="password", placeholder="gsk_...")
        if api_key:
            model_options = get_verified_groq_models(api_key)
            model_name = st.selectbox("가용 검증 모델", model_options, index=0)
            st.caption(f"🟢 검증 완료: `{model_name}`")
        else:
            model_name = "openai/gpt-oss-120b"
            st.warning("Groq API 키를 입력하세요.")
    else:
        selected_engine = "gemini"
        api_key = st.text_input("Gemini API Key", value=ENV_GEMINI_KEY, type="password", placeholder="AIzaSy...")
        if api_key:
            gemini_models = get_verified_gemini_models(api_key)
            model_name = st.selectbox("가용 검증 모델", gemini_models, index=0)
            st.caption(f"🟢 검증 완료: `{model_name}`")
        else:
            model_name = "gemini-2.5-flash"
            st.warning("Gemini API 키를 입력하세요.")

    st.divider()

    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #86868b; margin-bottom: 6px;'>참석 부서 (Stakeholders)</p>", unsafe_allow_html=True)
    all_dept_names = list(st.session_state.departments.keys())
    default_selected = [d for d in ["💼 설비구매", "🏭 생산", "🛡️ QA", "⚙️ 엔지니어링", "🎯 프로젝트 PM"] if d in all_dept_names]
    
    selected_depts = st.multiselect(
        "참석 부서 선택",
        options=all_dept_names,
        default=default_selected,
        label_visibility="collapsed"
    )
    
    with st.expander("+ 부서 추가"):
        with st.form("add_dept_form", clear_on_submit=True):
            new_dept_name = st.text_input("부서명", placeholder="예: 🌿 EHS (환경안전)")
            new_dept_role = st.text_area("핵심 KPI / 주요 이슈", placeholder="예: 고압가스 안전 인증, 노동부 규정...")
            if st.form_submit_button("등록"):
                if new_dept_name and new_dept_name not in st.session_state.departments:
                    st.session_state.departments[new_dept_name] = {
                        "accent": "#64d2ff", "bg": "rgba(100, 210, 255, 0.15)",
                        "role": new_dept_role if new_dept_role else "규정 준수"
                    }
                    st.success(f"'{new_dept_name}' 추가 완료")
                    st.rerun()

    st.divider()
    if st.button("세션 초기화 (New Session)", use_container_width=True):
        st.session_state.debate_history = []
        st.session_state.ai_suggestion = None
        st.session_state.debate_status = "idle"
        st.session_state.remaining_seconds = 0
        st.session_state.summary_analysis = None
        if "generated_report" in st.session_state:
            del st.session_state["generated_report"]
        st.cache_data.clear()
        st.rerun()

# ----------------------------------------------------
# 6. 상단 슬림 미니멀 헤더
# ----------------------------------------------------
mins_left, secs_left = divmod(int(st.session_state.remaining_seconds), 60)
if st.session_state.debate_status == "running":
    status_str = f"Live · {mins_left:02d}:{secs_left:02d}"
    status_bg = "rgba(48, 209, 88, 0.15)"
    status_text_color = "#30d158"
elif st.session_state.debate_status == "paused":
    status_str = f"Paused · {mins_left:02d}:{secs_left:02d}"
    status_bg = "rgba(255, 159, 10, 0.15)"
    status_text_color = "#ff9f0a"
elif st.session_state.debate_status == "completed":
    status_str = "Session Finished"
    status_bg = "rgba(41, 151, 255, 0.15)"
    status_text_color = "#2997ff"
else:
    status_str = "Ready"
    status_bg = "rgba(255, 255, 255, 0.08)"
    status_text_color = "#86868b"

st.markdown(f"""
<div class="apple-mini-header">
    <div class="apple-header-title">
        <span style="color: #2997ff;">⌘</span>
        <span>Debate Room Pro</span>
        <span style="font-size: 0.78rem; color: #86868b; font-weight: 500;">| Executive Decision Support</span>
    </div>
    <div style="font-size: 0.75rem; color: #86868b; display: flex; align-items: center; gap: 8px;">
        <span style="color: {status_text_color}; font-weight: 600;">● {status_str}</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 9999px;">{model_name}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 7. LLM 호출 엔진 (자연스러운 한국어 + 실무 영어 혼용 프롬프트)
# ----------------------------------------------------
def execute_llm_json(engine, key, model, sys_p, usr_p):
    if engine == "groq":
        from groq import Groq
        c = Groq(api_key=key)
        res = c.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_p + "\n반드시 순수한 JSON 포맷으로만 회신하십시오."},
                {"role": "user", "content": usr_p}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return safe_parse_json(res.choices[0].message.content)
    else:
        import google.generativeai as genai
        genai.configure(api_key=key)
        gm = genai.GenerativeModel(model)
        res = gm.generate_content(f"{sys_p}\n\n{usr_p}", generation_config={"response_mime_type": "application/json"})
        return safe_parse_json(res.text)

def stream_next_turn(engine, key, model, scenario, selected_depts, history, stream_container, turn_number):
    if not selected_depts:
        selected_depts = ["💼 설비구매", "🏭 생산", "🛡️ QA", "⚙️ 엔지니어링", "🎯 프로젝트 PM"]

    dept_contexts = [f"- [{d}]: {st.session_state.departments.get(d, {}).get('role', '')}" for d in selected_depts]
    dept_context_str = "\n".join(dept_contexts)
    recent_dialogue = "\n".join([f"Turn {m.get('turn_num', idx+1)} [{m['speaker']}]: {m['content']}" for idx, m in enumerate(history[-6:])])

    system_prompt = f"""
당신은 대기업 설비구매 및 생산/엔지니어링 다부서 사전 협의체를 시뮬레이션하는 시스템입니다.
참석 부서:
{dept_context_str}

안건 (Agenda):
{scenario}

최근 회의 내용:
{recent_dialogue if recent_dialogue else "(회의 시작)"}

언어 및 톤 가이드:
- 억지로 모든 영어를 한글로 번역하지 마십시오. 실제 사내 회의에서 쓰이듯 한국어를 바탕으로 하되, 실무 전문 용어(Lead Time, Delay, LD 조항, cGMP, Validation, FAT/SAT, Change Control, Buffer, TCO, SLA, Critical Path, Hook-up, Batch 등)는 자연스럽게 영어/약어로 섞어서 발언하십시오.
- 직전 발언자의 주장에 대해 가장 민감한 부서가 정면 반박하거나 실무적인 대안을 제시해야 합니다.
- 조율자(👑 Orchestrator)의 지침이 있었다면, 그 가이드라인을 최우선으로 수용하여 타협안을 제시하십시오.
- 2~3문장 내외로 군더더기 없이 직설적이고 날카롭게 발언하십시오.
- 부서명은 반드시 목록에 명시된 이름(이모티콘 포함) 그대로 출력하십시오.
- 첫 줄은 메타데이터, 둘째 줄부터 본문을 작성하십시오:
형식:
[부서명]|반응(정면반박/조건부수용/대안제시/추가우려)|대상부서
발언 본문...
"""
    user_prompt = "다음 회의 발언을 생성하십시오."
    full_output = ""

    if engine == "groq":
        from groq import Groq
        c = Groq(api_key=key)
        response = c.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            stream=True,
            temperature=0.7
        )
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
                if delta:
                    full_output += delta
                    stream_container.markdown(f"""
                    <div class="apple-bubble-incoming" style="border-left: 3px solid #2997ff;">
                        <span class="apple-tag" style="background: rgba(41, 151, 255, 0.2); color: #2997ff;">
                            Turn #{turn_number} · Live Streaming
                        </span>
                        <div style="font-size: 0.94rem; line-height: 1.65; color: #f5f5f7; margin-top: 6px;">{full_output}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.008)
    else:
        import google.generativeai as genai
        genai.configure(api_key=key)
        gm = genai.GenerativeModel(model)
        response = gm.generate_content(f"{system_prompt}\n\n{user_prompt}", stream=True)
        for chunk in response:
            if chunk.text:
                full_output += chunk.text
                stream_container.markdown(f"""
                <div class="apple-bubble-incoming" style="border-left: 3px solid #2997ff;">
                    <span class="apple-tag" style="background: rgba(41, 151, 255, 0.2); color: #2997ff;">
                        Turn #{turn_number} · Live Streaming
                    </span>
                    <div style="font-size: 0.94rem; line-height: 1.65; color: #f5f5f7; margin-top: 6px;">{full_output}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.015)

    lines = full_output.strip().split("\n")
    first_line = lines[0]
    speech_body = "\n".join(lines[1:]).strip() if len(lines) > 1 else full_output

    speaker = selected_depts[0]
    reaction = "발언"
    target = "전체"

    if "|" in first_line:
        parts = first_line.replace("[", "").replace("]", "").split("|")
        raw_spk = parts[0].strip()
        matched = next((d for d in st.session_state.departments.keys() if raw_spk in d or d in raw_spk), raw_spk)
        speaker = matched
        if len(parts) >= 2:
            reaction = parts[1].strip()
        if len(parts) >= 3:
            target = parts[2].strip()

    return {
        "turn_num": turn_number,
        "speaker": speaker,
        "reaction_type": reaction,
        "target_speaker": target,
        "content": speech_body if speech_body else full_output
    }

# ----------------------------------------------------
# 8. 메인 뷰: 좌측(작업창) & 우측(완벽 고정 플로팅 타이머)
# ----------------------------------------------------
col_main, col_watch = st.columns([3.6, 1.05])

# ====================================================
# [우측 패널] 스크롤을 내려도 항상 화면 우측에 고정되는 미니 클락 위젯
# ====================================================
with col_watch:
    st.markdown(f"""
    <div class="apple-watch-face">
        <div style="font-size: 0.65rem; font-weight: 700; color: #86868b; letter-spacing: 0.08em; text-transform: uppercase;">SESSION CLOCK</div>
        <div class="apple-watch-time">{mins_left:02d}:{secs_left:02d}</div>
        <div class="apple-watch-status" style="background: {status_bg}; color: {status_text_color};">
            ● {status_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 원하는 시간을 직접 입력(input)하거나 위아래 화살표로 스크롤 조절하는 미니 인풋
    user_min_input = st.number_input(
        "⏱️ 시간 설정 (분)",
        min_value=1,
        max_value=60,
        value=st.session_state.session_duration_min,
        step=1,
        help="직접 숫자를 입력하거나 화살표를 눌러 분을 설정하세요."
    )
    if user_min_input != st.session_state.session_duration_min:
        st.session_state.session_duration_min = int(user_min_input)

    # 2. 슬림 마이크로 제어 버튼 (높이 30px)
    if st.session_state.debate_status != "running":
        if st.button("▶ 토론 시작", use_container_width=True):
            if not api_key:
                st.error("API 키를 확인하세요.")
            elif not st.session_state.get("current_scenario", "").strip():
                st.warning("안건을 입력하세요.")
            else:
                st.session_state.remaining_seconds = st.session_state.session_duration_min * 60
                st.session_state.debate_status = "running"
                st.session_state.summary_analysis = None
                st.rerun()

    if st.session_state.debate_status == "running":
        if st.button("❚❚ 일시정지 (Pause)", use_container_width=True):
            st.session_state.debate_status = "paused"
            st.rerun()
    elif st.session_state.debate_status == "paused":
        if st.button(f"▶ 재개 ({mins_left:02d}:{secs_left:02d})", use_container_width=True):
            st.session_state.debate_status = "running"
            st.rerun()

    if st.session_state.debate_status in ["running", "paused"]:
        if st.button("■ 종료 & 요약", use_container_width=True):
            st.session_state.remaining_seconds = 0
            st.session_state.debate_status = "completed"
            with st.spinner("Executive Briefing 생성 중..."):
                p_sys = """당신은 CEO 및 경영진 직속 수석 의사결정 보좌관입니다. 
토론 내용을 바탕으로 바쁜 임원이 30초 안에 결재할 수 있도록 가장 간결하고 함축적인 JSON 브리핑을 작성하십시오.
한국어를 뼈대로 하되, Lead Time, LD 조항, FAT/SAT, Change Control, Buffer 등 실무 전문 용어는 자연스럽게 혼용하십시오."""
                p_usr = f"""Agenda: {st.session_state.get('current_scenario', '')}
Transcript: {json.dumps(st.session_state.debate_history, ensure_ascii=False)}

반드시 아래 간결한 포맷으로 작성하십시오:
{{
    "bottom_line": "CEO 핵심 의사결정 권고 1~2문장 (예: 벤더 항공료 전액 부담 및 보증 6개월 연장 조건부 수용, 입고 SAT에 필수 인터락 집중 검증 추진)",
    "top_3_risks": [
        "일정 Risk: 8주 Lead Time 지연 시 4분기 상업 Batch 차질 (대책: Air Freight 전환으로 4주 만회)",
        "규제/품질 Risk: 현지 FAT 서면 대체 시 cGMP 검증 결격 (대책: 입고 SAT 프로토콜에 인터락 테스트 이관)",
        "비용 Risk: 벤더 귀책에 따른 LD 조항 미적용 우려 (대책: 운임 전액 부담 확약서 징구)"
    ],
    "alignment_matrix": [
        {{"dept": "생산", "issue": "상업 Batch 일정 2주 이상 지연 불가", "resolution": "유틸리티 Hook-up 야간 돌관 작업으로 10일 만회"}},
        {{"dept": "QA", "issue": "FAT 서면 대체 불가 (규정 위반)", "resolution": "입고 SAT 시 핵심 인터락 현장 입회 검증 강화"}},
        {{"dept": "구매", "issue": "단독 벤더 귀책에 따른 비용 보전", "resolution": "Air Freight 100% 벤더 부담 및 계약 특약 반영"}}
    ],
    "next_actions": [
        {{"action": "벤더 변경 합의서(항공료 부담/보증기간 연장) 체결", "owner": "설비구매", "due": "D+2"}},
        {{"action": "SAT 보강 프로토콜 Change Control(CC) 상정", "owner": "QA/생산", "due": "D+5"}}
    ]
}}"""
                st.session_state.summary_analysis = execute_llm_json(selected_engine, api_key, model_name, p_sys, p_usr)
            st.rerun()

# ====================================================
# [좌측 메인 영역] 안건 -> 타임라인 -> [하단 임원 보고용 요약]
# ====================================================
with col_main:
    # 1. 안건 설정 (Agenda)
    st.markdown("<div style='font-size: 0.96rem; font-weight: 700; color: #f5f5f7; margin-bottom: 6px;'>회의 안건 및 현안 상황 (Agenda)</div>", unsafe_allow_html=True)

    scenario = st.text_area(
        "회의 안건",
        value=st.session_state.get("current_scenario", ""),
        placeholder="논의할 현안을 간략히 메모하세요. (예: 핵심 배양기 유럽 벤더 센서 수급난으로 Lead Time 8주 지연 통보. 4분기 상업 생산 Batch 일정 변경 불가. 벤더가 Air Freight 전액 부담 제안.)",
        height=75,
        label_visibility="collapsed"
    )
    st.session_state.current_scenario = scenario

    col_a1, col_a2, col_a3 = st.columns([1.3, 1, 1])
    with col_a1:
        if st.button("✨ AI 안건 정제 및 추천", use_container_width=True):
            if not api_key:
                st.error("API 키를 확인하세요.")
            elif not scenario.strip():
                st.warning("안건 메모를 입력하세요.")
            else:
                with st.spinner("전문 비즈니스 안건으로 정제 중..."):
                    try:
                        p_sys = "당신은 최고 전략 기획관입니다. 메모를 분석하여 실무 용어가 자연스럽게 섞인 전문 안건과 추천 키워드를 담은 JSON을 작성하십시오."
                        p_usr = f"""메모: {scenario}
{{
    "refined_scenario": "전문 실무 용어가 반영된 명확한 공식 안건 2문장",
    "recommended_keywords": ["LD 조항", "Change Control", "FAT/SAT 프로토콜", "Air Freight"]
}}"""
                        st.session_state.ai_suggestion = execute_llm_json(selected_engine, api_key, model_name, p_sys, p_usr)
                    except Exception as e:
                        st.error(f"정제 중 오류: {e}")

    with col_a2:
        if st.button("프리셋: 센서 납기 8주 지연", use_container_width=True):
            st.session_state.current_scenario = "5공장 핵심 배양기 유럽 벤더가 센서 수급난으로 납기 8주 지연 통보. 4분기 상업 생산 마일스톤 고정 및 지연 위약금 리스크 존재."
            st.session_state.ai_suggestion = None
            st.rerun()

    with col_a3:
        if st.button("프리셋: FAT 서면 대체 건", use_container_width=True):
            st.session_state.current_scenario = "정제 크로마토그래피 설비 벤더가 공기 단축을 이유로 현지 FAT 입회를 생략하고 서면 데이터 제출 및 도착 후 SAT 일괄 진행을 요구함."
            st.session_state.ai_suggestion = None
            st.rerun()

    if st.session_state.ai_suggestion:
        sug = st.session_state.ai_suggestion
        st.markdown(f"""
        <div style="background: rgba(41, 151, 255, 0.08); border: 1px solid rgba(41, 151, 255, 0.25); border-radius: 14px; padding: 14px 18px; margin-top: 10px;">
            <div style="font-weight: 700; color: #2997ff; margin-bottom: 4px; font-size: 0.84rem;">💡 정제된 비즈니스 안건 (Refined Agenda):</div>
            <div style="font-size: 0.92rem; color: #f5f5f7; line-height: 1.6; margin-bottom: 6px;">
                {sug.get('refined_scenario')}
            </div>
            <div style="font-size: 0.8rem; color: #86868b;">
                <b>Key Keywords:</b> {", ".join([f"<span style='color:#2997ff;'>#{k}</span>" for k in sug.get('recommended_keywords', [])])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 위 정제 안건을 본문에 적용"):
            st.session_state.current_scenario = sug.get('refined_scenario')
            st.session_state.ai_suggestion = None
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. 회의 타임라인 (Timeline)
    st.markdown("<div style='font-size: 1.05rem; font-weight: 700; color: #f5f5f7; margin-bottom: 10px;'>Discussion Transcript (실시간 회의록)</div>", unsafe_allow_html=True)

    if not st.session_state.debate_history:
        st.markdown("""
        <div style="background: #141416; border: 1px dashed rgba(255,255,255,0.12); border-radius: 16px; padding: 24px; text-align: center; color: #86868b; font-size: 0.88rem;">
            우측 플로팅 시계의 <b>'▶ 토론 시작'</b>을 누르면 유관부서들의 실시간 핑퐁 토론이 진행됩니다.
        </div>
        """, unsafe_allow_html=True)

    for item in st.session_state.debate_history:
        t_num = item.get("turn_num", 1)
        spk = item["speaker"]
        
        if "Orchestrator" in spk or "조율자" in spk:
            st.markdown(f"""
            <div class="apple-bubble-outgoing">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: 700; font-size: 0.84rem; color: #ffffff;">👑 Orchestrator Guidance (조율자 지침)</span>
                    <span style="font-size: 0.72rem; opacity: 0.8;">Turn #{t_num}</span>
                </div>
                <div style="font-size: 0.94rem; line-height: 1.65;">"{item['content']}"</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            dept_meta = st.session_state.departments.get(spk, {"accent": "#86868b", "bg": "rgba(255,255,255,0.08)"})
            reaction = item.get("reaction_type", "발언")
            target = item.get("target_speaker", "전체")
            target_str = f" ➔ vs {target}" if target != "전체" else ""
            
            st.markdown(f"""
            <div class="apple-bubble-incoming" style="border-left: 3px solid {dept_meta['accent']};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div>
                        <span class="apple-tag" style="background: {dept_meta['bg']}; color: {dept_meta['accent']};">
                            {spk}
                        </span>
                        <span style="font-size: 0.76rem; color: #86868b; margin-left: 6px;">{reaction}{target_str}</span>
                    </div>
                    <span style="font-size: 0.72rem; color: #86868b;">Turn #{t_num}</span>
                </div>
                <div style="font-size: 0.94rem; line-height: 1.65; color: #f5f5f7; margin-top: 4px;">
                    {item['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    stream_slot = st.empty()

    # 3. 조율자 개입 바 (Orchestrator Intervention)
    st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #f5f5f7; margin-top: 14px; margin-bottom: 6px;'>👑 Orchestrator Intervention (가이드라인 및 정보 공유)</div>", unsafe_allow_html=True)
    col_in1, col_in2 = st.columns([4, 1])

    with col_in1:
        orchestrator_input = st.text_input(
            "Orchestrator 코멘트",
            placeholder="부서에 전달할 가이드라인이나 팩트를 입력하세요. (예: 납기 4주는 Buffer가 있으니 QA 요구대로 SAT 보강을 전제로 Air Freight 안을 채택합시다.)",
            label_visibility="collapsed"
        )

    with col_in2:
        if st.button("가이드라인 반영", use_container_width=True):
            if not api_key or not orchestrator_input:
                st.warning("내용을 입력하세요.")
            else:
                next_turn_idx = len(st.session_state.debate_history) + 1
                st.session_state.debate_history.append({
                    "turn_num": next_turn_idx,
                    "speaker": "👑 Orchestrator",
                    "content": orchestrator_input
                })
                st.success("가이드라인 반영 완료")
                st.rerun()

    # ====================================================
    # 4. [페이지 하단] CEO/임원 보고용 초압축 브리핑 (Executive Summary)
    # ====================================================
    if st.session_state.debate_status == "completed" and st.session_state.summary_analysis:
        an = st.session_state.summary_analysis
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #f5f5f7;">📋 Executive Summary (경영진 의사결정 브리핑)</div>
            <span style="font-size:0.75rem; color:#86868b; background:rgba(255,255,255,0.08); padding:3px 10px; border-radius:9999px;">CEO 직속 결재 포맷</span>
        </div>
        """, unsafe_allow_html=True)

        # Bottom Line
        st.markdown(f"""
        <div class="executive-card" style="border-left: 4px solid #0071e3; background: rgba(0, 113, 227, 0.08);">
            <div style="font-size:0.78rem; font-weight:700; color:#2997ff; text-transform:uppercase; margin-bottom:4px;">Bottom Line (최종 의사결정 권고)</div>
            <div style="font-size:0.96rem; font-weight:600; color:#ffffff; line-height:1.6;">
                {an.get('bottom_line', '종합 합의안 추진')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.markdown(f"""
            <div class="executive-card">
                <div style="font-size:0.82rem; font-weight:700; color:#ff453a; margin-bottom:8px;">⚠️ Top 3 Key Risks & Mitigation</div>
                <ul style="color:#f5f5f7; font-size:0.88rem; line-height:1.7; padding-left:16px; margin:0;">
                    {"".join([f"<li>{r}</li>" for r in an.get('top_3_risks', [])])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_ex2:
            matrix_items = ""
            for m in an.get('alignment_matrix', []):
                matrix_items += f"<div style='margin-bottom:6px; font-size:0.86rem;'><b style='color:#2997ff;'>[{m.get('dept')}]</b> <span style='color:#86868b;'>{m.get('issue')}</span> ➔ <b style='color:#30d158;'>{m.get('resolution')}</b></div>"
            
            st.markdown(f"""
            <div class="executive-card">
                <div style="font-size:0.82rem; font-weight:700; color:#30d158; margin-bottom:8px;">🤝 Department Alignment Matrix</div>
                {matrix_items}
            </div>
            """, unsafe_allow_html=True)

        # Next Action Items
        actions_html = "".join([f"<span style='display:inline-block; background:#1c1c1e; border:1px solid rgba(255,255,255,0.1); padding:4px 10px; border-radius:8px; margin-right:8px; font-size:0.82rem;'><b>{a.get('action')}</b> (담당: <span style='color:#2997ff;'>{a.get('owner')}</span> / 기한: <span style='color:#ff9f0a;'>{a.get('due')}</span>)</span>" for a in an.get('next_actions', [])])
        st.markdown(f"""
        <div style="background:#141416; border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:12px 18px; margin-bottom:18px;">
            <span style="font-size:0.8rem; font-weight:700; color:#86868b; margin-right:12px;">Next Actions:</span>
            {actions_html}
        </div>
        """, unsafe_allow_html=True)

    # 5. 임원 보고용 독립 HTML 리포트 생성기
    st.markdown("---")
    col_r1, col_r2 = st.columns([3, 1])
    with col_r1:
        st.markdown("<div style='font-size: 0.98rem; font-weight: 700; color: #f5f5f7;'>Executive Decision Report (.html)</div>", unsafe_allow_html=True)
        st.caption("CEO 결재용 원페이지(One-pager) 서식으로 발행되어 인쇄 및 공유가 간편합니다.")
    with col_r2:
        if st.button("공식 보고서 생성", use_container_width=True):
            if not st.session_state.debate_history:
                st.warning("토론 기록이 필요합니다.")
            else:
                an = st.session_state.summary_analysis or {}
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                
                risks_li = "".join([f"<li style='margin-bottom:6px;'>{r}</li>" for r in an.get('top_3_risks', [])])
                matrix_tr = "".join([f"<tr><td style='font-weight:700; color:#0071e3; width:20%;'>{m.get('dept')}</td><td style='color:#555;'>{m.get('issue')}</td><td style='font-weight:600; color:#111;'>{m.get('resolution')}</td></tr>" for m in an.get('alignment_matrix', [])])
                actions_tr = "".join([f"<tr><td style='font-weight:600;'>{a.get('action')}</td><td style='text-align:center; color:#0071e3;'>{a.get('owner')}</td><td style='text-align:center; color:#ff9500;'>{a.get('due')}</td></tr>" for a in an.get('next_actions', [])])
                
                html_doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Executive Decision Report · Debate Room Pro</title>
    <style>
        @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css");
        * {{ font-family: "Pretendard", -apple-system, BlinkMacSystemFont, sans-serif !important; letter-spacing: -0.02em; box-sizing: border-box; }}
        body {{ margin: 0; padding: 36px 20px; background-color: #f5f5f7; color: #1d1d1f; }}
        .wrapper {{ max-width: 840px; margin: 0 auto; background: #ffffff; border-radius: 22px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); padding: 40px 44px; border: 1px solid #e5e5ea; }}
        .header {{ border-bottom: 2px solid #111; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .header-title {{ font-size: 24px; font-weight: 800; color: #111; margin: 0; }}
        .header-meta {{ font-size: 12px; color: #86868b; text-align: right; }}
        .section-title {{ font-size: 13.5px; font-weight: 700; color: #111; text-transform: uppercase; margin: 20px 0 8px 0; display: flex; align-items: center; gap: 6px; }}
        .section-title::before {{ content: ''; width: 4px; height: 14px; background: #0071e3; border-radius: 2px; }}
        .box-decision {{ background: #f0f7ff; border-left: 4px solid #0071e3; padding: 14px 18px; border-radius: 10px; font-size: 14.5px; font-weight: 600; color: #004085; line-height: 1.6; }}
        .box-gray {{ background: #f9f9fb; border: 1px solid #e5e5ea; border-radius: 10px; padding: 14px 18px; font-size: 13.5px; line-height: 1.6; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 13px; }}
        th {{ background: #f5f5f7; padding: 8px 12px; text-align: left; font-weight: 600; border-bottom: 1px solid #d2d2d7; color: #666; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; line-height: 1.5; }}
        .footer {{ text-align: center; font-size: 11px; color: #999; margin-top: 30px; padding-top: 14px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <div>
                <span style="font-size: 11px; font-weight: 700; color: #0071e3;">EXECUTIVE BRIEF · ONE-PAGER</span>
                <h1 class="header-title">Executive Decision Report</h1>
            </div>
            <div class="header-meta">
                Date: {now_str}<br>
                Chair: 설비구매 그룹장 (Orchestrator)
            </div>
        </div>

        <div class="section-title">1. Agenda & Situation</div>
        <div class="box-gray">{st.session_state.get('current_scenario', '')}</div>

        <div class="section-title">2. Bottom Line (Executive Directive)</div>
        <div class="box-decision">{an.get('bottom_line', '종합 합의 추진')}</div>

        <div class="section-title">3. Top 3 Key Risks & Mitigation</div>
        <div class="box-gray">
            <ul style="margin: 0; padding-left: 18px; font-size: 13.5px; line-height: 1.65;">
                {risks_li}
            </ul>
        </div>

        <div class="section-title">4. Department Alignment Matrix</div>
        <table>
            <thead><tr><th>Stakeholder</th><th>Key Concern / Risk</th><th>Aligned Resolution</th></tr></thead>
            <tbody>{matrix_tr}</tbody>
        </table>

        <div class="section-title">5. Next Action Items</div>
        <table>
            <thead><tr><th>Action</th><th style="text-align:center; width:20%;">Owner</th><th style="text-align:center; width:20%;">Timeline</th></tr></thead>
            <tbody>{actions_tr}</tbody>
        </table>

        <div class="footer">
            Generated via Debate Room Pro · Cross-Functional Decision Simulator
        </div>
    </div>
</body>
</html>"""
                st.session_state.generated_report = html_doc
                st.success("보고서 생성 완료!")

    if "generated_report" in st.session_state:
        st.download_button(
            label="📥 Executive Report 다운로드 (.html)",
            data=st.session_state.generated_report,
            file_name=f"Executive_Decision_Report_{datetime.date.today()}.html",
            mime="text/html",
            use_container_width=True
        )

# ----------------------------------------------------
# 9. 실시간 토론 실행 루프 엔진
# ----------------------------------------------------
if st.session_state.debate_status == "running":
    if st.session_state.remaining_seconds <= 0:
        st.session_state.debate_status = "completed"
        with st.spinner("Executive Briefing 분석 도출 중..."):
            try:
                p_sys = """당신은 CEO 및 경영진 직속 수석 의사결정 보좌관입니다. 
바쁜 임원이 30초 안에 결재할 수 있도록 가장 간결하고 함축적인 JSON 브리핑을 작성하십시오.
한국어를 기본으로 하되 Lead Time, LD 조항, FAT/SAT 등 실무 전문 용어를 자연스럽게 혼용하십시오."""
                p_usr = f"""Agenda: {st.session_state.get('current_scenario', '')}
Transcript: {json.dumps(st.session_state.debate_history, ensure_ascii=False)}

형식:
{{
    "bottom_line": "CEO 핵심 권고 1~2문장",
    "top_3_risks": ["Risk 1 & 대응책", "Risk 2 & 대응책", "Risk 3 & 대응책"],
    "alignment_matrix": [{{"dept":"부서","issue":"쟁점","resolution":"타협안"}}],
    "next_actions": [{{"action":"과제","owner":"담당","due":"기한"}}]
}}"""
                st.session_state.summary_analysis = execute_llm_json(selected_engine, api_key, model_name, p_sys, p_usr)
            except Exception as e:
                st.error(f"분석 중 오류: {e}")
        st.rerun()
    else:
        next_turn_idx = len(st.session_state.debate_history) + 1
        t_start = time.time()

        try:
            turn_data = stream_next_turn(
                selected_engine, api_key, model_name, st.session_state.get("current_scenario", ""), selected_depts,
                st.session_state.debate_history, stream_slot, next_turn_idx
            )
            st.session_state.debate_history.append(turn_data)
        except Exception as e:
            st.error(f"발언 생성 오류: {e}")
            st.session_state.debate_status = "paused"
            st.stop()

        elapsed = time.time() - t_start + 1.0
        st.session_state.remaining_seconds = max(0, st.session_state.remaining_seconds - elapsed)

        if st.session_state.remaining_seconds <= 0:
            st.session_state.debate_status = "completed"
            with st.spinner("Executive Briefing 분석 도출 중..."):
                try:
                    p_sys = """당신은 CEO 및 경영진 직속 수석 의사결정 보좌관입니다. 
바쁜 임원이 30초 안에 결재할 수 있도록 가장 간결하고 함축적인 JSON 브리핑을 작성하십시오.
한국어를 기본으로 하되 Lead Time, LD 조항, FAT/SAT 등 실무 전문 용어를 자연스럽게 혼용하십시오."""
                    p_usr = f"""Agenda: {st.session_state.get('current_scenario', '')}
Transcript: {json.dumps(st.session_state.debate_history, ensure_ascii=False)}

형식:
{{
    "bottom_line": "CEO 핵심 권고 1~2문장",
    "top_3_risks": ["Risk 1 & 대응책", "Risk 2 & 대응책", "Risk 3 & 대응책"],
    "alignment_matrix": [{{"dept":"부서","issue":"쟁점","resolution":"타협안"}}],
    "next_actions": [{{"action":"과제","owner":"담당","due":"기한"}}]
}}"""
                    st.session_state.summary_analysis = execute_llm_json(selected_engine, api_key, model_name, p_sys, p_usr)
                except Exception as e:
                    st.error(f"분석 중 오류: {e}")

        st.rerun()