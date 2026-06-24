import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "mediinsight.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_history_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                filename TEXT,
                report_type TEXT,
                risk_level TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT,
                context_type TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(report_id) REFERENCES reports(id)
            )
            """
        )


def save_report(
    report_id: str,
    filename: str,
    report_type: str,
    risk_level: str,
    summary: str,
) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO reports (id, filename, report_type, risk_level, summary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (report_id, filename, report_type, risk_level, summary),
        )


def save_chat_message(
    question: str,
    answer: str,
    model: str,
    context_type: str,
    report_id: str | None = None,
) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (report_id, context_type, question, answer, model)
            VALUES (?, ?, ?, ?, ?)
            """,
            (report_id, context_type, question, answer, model),
        )


def get_chat_history(report_id: str | None = None, limit: int = 50) -> list[dict]:
    with _connect() as conn:
        if report_id:
            rows = conn.execute(
                """
                SELECT id, report_id, context_type, question, answer, model, created_at
                FROM chat_messages
                WHERE report_id = ? OR report_id IS NULL
                ORDER BY id DESC
                LIMIT ?
                """,
                (report_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, report_id, context_type, question, answer, model, created_at
                FROM chat_messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [dict(row) for row in rows]


def clear_chat_history(report_id: str | None = None) -> int:
    """Delete chat history rows and return number of deleted records."""
    with _connect() as conn:
        if report_id:
            cursor = conn.execute(
                "DELETE FROM chat_messages WHERE report_id = ? OR report_id IS NULL",
                (report_id,),
            )
        else:
            cursor = conn.execute("DELETE FROM chat_messages")
        return cursor.rowcount


def get_report_list(limit: int = 20) -> list[dict]:
    """Return most recent uploaded reports for comparison picker."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, filename, report_type, risk_level, summary, created_at
            FROM reports
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def save_report_analysis(report_id: str, analysis_json: str) -> None:
    """Persist full analysis JSON into reports table (added lazily if column missing)."""
    with _connect() as conn:
        try:
            conn.execute("ALTER TABLE reports ADD COLUMN analysis_json TEXT")
        except Exception:
            pass  # column already exists
        conn.execute(
            "UPDATE reports SET analysis_json = ? WHERE id = ?",
            (analysis_json, report_id),
        )


def get_report_analysis(report_id: str) -> dict | None:
    """Return stored analysis dict for a report, or None if not found."""
    import json
    with _connect() as conn:
        row = conn.execute(
            "SELECT analysis_json, filename, report_type, risk_level, created_at FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    try:
        d["analysis"] = json.loads(d.pop("analysis_json") or "{}")
    except Exception:
        d["analysis"] = {}
    return d
