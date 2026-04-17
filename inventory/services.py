from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import InventoryItem, MovimientoInventario


@dataclass(frozen=True)
class StockLine:
    producto_id: int
    cantidad: int
    nombre: str


class InventoryError(Exception):
    pass


class InsufficientStockError(InventoryError):
    def __init__(self, items: list[dict]):
        self.items = items
        super().__init__("Stock insuficiente para completar la operacion.")


class InvalidStockAdjustmentError(InventoryError):
    pass


def build_stock_line(*, producto_id: int, cantidad: int, nombre: str) -> StockLine:
    return StockLine(producto_id=producto_id, cantidad=cantidad, nombre=nombre)


def _aggregate_lines(lines: Iterable[StockLine]) -> list[StockLine]:
    aggregated: dict[int, StockLine] = {}

    for line in lines:
        if line.cantidad <= 0:
            raise InvalidStockAdjustmentError("La cantidad debe ser mayor que cero.")
        if line.producto_id in aggregated:
            previous = aggregated[line.producto_id]
            aggregated[line.producto_id] = StockLine(
                producto_id=line.producto_id,
                cantidad=previous.cantidad + line.cantidad,
                nombre=previous.nombre,
            )
            continue
        aggregated[line.producto_id] = line

    return list(aggregated.values())


def _lock_inventory_items(*, product_ids: list[int], create_missing: bool) -> dict[int, InventoryItem]:
    queryset = InventoryItem.objects.select_for_update().select_related("producto")
    inventory_map = {
        inventory_item.producto_id: inventory_item
        for inventory_item in queryset.filter(producto_id__in=product_ids)
    }

    if not create_missing:
        return inventory_map

    missing_product_ids = [product_id for product_id in product_ids if product_id not in inventory_map]
    if not missing_product_ids:
        return inventory_map

    for product_id in missing_product_ids:
        inventory_item, _ = InventoryItem.objects.select_for_update().get_or_create(producto_id=product_id)
        inventory_map[product_id] = inventory_item

    return inventory_map


def descontar_stock(
    *,
    lines: Iterable[StockLine],
    actor=None,
    motivo: str = "",
    referencia: str = "",
) -> list[MovimientoInventario]:
    normalized_lines = _aggregate_lines(lines)
    inventory_map = _lock_inventory_items(
        product_ids=[line.producto_id for line in normalized_lines],
        create_missing=False,
    )

    stock_errors = []
    for line in normalized_lines:
        inventory_item = inventory_map.get(line.producto_id)
        cantidad_disponible = inventory_item.cantidad_disponible if inventory_item else 0
        if cantidad_disponible < line.cantidad:
            stock_errors.append(
                {
                    "product_id": line.producto_id,
                    "nombre": line.nombre,
                    "requested": line.cantidad,
                    "available": cantidad_disponible,
                }
            )

    if stock_errors:
        raise InsufficientStockError(stock_errors)

    movimientos = []
    for line in normalized_lines:
        inventory_item = inventory_map[line.producto_id]
        cantidad_anterior = inventory_item.cantidad_disponible
        inventory_item.cantidad_disponible -= line.cantidad
        inventory_item.save(update_fields=["cantidad_disponible", "actualizado_en"])
        movimientos.append(
            MovimientoInventario(
                item_inventario=inventory_item,
                tipo=MovimientoInventario.Tipo.SALIDA,
                cantidad=line.cantidad,
                cantidad_anterior=cantidad_anterior,
                cantidad_posterior=inventory_item.cantidad_disponible,
                motivo=motivo,
                referencia=referencia,
                creado_por=actor,
            )
        )

    return MovimientoInventario.objects.bulk_create(movimientos)


def reingresar_stock(
    *,
    lines: Iterable[StockLine],
    actor=None,
    motivo: str = "",
    referencia: str = "",
) -> list[MovimientoInventario]:
    normalized_lines = _aggregate_lines(lines)
    inventory_map = _lock_inventory_items(
        product_ids=[line.producto_id for line in normalized_lines],
        create_missing=True,
    )

    movimientos = []
    for line in normalized_lines:
        inventory_item = inventory_map[line.producto_id]
        cantidad_anterior = inventory_item.cantidad_disponible
        inventory_item.cantidad_disponible += line.cantidad
        inventory_item.save(update_fields=["cantidad_disponible", "actualizado_en"])
        movimientos.append(
            MovimientoInventario(
                item_inventario=inventory_item,
                tipo=MovimientoInventario.Tipo.ENTRADA,
                cantidad=line.cantidad,
                cantidad_anterior=cantidad_anterior,
                cantidad_posterior=inventory_item.cantidad_disponible,
                motivo=motivo,
                referencia=referencia,
                creado_por=actor,
            )
        )

    return MovimientoInventario.objects.bulk_create(movimientos)


def ajustar_stock(
    *,
    inventory_item: InventoryItem,
    cantidad_disponible: int,
    actor=None,
    motivo: str = "",
    referencia: str = "",
) -> MovimientoInventario:
    if cantidad_disponible < 0:
        raise InvalidStockAdjustmentError("La cantidad disponible no puede ser negativa.")

    inventory_item = (
        InventoryItem.objects
        .select_for_update()
        .select_related("producto")
        .get(pk=inventory_item.pk)
    )
    cantidad_anterior = inventory_item.cantidad_disponible
    if cantidad_disponible == cantidad_anterior:
        raise InvalidStockAdjustmentError("El ajuste no cambia el stock disponible.")
    inventory_item.cantidad_disponible = cantidad_disponible
    inventory_item.save(update_fields=["cantidad_disponible", "actualizado_en"])
    return MovimientoInventario.objects.create(
        item_inventario=inventory_item,
        tipo=MovimientoInventario.Tipo.AJUSTE,
        cantidad=abs(cantidad_disponible - cantidad_anterior) or 1,
        cantidad_anterior=cantidad_anterior,
        cantidad_posterior=inventory_item.cantidad_disponible,
        motivo=motivo,
        referencia=referencia,
        creado_por=actor,
    )


def registrar_entrada_stock(
    *,
    inventory_item: InventoryItem,
    cantidad: int,
    actor=None,
    motivo: str = "",
    referencia: str = "",
) -> MovimientoInventario:
    if cantidad <= 0:
        raise InvalidStockAdjustmentError("La cantidad de entrada debe ser mayor que cero.")

    inventory_item = (
        InventoryItem.objects
        .select_for_update()
        .select_related("producto")
        .get(pk=inventory_item.pk)
    )
    cantidad_anterior = inventory_item.cantidad_disponible
    inventory_item.cantidad_disponible += cantidad
    inventory_item.save(update_fields=["cantidad_disponible", "actualizado_en"])
    return MovimientoInventario.objects.create(
        item_inventario=inventory_item,
        tipo=MovimientoInventario.Tipo.ENTRADA,
        cantidad=cantidad,
        cantidad_anterior=cantidad_anterior,
        cantidad_posterior=inventory_item.cantidad_disponible,
        motivo=motivo,
        referencia=referencia,
        creado_por=actor,
    )
