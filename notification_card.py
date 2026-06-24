"""
notification_card.py
Gera cartão de fidelidade (PNG) usando os templates base pré-renderizados
em templates/purchase_base.png e templates/milestone_base.png.
Apenas os dados dinâmicos são desenhados sobre o template.
"""

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from calculations import format_currency, get_milestone_progress

BASE_DIR = Path(__file__).parent
PURCHASE_BASE  = BASE_DIR / "templates" / "purchase_base.png"
MILESTONE_BASE = BASE_DIR / "templates" / "milestone_base.png"

# Posições de cada elemento de dado (coordenadas do template 848x1264)
RECT_TOP   = 514
RECT_LEFT  = 51
RECT_RIGHT = 797
BAR_Y      = 960
BAR_X1     = 75
BAR_X2     = 773
BAR_H      = 22
CX         = (RECT_LEFT + RECT_RIGHT) // 2   # 424

# Y de cada campo dinâmico no cartão de compra
Y_POINTS  = RECT_TOP + 92    # "+X PONTOS GANHOS"
Y_INFO    = Y_POINTS + 80    # "Compra: X | Saldo: X"
Y_FALTAM  = Y_INFO + 34      # "Faltam X pontos..."

# Y do nome no cartão milestone
Y_NAME_MILE = RECT_TOP + 40


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _glow(img: Image.Image, pos, text: str, font,
          text_color, glow_color, radius: int = 12, anchor: str = "mt") -> Image.Image:
    for r, alpha in [(radius, 220), (max(1, radius // 2), 160)]:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text(pos, text, font=font,
                                   fill=(*glow_color[:3], alpha), anchor=anchor)
        layer = layer.filter(ImageFilter.GaussianBlur(radius=r))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    ImageDraw.Draw(img).text(pos, text, font=font, fill=text_color, anchor=anchor)
    return img


def _cover(draw: ImageDraw.ImageDraw, y: int, height: int, bg_color):
    """Cobre uma faixa horizontal com a cor de fundo para apagar texto anterior."""
    draw.rectangle([(RECT_LEFT + 5, y - 4), (RECT_RIGHT - 5, y + height + 4)],
                   fill=bg_color)


def _progress_bar(draw: ImageDraw.ImageDraw, pct: float, bg_color):
    teal = (0, 220, 210)
    draw.rectangle([(BAR_X1 - 5, BAR_Y - 8), (BAR_X2 + 5, BAR_Y + BAR_H + 10)],
                   fill=bg_color)
    fill_w = int((BAR_X2 - BAR_X1) * min(1.0, pct))
    draw.rounded_rectangle([(BAR_X1, BAR_Y), (BAR_X2, BAR_Y + BAR_H)],
                            radius=10, fill=(40, 55, 70))
    if fill_w > 0:
        draw.rounded_rectangle([(BAR_X1, BAR_Y), (BAR_X1 + fill_w, BAR_Y + BAR_H)],
                                radius=10, fill=teal)
    draw.text(((BAR_X1 + BAR_X2) // 2, BAR_Y + BAR_H // 2),
              f"{int(pct * 100)}%", font=_load_font(13, bold=True),
              fill=(240, 245, 250), anchor="mm")


def generate_points_card(
    client_name: str,
    points_earned: int,
    current_points: int,
    amount: float,
    settings: Optional[Dict[str, Any]] = None,
    available_packages: int = 0,
    points_to_next_package: int = 0,
    total_packages_bought: int = 0,
    milestone_remaining: int = 0,
) -> BytesIO:
    settings = settings or {}
    teal  = (0, 220, 210)
    white = (240, 245, 250)
    muted = (150, 170, 190)
    first_name = client_name.split()[0] if client_name else "Parceiro"
    pkg_info = get_milestone_progress(current_points)
    is_milestone = pkg_info["reached"]

    if is_milestone:
        # ── CARTÃO MILESTONE ─────────────────────────────────────────────────
        # Template já tem: "VOCÊ ATINGIU O MARCO DE", "500 PACOTES", "CAFETEIRA",
        # barra 100%, rodapé. Só o nome do cliente é dinâmico.
        img = Image.open(MILESTONE_BASE).convert("RGB")
        bg_color = img.getpixel((10, 460))
        draw = ImageDraw.Draw(img)

        # Cobre área do nome e desenha o nome real
        _cover(draw, Y_NAME_MILE, 50, bg_color)
        font_name = _load_font(36, bold=True)
        img = _glow(img, (CX, Y_NAME_MILE), f"Parabéns, {first_name}!",
                    font_name, white, teal, radius=8)

    else:
        # ── CARTÃO DE COMPRA ─────────────────────────────────────────────────
        # Template já tem: título "Parabéns! Você ganhou pontos!" e barra estática.
        # Dados dinâmicos: pontos, compra/saldo, faltam, barra de progresso.
        img = Image.open(PURCHASE_BASE).convert("RGB")
        bg_color = img.getpixel((10, 460))
        draw = ImageDraw.Draw(img)

        # +X PONTOS GANHOS
        _cover(draw, Y_POINTS, 90, bg_color)
        font_big = _load_font(66, bold=True)
        img = _glow(img, (CX, Y_POINTS), f"+{points_earned} PONTOS GANHOS",
                    font_big, teal, teal, radius=14)
        draw = ImageDraw.Draw(img)

        # Compra | Saldo
        _cover(draw, Y_INFO, 28, bg_color)
        font_info = _load_font(20)
        draw.text((CX, Y_INFO),
                  f"Compra: {format_currency(amount)}  |  Saldo atual: {current_points} pts",
                  font=font_info, fill=white, anchor="mt")

        # Faltam X pontos
        remaining = points_to_next_package if points_to_next_package > 0 else pkg_info["remaining"]
        _cover(draw, Y_FALTAM, 24, bg_color)
        font_faltam = _load_font(18)
        draw.text((CX, Y_FALTAM),
                  f"Faltam {remaining} pontos para ganhar a cafeteira",
                  font=font_faltam, fill=muted, anchor="mt")

        # Barra dinâmica
        pct = min(1.0, current_points / 500.0)
        _progress_bar(draw, pct, bg_color)

    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer
