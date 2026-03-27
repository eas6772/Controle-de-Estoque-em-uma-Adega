from datetime import date, timedelta
from typing import List, Tuple

from app.extensions import db
from app.models import Batch, Product, StockMovement


def suggested_sale_price(preco_custo: float, margem: float = 0.30) -> float:
    return round(preco_custo * (1 + margem), 2)


def produtos_vencendo(dias: int = 30) -> list[Batch]:
    limite = date.today() + timedelta(days=dias)
    return Batch.query.filter(Batch.data_validade <= limite, Batch.quantidade > 0).all()


def pick_fifo_batches(product_id: int, quantidade: int) -> List[Tuple[Batch, int]]:
    lotes = (
        Batch.query.filter_by(produto_id=product_id)
        .filter(Batch.quantidade > 0, Batch.data_validade >= date.today())
        .order_by(Batch.data_validade.asc(), Batch.data_entrada.asc())
        .all()
    )
    restante = quantidade
    saida: list[tuple[Batch, int]] = []
    for lote in lotes:
        if restante <= 0:
            break
        mover = min(lote.quantidade, restante)
        saida.append((lote, mover))
        restante -= mover
    if restante > 0:
        raise ValueError("Estoque insuficiente ou lotes disponíveis estão vencidos.")
    return saida


def register_sale(product: Product, quantidade: int, usuario_id: int) -> None:
    if quantidade <= 0:
        raise ValueError("Quantidade de venda inválida.")
    lotes_saida = pick_fifo_batches(product.id, quantidade)
    for lote, retirada in lotes_saida:
        lote.quantidade -= retirada
    movimento = StockMovement(
        produto_id=product.id,
        tipo="venda",
        quantidade=quantidade,
        usuario_id=usuario_id,
        motivo="Venda via PDV",
    )
    db.session.add(movimento)
    db.session.commit()
