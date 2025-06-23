from decimal import Decimal
from random import random
from sqlite3 import OperationalError
from time import time
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc, exists, func, and_, select, update
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import selectinload, joinedload, Session
import models
import schemas


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    """
    Получает товар по ID для админки - возвращает все варианты независимо от статуса и остатков.
    """

    # Основной запрос с eager loading всех связанных данных
    stmt = (
        select(models.Product)
        .options(
            selectinload(models.Product.variants)
            .selectinload(models.ProductVariant.attributes)
            .joinedload(models.VariantAttribute.attribute),
            selectinload(models.Product.images),
            joinedload(models.Product.category),
            joinedload(models.Product.brand),
        )
        .where(models.Product.id == product_id)
    )

    # Выполняем запрос
    product = db.scalar(stmt)

    return product


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 12,
    category_slug: Optional[str] = None,
    brand_slugs: Optional[List[str]] = None,
    size_values: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
) -> Tuple[List[models.Product], int]:

    # Базовый запрос с eager loading
    stmt = select(models.Product).options(
        selectinload(models.Product.variants)
        .selectinload(models.ProductVariant.attributes)
        .joinedload(models.VariantAttribute.attribute),
        selectinload(models.Product.images),
        joinedload(models.Product.category),
        joinedload(models.Product.brand),
    )

    # Фильтрация товаров, которые полностью отсутствуют на складе или неактивны
    stmt = stmt.where(
        exists().where(
            and_(
                models.ProductVariant.product_id == models.Product.id,
                models.ProductVariant.stock > 0,
                models.ProductVariant.status == models.VariantStatus.ACTIVE,
            )
        )
    )

    # Фильтрация по категориям
    if category_slug:
        category_tree = _build_category_tree(db)
        start_category = category_tree.get(category_slug)
        if start_category:
            category_ids = _get_descendant_and_self_ids(start_category)
            stmt = stmt.where(models.Product.category_id.in_(category_ids))
        else:
            return [], 0  # Категория не найдена

    # Фильтрация по брендам
    if brand_slugs:
        stmt = stmt.join(models.Brand).where(models.Brand.slug.in_(brand_slugs))

    # Фильтрация по вариантам (цена, размер)
    variant_filters_exist = any(
        [min_price is not None, max_price is not None, size_values]
    )
    if variant_filters_exist:
        # Создаем подзапрос для фильтрации вариантов
        variant_subquery = select(models.ProductVariant.product_id).distinct()

        # Добавляем фильтр активных вариантов в наличии
        variant_conditions = [
            models.ProductVariant.stock > 0,
            models.ProductVariant.status == models.VariantStatus.ACTIVE,
        ]

        if min_price is not None:
            variant_conditions.append(models.ProductVariant.price >= min_price)

        if max_price is not None:
            variant_conditions.append(models.ProductVariant.price <= max_price)

        if size_values:
            variant_subquery = variant_subquery.join(models.VariantAttribute).join(
                models.Attribute
            )
            variant_conditions.extend(
                [
                    models.Attribute.type == "size",
                    models.Attribute.value.in_(size_values),
                ]
            )

        variant_subquery = variant_subquery.where(and_(*variant_conditions))
        stmt = stmt.where(models.Product.id.in_(variant_subquery))

    # Логика сортировки
    if sort_by in ["price_asc", "price_desc"]:
        # Подзапрос для получения минимальной цены активных вариантов
        min_price_subquery = (
            select(
                models.ProductVariant.product_id,
                func.min(models.ProductVariant.price).label("min_price"),
            )
            .where(
                and_(
                    models.ProductVariant.stock > 0,
                    models.ProductVariant.status == models.VariantStatus.ACTIVE,
                )
            )
            .group_by(models.ProductVariant.product_id)
            .subquery()
        )

        stmt = stmt.join(
            min_price_subquery, models.Product.id == min_price_subquery.c.product_id
        )
        order_by_col = (
            asc(min_price_subquery.c.min_price)
            if sort_by == "price_asc"
            else desc(min_price_subquery.c.min_price)
        )
        stmt = stmt.order_by(order_by_col)
    elif sort_by == "name_asc":
        stmt = stmt.order_by(asc(models.Product.name))
    elif sort_by == "name_desc":
        stmt = stmt.order_by(desc(models.Product.name))
    else:  # Сортировка по умолчанию
        stmt = stmt.order_by(desc(models.Product.created_at))

    # Получение общего количества до пагинации
    # Создаем копию запроса без order_by для подсчета
    count_stmt = stmt.with_only_columns(models.Product.id).distinct()
    # Убираем order_by из запроса для подсчета (он не нужен и может вызывать проблемы)
    count_stmt = count_stmt.order_by(None)
    total_count = (
        db.scalar(select(func.count()).select_from(count_stmt.subquery())) or 0
    )

    # Применение пагинации и получение результатов
    stmt = stmt.offset(skip).limit(limit)
    products = list(db.scalars(stmt).unique().all())

    # Фильтрация вариантов в результатах
    for product in products:
        # Сначала фильтруем по остаткам на складе и статусу
        product.variants = [
            v
            for v in product.variants
            if v.stock > 0 and v.status == models.VariantStatus.ACTIVE
        ]

        # Затем применяем дополнительные фильтры, если они есть
        if variant_filters_exist:
            filtered_variants = []
            for variant in product.variants:
                # Проверяем фильтр по цене
                if min_price is not None and variant.price < min_price:
                    continue
                if max_price is not None and variant.price > max_price:
                    continue

                # Проверяем фильтр по размеру
                if size_values:
                    variant_sizes = [
                        attr.attribute.value
                        for attr in variant.attributes
                        if attr.attribute.type == "size"
                    ]
                    if not any(size in size_values for size in variant_sizes):
                        continue

                filtered_variants.append(variant)

            product.variants = filtered_variants

    return products, total_count


