"""
notifications.py
Automação de avisos de pontos via WhatsApp (deep link wa.me).
Registra histórico de notificações enviadas/preparadas.
"""

import re
import urllib.parse
from datetime import datetime
from typing import Any, Dict, Optional

from database import get_conn, get_program_texts, get_public_base_url
from calculations import format_currency, get_rewards_status
from utils import create_welcome_purchase_message, create_milestone_reward_message


def format_phone_for_whatsapp(phone: str, country_code: str = "55") -> str:
    """Normaliza telefone brasileiro para formato wa.me (somente dígitos com DDI)."""
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return ""
    if digits.startswith(country_code) and len(digits) >= 12:
        return digits
    if len(digits) in (10, 11):
        return f"{country_code}{digits}"
    if len(digits) >= 12:
        return digits
    return f"{country_code}{digits}"


def build_whatsapp_url(phone: str, message: str) -> str:
    """Gera link wa.me com mensagem pré-preenchida."""
    formatted = format_phone_for_whatsapp(phone)
    encoded = urllib.parse.quote(message, safe="")
    if formatted:
        return f"https://wa.me/{formatted}?text={encoded}"
    return f"https://wa.me/?text={encoded}"


def get_first_name(full_name: str) -> str:
    return full_name.split()[0] if full_name else "Parceiro"


def build_purchase_message(
    client: Dict[str, Any],
    result: Dict[str, Any],
) -> str:
    """Monta mensagem de compra usando template personalizado ou fallback."""
    texts = get_program_texts()
    program_name = texts.get("program_name", "Programa Parceiro Isopor")
    template = texts.get("whatsapp_purchase", "")
    first = get_first_name(client["name"])
    # Versão simples: sem resgate
    rewards = get_rewards_status(
        client["current_points"],
        client.get("total_packages_bought", 0),
    )
    progress_msg = rewards.get("summary_text", "")

    # Link do painel do cliente
    base_url = get_public_base_url()
    client_link = f"{base_url}/?view=cliente&id={client['id']}"

    if template:
        try:
            return template.format(
                first_name=first,
                program_name=program_name,
                amount=format_currency(result.get("amount", 0)),
                final_points=result["final_points"],
                current_points=client["current_points"],
                package_message="",
                progress_message=progress_msg,
                client_link=client_link,
            )
        except KeyError:
            pass

    return create_welcome_purchase_message(
        client_name=client["name"],
        amount=result.get("amount", 0),
        final_points=result["final_points"],
        current_points=client["current_points"],
        available_packages=0,
        client_link=client_link,
    )


def build_redemption_message(
    client: Dict[str, Any],
    num_packages: int,
    redeem_result: Dict[str, Any],
) -> str:
    """Monta mensagem de resgate usando template personalizado ou fallback."""
    texts = get_program_texts()
    program_name = texts.get("program_name", "Programa Parceiro Isopor")
    template = texts.get("whatsapp_redemption", "")
    first = get_first_name(client["name"])

    if template:
        return template.format(
            first_name=first,
            program_name=program_name,
            num_packages=int(num_packages),
            points_deducted=redeem_result["points_deducted"],
            remaining_points=redeem_result["remaining_points"],
        )

    return create_redemption_message(
        client_name=client["name"],
        packages=int(num_packages),
        points_deducted=redeem_result["points_deducted"],
        remaining_points=redeem_result["remaining_points"],
    )


def init_notification_log() -> None:
    """Cria tabela de log de notificações se não existir."""
    conn = get_conn()
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS notification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL,
            message TEXT NOT NULL,
            phone TEXT,
            status TEXT NOT NULL DEFAULT 'prepared',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_notification_log_client
            ON notification_log(client_id, created_at);
        """)
        conn.commit()
    finally:
        conn.close()


def log_notification(
    client_id: int,
    notification_type: str,
    message: str,
    phone: str = "",
    status: str = "prepared",
) -> int:
    """Registra notificação no histórico. Retorna o ID do log."""
    init_notification_log()
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO notification_log
            (client_id, notification_type, message, phone, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (client_id, notification_type, message, phone, status),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_recent_notifications(limit: int = 10) -> list:
    """Últimas notificações com nome do cliente."""
    init_notification_log()
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT n.id, n.client_id, c.name as client_name, n.notification_type,
                   n.phone, n.status, n.created_at
            FROM notification_log n
            JOIN clients c ON c.id = n.client_id
            ORDER BY n.created_at DESC, n.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
def build_milestone_reward_message(
    client: Dict[str, Any],
    reward_description: str,
) -> str:
    """Monta mensagem de recompensa de marco 500 usando template ou fallback."""
    texts = get_program_texts()
    program_name = texts.get("program_name", "Programa Parceiro Isopor")
    template = texts.get("whatsapp_milestone_500", "")
    first = get_first_name(client["name"])

    if template:
        return template.format(
            first_name=first,
            program_name=program_name,
            reward_description=reward_description,
        )

    return create_milestone_reward_message(
        client_name=client["name"],
        reward_description=reward_description,
        program_name=program_name,
    )
