from __future__ import annotations

import base64
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st


BASE_URL = "https://ranking.scorito.com/6/ranking/v2.0/gameranking/getpage/1078336/0/{page}"
PAGE_SIZE_HINT = 10
REQUEST_TIMEOUT = 15
DISPLAY_COLUMNS = ["Rank", "UserName", "RoundPoints", "TotalPoints", "Delta", "UserId"]
TABLE_COLUMNS = ["Rank", "UserName", "RoundPoints", "TotalPoints"]
TABLE_LABELS = {
    "Rank": "Positie",
    "UserName": "Naam",
    "RoundPoints": "Ronde punten",
    "TotalPoints": "Totale punten",
}
PHOTO_DIR = Path("photos")
PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
}


class RankingError(Exception):
    """Raised when the ranking API cannot be read into the expected table."""


st.set_page_config(
    page_title="Scorito Ranking",
    page_icon="T",
    layout="wide",
)


st.markdown(
    """
    <style>
        :root {
            --surface: #ffffff;
            --surface-muted: #f3f5f2;
            --line: #d8ded4;
            --ink: #20252c;
            --muted: #697169;
            --navy: #313767;
            --green: #75a808;
            --green-dark: #5f8f00;
            --steel: #eef1ed;
        }

        .stApp {
            background:
                linear-gradient(180deg, #eef2eb 0, #f7f8f5 270px, #f7f8f5 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        .brand-header {
            background: var(--navy);
            border-radius: 8px;
            color: #ffffff;
            display: flex;
            align-items: stretch;
            min-height: 128px;
            overflow: hidden;
            margin-bottom: 1rem;
            box-shadow: 0 18px 45px rgba(32, 37, 44, 0.12);
        }

        .brand-mark {
            background: var(--green);
            display: flex;
            align-items: center;
            justify-content: center;
            width: 220px;
            min-width: 220px;
            padding: 1rem;
            text-align: center;
        }

        .brand-mark strong {
            display: block;
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: 0.08rem;
            line-height: 1;
        }

        .brand-mark span {
            display: block;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.18rem;
            margin-top: 0.42rem;
            text-transform: uppercase;
        }

        .brand-copy {
            flex: 1;
            padding: 1.35rem 1.55rem;
        }

        .brand-kicker {
            color: #a9ca42;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.1rem;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
        }

        .brand-title {
            font-size: 1.7rem;
            font-weight: 800;
            line-height: 1.2 !important;
            letter-spacing: 0 !important;
            margin-bottom: 0.35rem !important;
        }

        .brand-subtitle {
            color: #dfe7db;
            font-size: 0.95rem;
            max-width: 680px;
        }

        .toolbar-row {
            align-items: center;
            color: var(--muted);
            display: flex;
            font-size: 0.9rem;
            justify-content: space-between;
            margin: 0.2rem 0 1rem;
        }

        .screen-grid {
            align-items: start;
            display: grid;
            gap: 1rem;
            grid-template-columns: minmax(420px, 0.95fr) minmax(520px, 1.35fr);
            margin-top: 0.6rem;
        }

        .podium-panel,
        .ranking-panel {
            min-width: 0;
        }

        .section-label {
            color: var(--muted);
            font-size: 0.88rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .podium-stack {
            display: grid;
            gap: 0.85rem;
        }

        .podium-card {
            align-items: center;
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 5px solid var(--green);
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(32, 37, 44, 0.05);
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            min-height: 245px;
            padding: 1rem;
            text-align: center;
            width: 100%;
        }

        .podium-card.is-first {
            background: linear-gradient(180deg, #ffffff 0%, #f7fbef 100%);
            min-height: 300px;
            padding: 1.25rem;
        }

        .podium-row-small {
            display: grid;
            gap: 0.85rem;
            grid-template-columns: 1fr 1fr;
        }

        .podium-photo {
            background: var(--navy);
            border: 4px solid #edf3e2;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 112px;
            overflow: hidden;
            width: 112px;
            min-width: 112px;
        }

        .podium-card.is-first .podium-photo {
            border-width: 6px;
            height: 170px;
            width: 170px;
            min-width: 170px;
        }

        .podium-photo img {
            height: 100%;
            object-fit: cover;
            width: 100%;
        }

        .podium-initials {
            color: #ffffff;
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: 0;
        }

        .podium-card.is-first .podium-initials {
            font-size: 3.5rem;
        }

        .podium-rank {
            color: var(--green);
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.08rem;
            text-transform: uppercase;
        }

        .podium-name {
            color: var(--ink);
            font-size: 1.15rem;
            font-weight: 800;
            line-height: 1.15;
        }

        .podium-card.is-first .podium-name {
            font-size: 1.6rem;
        }

        .podium-meta {
            color: var(--muted);
            font-size: 0.9rem;
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 5px solid var(--green);
            border-radius: 8px;
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 25px rgba(32, 37, 44, 0.05);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
        }

        [data-testid="stMetricValue"] {
            color: var(--ink);
            font-size: 1.55rem;
            font-weight: 800;
        }

        div[data-testid="stButton"] button {
            border-radius: 6px;
            border: 1px solid var(--green);
            color: #ffffff;
            background: var(--green);
            font-weight: 700;
        }

        div[data-testid="stButton"] button:hover {
            border-color: var(--green-dark);
            color: #ffffff;
            background: var(--green-dark);
        }

        [data-testid="stTextInput"] label {
            color: var(--ink);
            font-weight: 700;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(32, 37, 44, 0.05);
        }

        .meta-row {
            color: var(--muted);
            font-size: 0.88rem;
            margin: 0.25rem 0 1rem;
        }

        @media (max-width: 760px) {
            .brand-header {
                display: block;
            }

            .brand-mark {
                min-width: 0;
                width: 100%;
            }

            .brand-copy {
                padding: 1.1rem;
            }

            .podium-card,
            .podium-card.is-first {
                min-height: 0;
            }

            .screen-grid,
            .podium-row-small {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _api_error_message(payload: dict[str, Any]) -> str:
    for key in ("Message", "ErrorMessage", "ResultMessage", "Description"):
        value = payload.get(key)
        if value:
            return str(value)
    return "The Scorito API returned an error without a message."


def _get_required_content(payload: dict[str, Any], page: int) -> dict[str, Any]:
    if payload.get("ResultCode") != 0:
        raise RankingError(_api_error_message(payload))

    content = payload.get("Content")
    if not isinstance(content, dict):
        raise RankingError(f"Unexpected JSON structure on page {page}: missing Content object.")

    return content


def _fetch_page(page: int) -> dict[str, Any]:
    url = BASE_URL.format(page=page)

    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RankingError(f"Request failed for page {page}: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RankingError(f"Page {page} did not return valid JSON.") from exc

    if not isinstance(payload, dict):
        raise RankingError(f"Unexpected JSON structure on page {page}: expected a JSON object.")

    return payload


def _normalize_row(item: dict[str, Any]) -> dict[str, Any]:
    return {column: item.get(column) for column in DISPLAY_COLUMNS}


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_ranking() -> tuple[pd.DataFrame, int, datetime]:
    rows: list[dict[str, Any]] = []
    participant_count: int | None = None
    page = 0

    while True:
        payload = _fetch_page(page)
        content = _get_required_content(payload, page)

        if participant_count is None:
            raw_count = content.get("ParticipantCount")
            if not isinstance(raw_count, int):
                raise RankingError("Unexpected JSON structure: Content.ParticipantCount is missing or invalid.")
            participant_count = raw_count

        ranking_items = content.get("RankingItems")
        if ranking_items is None:
            raise RankingError(f"Unexpected JSON structure on page {page}: missing Content.RankingItems.")
        if not isinstance(ranking_items, list):
            raise RankingError(f"Unexpected JSON structure on page {page}: RankingItems is not a list.")
        if not ranking_items:
            break

        for item in ranking_items:
            if not isinstance(item, dict):
                raise RankingError(f"Unexpected JSON structure on page {page}: a ranking item is not an object.")
            rows.append(_normalize_row(item))

        if len(rows) >= participant_count:
            rows = rows[:participant_count]
            break

        # The API appears to use 10 rows per page, but the loop also works if that changes.
        page += 1
        if len(ranking_items) < PAGE_SIZE_HINT and len(rows) >= participant_count:
            break

    if participant_count is None:
        raise RankingError("Unexpected JSON structure: no participant count was returned.")

    df = pd.DataFrame(rows, columns=DISPLAY_COLUMNS)
    if not df.empty:
        df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
        df["RoundPoints"] = pd.to_numeric(df["RoundPoints"], errors="coerce")
        df["TotalPoints"] = pd.to_numeric(df["TotalPoints"], errors="coerce")
        df["Delta"] = pd.to_numeric(df["Delta"], errors="coerce")
        df = df.sort_values("Rank", ascending=True, na_position="last").reset_index(drop=True)

    return df, participant_count, datetime.now()


def format_number(value: Any) -> str:
    if pd.isna(value):
        return "-"
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


def photo_path_for_user(user_name: Any) -> Path | None:
    if not isinstance(user_name, str) or not user_name.strip():
        return None

    safe_name = "".join(character for character in user_name if character.isalnum() or character in (" ", "-", "_")).strip()
    candidates = {user_name.strip(), safe_name, safe_name.replace(" ", "_"), safe_name.replace(" ", "-")}

    for candidate in candidates:
        for extension in PHOTO_EXTENSIONS:
            path = PHOTO_DIR / f"{candidate}{extension}"
            if path.exists():
                return path

    return None


def initials_for_user(user_name: Any) -> str:
    if not isinstance(user_name, str) or not user_name.strip():
        return "1"

    parts = [part for part in user_name.replace("_", " ").replace("-", " ").split(" ") if part]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return "".join(part[0] for part in parts[:2]).upper()
    
@st.cache_data(show_spinner=False)
def image_data_uri(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix == "jpg" else suffix
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"

def image_data_uri(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix == "jpg" else suffix
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def participant_photo_html(user_name: Any, class_name: str = "podium-photo") -> str:
    photo_path = photo_path_for_user(user_name)
    if photo_path:
        return f'<div class="{class_name}"><img src="{image_data_uri(photo_path)}" alt="{escape(str(user_name))}"></div>'
    return f'<div class="{class_name}"><div class="podium-initials">{initials_for_user(user_name)}</div></div>'


def podium_card(row: pd.Series, rank_label: str, extra_class: str = "") -> str:
    user_name = row.get("UserName")
    return (
        f'<div class="podium-card {extra_class}">'
        f"{participant_photo_html(user_name)}"
        f'<div class="podium-rank">{rank_label}</div>'
        f'<div class="podium-name">{escape(str(user_name))}</div>'
        f'<div class="podium-meta">'
        f'{format_number(row.get("TotalPoints"))} totale punten · '
        f'{format_number(row.get("RoundPoints"))} ronde punten'
        f"</div>"
        f"</div>"
    )


st.markdown(
    """
    <div class="brand-header">
        <div class="brand-mark">
            <div>
                <strong>TOPCALF</strong>
                <span>Calf Housing Solutions</span>
            </div>
        </div>
        <div class="brand-copy">
            <div class="brand-kicker">Done by People, Inspired by Calves</div>
            <div class="brand-title">Scorito Ranking</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

header_left, header_right = st.columns([1, 0.22])
with header_right:
    if st.button("Refresh ranking", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

try:
    ranking_df, participant_count, last_updated = fetch_ranking()
except RankingError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:
    st.error(f"Unexpected error while loading the ranking: {exc}")
    st.stop()

podium_area, ranking_area = st.columns([0.95, 1.35], gap="medium")

top_three = [ranking_df.iloc[index] for index in range(min(3, len(ranking_df)))]
with podium_area:
    if top_three:
        podium_items = {
            int(row["Rank"]): row
            for row in top_three
            if not pd.isna(row.get("Rank"))
        }
        st.markdown('<div class="section-label">Podium</div>', unsafe_allow_html=True)
        if 1 in podium_items:
            st.markdown(podium_card(podium_items[1], "#1", "is-first"), unsafe_allow_html=True)

        small_2, small_3 = st.columns(2, gap="small")
        if 2 in podium_items:
            with small_2:
                st.markdown(podium_card(podium_items[2], "#2"), unsafe_allow_html=True)
        if 3 in podium_items:
            with small_3:
                st.markdown(podium_card(podium_items[3], "#3"), unsafe_allow_html=True)

with ranking_area:
    st.markdown('<div class="section-label">Ranglijst</div>', unsafe_allow_html=True)
    display_df = ranking_df[TABLE_COLUMNS].rename(columns=TABLE_LABELS)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=690,
        hide_index=True,
        column_config={
            "Positie": st.column_config.NumberColumn("Positie", format="%d"),
            "Ronde punten": st.column_config.NumberColumn("Ronde punten", format="%d"),
            "Totale punten": st.column_config.NumberColumn("Totale punten", format="%d"),
        },
    )