# Вспомогательные функции (нужно будет реализовать отдельно)
def _build_category_tree(db: Session) -> Dict[str, Any]:
    """
    Строит дерево категорий для эффективного поиска потомков.
    Возвращает словарь, где ключ - slug категории, значение - объект категории с потомками.
    """
    # Загружаем все категории одним запросом
    categories_stmt = select(models.Category).options(
        selectinload(models.Category.children)
    )
    categories = db.scalars(categories_stmt).all()

    # Строим словарь для быстрого доступа по slug
    category_tree = {}
    for category in categories:
        category_tree[category.slug] = category

    return category_tree


def _get_descendant_and_self_ids(category) -> List[int]:
    """
    Рекурсивно получает ID категории и всех её потомков.
    """
    ids = [category.id]

    def collect_descendant_ids(cat):
        for child in cat.children:
            ids.append(child.id)
            collect_descendant_ids(child)

    collect_descendant_ids(category)
    return ids


def get_filters_for_category(db: Session, category_slug: str) -> Dict[str, Any]:
    """
    Получает доступные фильтры для категории.
    Оптимизированная версия с минимальным количеством запросов.
    """

    # Получаем категорию с прямыми детьми для подкатегорий
    start_category_with_children = db.scalar(
        select(models.Category)
        .options(selectinload(models.Category.children))
        .where(models.Category.slug == category_slug)
    )

    if not start_category_with_children:
        return {"brands": [], "sizes": [], "subcategories": []}

    # Получаем подкатегории (прямые дочерние)
    subcategories = [
        {"name": child.name, "slug": child.slug}
        for child in start_category_with_children.children
    ]

    # Для фильтрации брендов и размеров нужны ID всех потомков
    category_tree = _build_category_tree(db)
    tree_start_node = category_tree.get(category_slug)

    if not tree_start_node:
        return {"brands": [], "sizes": [], "subcategories": subcategories}

    category_ids = _get_descendant_and_self_ids(tree_start_node)

    # Получаем бренды
    brands_query = (
        select(models.Brand.id, models.Brand.name, models.Brand.slug)
        .join(models.Product)
        .where(
            and_(
                models.Product.category_id.in_(category_ids),
                # Проверяем что у продукта есть активные варианты в наличии
                exists().where(
                    and_(
                        models.ProductVariant.product_id == models.Product.id,
                        models.ProductVariant.stock > 0,
                        models.ProductVariant.status == models.VariantStatus.ACTIVE,
                    )
                ),
            )
        )
        .distinct()
    )

    # Получаем размеры
    sizes_query = (
        select(models.Attribute.value)
        .join(models.VariantAttribute)
        .join(models.ProductVariant)
        .join(models.Product)
        .where(
            and_(
                models.Product.category_id.in_(category_ids),
                models.Attribute.type == "size",
                models.ProductVariant.stock > 0,
                models.ProductVariant.status == models.VariantStatus.ACTIVE,
            )
        )
        .distinct()
    )

    # Выполняем запросы
    brands_result = db.execute(brands_query).all()
    sizes_result = db.execute(sizes_query).all()

    # Формируем результат
    brands = [
        {"id": brand_id, "name": name, "slug": slug}
        for brand_id, name, slug in brands_result
    ]

    sizes = sorted(
        [size[0] for size in sizes_result],
        key=lambda x: (str.isdigit(x), x),  # Сначала буквенные размеры, потом цифровые
    )

    return {"brands": brands, "sizes": sizes, "subcategories": subcategories}


