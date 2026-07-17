"""
regenerate_receipts.py
Gera (ou regenera) os recibos de compra (cartão PNG + mensagem WhatsApp) de
TODAS as compras já registradas no banco, preenchendo a tabela
purchase_receipts. Mantém apenas os 10 recibos mais recentes por cliente
(mesma regra usada pelo app ao registrar uma nova compra).

Uso:
    python regenerate_receipts.py
"""

from database import (
    init_db,
    get_conn,
    get_all_settings,
    get_program_rules,
    save_purchase_receipt,
)
from notifications import build_purchase_message
from notification_card import generate_points_card
from calculations import get_milestone_progress


def regenerate_all_receipts() -> None:
    init_db()
    settings = get_all_settings()
    rules = get_program_rules()
    threshold = rules.get("milestone_packages_threshold", 500)

    conn = get_conn()
    try:
        clients = conn.execute("SELECT id, name, phone FROM clients ORDER BY id").fetchall()
        total_generated = 0

        for c in clients:
            purchases = conn.execute("""
                SELECT id, purchase_date, amount, final_points, COALESCE(package_quantity, 0) as package_quantity
                FROM purchases
                WHERE client_id = ?
                ORDER BY purchase_date ASC, id ASC
            """, (c["id"],)).fetchall()

            running_points = 0
            running_packages = 0

            for p in purchases:
                running_points += int(p["final_points"] or 0)
                running_packages += int(p["package_quantity"] or 0)

                # Snapshot do cliente no momento histórico desta compra
                # (saldo acumulado até e incluindo esta compra).
                client_snapshot = {
                    "id": c["id"],
                    "name": c["name"],
                    "phone": c["phone"],
                    "current_points": running_points,
                    "total_packages_bought": running_packages,
                    "milestone_packages_threshold": threshold,
                }
                result = {
                    "final_points": int(p["final_points"] or 0),
                    "amount": p["amount"],
                    "date": p["purchase_date"],
                }

                message = build_purchase_message(client_snapshot, result)
                remaining = get_milestone_progress(running_points, threshold)["remaining"]

                card_buffer = generate_points_card(
                    client_name=c["name"],
                    points_earned=result["final_points"],
                    current_points=running_points,
                    amount=result["amount"],
                    settings=settings,
                    available_packages=0,
                    points_to_next_package=remaining,
                    total_packages_bought=running_packages,
                    milestone_remaining=threshold - running_packages,
                )

                save_purchase_receipt(
                    client_id=c["id"],
                    purchase_id=p["id"],
                    purchase_date=p["purchase_date"],
                    message=message,
                    card_image=card_buffer.getvalue(),
                )
                total_generated += 1

        print(
            f"OK: {total_generated} recibo(s) processado(s) para {len(clients)} cliente(s). "
            f"Cada cliente mantem os 10 mais recentes."
        )
    finally:
        conn.close()


if __name__ == "__main__":
    regenerate_all_receipts()