def get_products_for_admin(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_slug: Optional[str] = None,
    brand_slugs: Optional[List[str]] = None,
    size_values: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    max_stock: Optional[int] = None,
    status: Optional[str] = None,
) -> Tuple[List[models.Product], int]:
    """
    Получение продуктов для админ-панели с полной информацией о вариантах.
    Включает все варианты продуктов независимо от статуса и остатков на складе.
    """

    # Базовый запрос с eager loading для всех связанных данных
    stmt = select(models.Product).options(
        selectinload(models.Product.variants)
        .selectinload(models.ProductVariant.attributes)
        .joinedload(models.VariantAttribute.attribute),
        selectinload(models.Product.images),
        joinedload(models.Product.category),
        joinedload(models.Product.brand),
    )

    # Для админа показываем ВСЕ продукты (даже без активных вариантов)
    # Убираем фильтрацию по активным вариантам из пользовательской версии

    # Фильтрация по категориям
    if category_slug:
        category_tree = _build_category_tree(db)
        start_category = category_tree.get(category_slug)
        if start_category:
            category_ids = _get_descendant_and_self_ids(start_category)
            stmt = stmt.where(models.Product.category_id.in_(category_ids))
        else:
            return [], 0  # Категория не найдена

    # Фильтрация по брендам
    if brand_slugs:
        stmt = stmt.join(models.Brand).where(models.Brand.slug.in_(brand_slugs))

    # Фильтрация по статусу (специфично для админа)
    if status:
        # Находим продукты, у которых есть варианты с указанным статусом
        status_subquery = (
            select(models.ProductVariant.product_id)
            .distinct()
            .where(models.ProductVariant.status == status)
        )
        stmt = stmt.where(models.Product.id.in_(status_subquery))

    # Фильтрация по максимальному остатку (специфично для админа)
    if max_stock is not None:
        # Находим продукты, у которых есть варианты с остатком <= max_stock
        low_stock_subquery = (
            select(models.ProductVariant.product_id)
            .distinct()
            .where(models.ProductVariant.stock <= max_stock)
        )
        stmt = stmt.where(models.Product.id.in_(low_stock_subquery))

    # Обновляем переменную для включения max_stock и status
    other_variant_filters_exist = any(
        [min_price is not None, max_price is not None, size_values]
    )
    if other_variant_filters_exist:
        # Создаем подзапрос для фильтрации вариантов (БЕЗ фильтра по статусу и остаткам)
        variant_subquery = select(models.ProductVariant.product_id).distinct()
        variant_conditions = []

        if min_price is not None:
            variant_conditions.append(models.ProductVariant.price >= min_price)

        if max_price is not None:
            variant_conditions.append(models.ProductVariant.price <= max_price)

        if size_values:
            variant_subquery = variant_subquery.join(models.VariantAttribute).join(
                models.Attribute
            )
            variant_conditions.extend(
                [
                    models.Attribute.type == "size",
                    models.Attribute.value.in_(size_values),
                ]
            )

        if variant_conditions:
            variant_subquery = variant_subquery.where(and_(*variant_conditions))
            stmt = stmt.where(models.Product.id.in_(variant_subquery))

    # Логика сортировки
    if sort_by in ["price_asc", "price_desc"]:
        # Подзапрос для получения минимальной цены среди ВСЕХ вариантов (не только активных)
        min_price_subquery = (
            select(
                models.ProductVariant.product_id,
                func.min(models.ProductVariant.price).label("min_price"),
            )
            .group_by(models.ProductVariant.product_id)
            .subquery()
        )

        stmt = stmt.join(
            min_price_subquery, models.Product.id == min_price_subquery.c.product_id
        )
        order_by_col = (
            asc(min_price_subquery.c.min_price)
            if sort_by == "price_asc"
            else desc(min_price_subquery.c.min_price)
        )
        stmt = stmt.order_by(order_by_col)
    elif sort_by == "name_asc":
        stmt = stmt.order_by(asc(models.Product.name))
    elif sort_by == "name_desc":
        stmt = stmt.order_by(desc(models.Product.name))
    else:  # Сортировка по умолчанию
        stmt = stmt.order_by(desc(models.Product.created_at))

    # Получение общего количества до пагинации
    count_stmt = stmt.with_only_columns(models.Product.id).distinct()
    count_stmt = count_stmt.order_by(None)
    total_count = (
        db.scalar(select(func.count()).select_from(count_stmt.subquery())) or 0
    )

    # Применение пагинации и получение результатов
    stmt = stmt.offset(skip).limit(limit)
    products = list(db.scalars(stmt).unique().all())

    # ДЛЯ АДМИНА: Фильтруем варианты по заданным критериям
    for product in products:
        filtered_variants = []

        for variant in product.variants:
            # Проверяем фильтр по статусу
            if status and variant.status != status:
                continue

            # Проверяем фильтр по максимальному остатку
            if max_stock is not None and variant.stock > max_stock:
                continue

            # Проверяем фильтр по цене
            if min_price is not None and variant.price < min_price:
                continue
            if max_price is not None and variant.price > max_price:
                continue

            # Проверяем фильтр по размеру
            if size_values:
                variant_sizes = [
                    attr.attribute.value
                    for attr in variant.attributes
                    if attr.attribute.type == "size"
                ]
                if not any(size in size_values for size in variant_sizes):
                    continue

            filtered_variants.append(variant)

        product.variants = filtered_variants

    return products, total_count


def create_order(
    db: Session, checkout_form: schemas.CheckoutForm, max_retries: int = 3
) -> models.Order:
    """
    Создает новый заказ с элементами заказа с оптимистичной блокировкой для SQLite.

    Args:
        db: Сессия базы данных
        checkout_form: Данные формы оформления заказа
        max_retries: Максимальное количество попыток при конкурентном доступе

    Returns:
        Order: Созданный заказ

    Raises:
        ValueError: При недостаточном количестве товара или неактивном варианте
    """
    # ИСПРАВЛЕНО: используем VariantId вместо productId для получения вариантов
    variant_ids = [item.ProductVariantId for item in checkout_form.cart]

    for attempt in range(max_retries):
        try:
            # Получаем актуальные данные о товарах
            stmt = (
                select(models.ProductVariant)
                .options(selectinload(models.ProductVariant.product))
                .where(models.ProductVariant.id.in_(variant_ids))
            )
            variants = db.execute(stmt).scalars().all()
            variants_dict = {variant.id: variant for variant in variants}

            # Валидация и подготовка данных
            total_amount = Decimal("0")
            order_items_data = []

            for cart_item in checkout_form.cart:
                # ИСПРАВЛЕНО: используем VariantId для получения варианта
                variant = variants_dict.get(cart_item.ProductVariantId)

                if not variant:
                    raise ValueError(
                        f"Вариант товара с ID {cart_item.ProductVariantId} не найден"
                    )

                if variant.status != models.VariantStatus.ACTIVE:
                    raise ValueError(
                        f"Товар '{variant.product.name}' недоступен для заказа"
                    )

                if variant.stock < cart_item.quantity:
                    raise ValueError(
                        f"Недостаточно товара '{variant.product.name}'. "
                        f"Доступно: {variant.stock}, запрошено: {cart_item.quantity}"
                    )

                unit_price = variant.price
                total_price = unit_price * cart_item.quantity
                total_amount += total_price

                order_items_data.append(
                    {
                        "variant_id": variant.id,
                        "quantity": cart_item.quantity,
                        "unit_price": unit_price,
                        "total_price": total_price,
                        "current_stock": variant.stock,  # Запоминаем текущий остаток
                    }
                )

            # Создаем заказ
            # ИСПРАВЛЕНО: добавлен shipping_city согласно схеме CheckoutForm
            order = models.Order(
                customer_name=checkout_form.name,
                customer_phone=checkout_form.phone,
                shipping_city=checkout_form.shipping_city,  # Добавлено поле города
                total_amount=total_amount,
                status=models.OrderStatus.PENDING,
            )

            db.add(order)
            db.flush()

            # Создаем элементы заказа
            order_items = [
                models.OrderItem(
                    order_id=order.id,
                    variant_id=item_data["variant_id"],
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    total_price=item_data["total_price"],
                )
                for item_data in order_items_data
            ]

            db.add_all(order_items)

            # Оптимистичное обновление остатков - обновляем только если остаток не изменился
            # Это эквивалент row-level locking через optimistic concurrency control
            failed_updates = []

            for item_data in order_items_data:
                update_stmt = (
                    update(models.ProductVariant)
                    .where(
                        and_(
                            models.ProductVariant.id == item_data["variant_id"],
                            models.ProductVariant.stock
                            == item_data["current_stock"],  # Оптимистичная проверка
                        )
                    )
                    .values(stock=item_data["current_stock"] - item_data["quantity"])
                )

                result = db.execute(update_stmt)

                if result.rowcount == 0:
                    # Остаток изменился - добавляем в список неудачных обновлений
                    variant_name = variants_dict[item_data["variant_id"]].product.name
                    failed_updates.append(variant_name)

            if failed_updates:
                # Если есть неудачные обновления, откатываем и повторяем
                db.rollback()
                if attempt < max_retries - 1:
                    # Небольшая задержка перед повтором
                    time.sleep(random.uniform(0.01, 0.05))
                    continue
                else:
                    raise ValueError(
                        f"Остатки товаров изменились: {', '.join(failed_updates)}"
                    )

            # Все обновления прошли успешно
            db.commit()
            db.refresh(order)
            return order

        except ValueError:
            # Ошибки валидации не требуют повтора
            db.rollback()
            raise

        except OperationalError as e:
            # Database locked - повторяем
            db.rollback()
            if attempt < max_retries - 1:
                time.sleep(random.uniform(0.05, 0.1))
                continue
            else:
                raise ValueError("База данных временно недоступна")

        except Exception as e:
            db.rollback()
            if attempt < max_retries - 1:
                time.sleep(random.uniform(0.01, 0.05))
                continue
            else:
                raise ValueError("Ошибка при создании заказа")

    raise ValueError("Не удалось создать заказ после всех попыток")


def get_order_by_id(db: Session, order_id: int) -> Optional[models.Order]:
    """
    Получает заказ по ID с предзагрузкой связанных данных.

    Args:
        db: Сессия базы данных
        order_id: ID заказа

    Returns:
        Order | None: Заказ или None если не найден
    """
    stmt = (
        select(models.Order)
        .options(
            selectinload(models.Order.items)
            .selectinload(models.OrderItem.variant)
            .selectinload(models.ProductVariant.product),
            selectinload(models.Order.items)
            .selectinload(models.OrderItem.variant)
            .selectinload(models.ProductVariant.attributes),
        )
        .where(models.Order.id == order_id)
    )

    return db.execute(stmt).scalar_one_or_none()


def update_order_status(
    db: Session, order_id: int, status: models.OrderStatus
) -> Optional[models.Order]:
    """
    Обновляет статус заказа.

    Args:
        db: Сессия базы данных
        order_id: ID заказа
        status: Новый статус

    Returns:
        Order | None: Обновленный заказ или None если не найден
    """
    order = db.get(models.Order, order_id)
    if not order:
        return None

    order.status = status

    # Если заказ отменяется, возвращаем товары на склад
    if status == models.OrderStatus.CANCELLED:
        stmt = (
            select(models.OrderItem)
            .options(selectinload(models.OrderItem.variant))
            .where(models.OrderItem.order_id == order_id)
        )
        order_items = db.execute(stmt).scalars().all()

        for item in order_items:
            item.variant.stock += item.quantity

    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        raise
