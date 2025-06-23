"""
Скрипт для заполнения базы данных тестовыми данными
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Импорт моделей (предполагается, что они в файле models.py)
from models import (
    Base,
    Category,
    Brand,
    Product,
    ProductVariant,
    Attribute,
    VariantAttribute,
    ProductImage,
    Order,
    OrderItem,
    VariantStatus,
    OrderStatus,
)

# Настройка базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./shop.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, bind=engine)


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("✅ Таблицы созданы")


def create_categories():
    db = SessionLocal()
    try:
        # Основные категории
        mens = Category(name="Мужская одежда", slug="mens")
        womens = Category(name="Женская одежда", slug="womens")
        shoes = Category(name="Кроссовки", slug="sneakers")

        db.add_all([mens, womens, shoes])
        db.commit()

        # Подкатегории для мужской одежды
        mens_tshirts = Category(name="Футболки", slug="mens-tshirts", parent=mens)
        mens_hoodies = Category(name="Кофты", slug="mens-hoodies", parent=mens)

        # Подкатегории для женской одежды
        womens_tshirts = Category(name="Футболки", slug="womens-tshirts", parent=womens)
        womens_cardigans = Category(
            name="Кардиганы", slug="womens-cardigans", parent=womens
        )

        db.add_all([mens_tshirts, mens_hoodies, womens_tshirts, womens_cardigans])
        db.commit()

        return {
            "mens": mens.id,
            "womens": womens.id,
            "sneakers": shoes.id,
            "mens_tshirts": mens_tshirts.id,
            "mens_hoodies": mens_hoodies.id,
            "womens_tshirts": womens_tshirts.id,
            "womens_cardigans": womens_cardigans.id,
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании категорий: {e}")
        return {}
    finally:
        db.close()


def create_brands():
    db = SessionLocal()
    try:
        brands_data = [
            ("Nike", "nike"),
            ("Adidas", "adidas"),
            ("Puma", "puma"),
            ("Zara", "zara"),
            ("H&M", "hm"),
            ("Uniqlo", "uniqlo"),
            ("Lacoste", "lacoste"),
            ("Tommy Hilfiger", "tommy-hilfiger"),
        ]

        brands = [Brand(name=name, slug=slug) for name, slug in brands_data]
        db.add_all(brands)
        db.commit()
        return {brand.slug: brand.id for brand in brands}
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании брендов: {e}")
        return {}
    finally:
        db.close()


def create_attributes():
    db = SessionLocal()
    try:
        attributes_data = [
            ("size", "XS"),
            ("size", "S"),
            ("size", "M"),
            ("size", "L"),
            ("size", "XL"),
            ("size", "39"),
            ("size", "40"),
            ("size", "41"),
            ("size", "42"),
        ]

        attributes = [
            Attribute(type=type, value=value) for type, value in attributes_data
        ]
        db.add_all(attributes)
        db.commit()
        return {f"{attr.type}_{attr.value}": attr.id for attr in attributes}
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании атрибутов: {e}")
        return {}
    finally:
        db.close()


def create_products_and_variants(categories, brands, attributes):
    db = SessionLocal()
    try:
        products_data = [
            # Мужские футболки
            {
                "name": "Футболка Nike Classic",
                "slug": "nike-classic-tshirt",
                "description": "Классическая хлопковая футболка с логотипом Nike. Удобная и дышащая.",
                "category_id": categories["mens_tshirts"],
                "brand_id": brands["nike"],
                "variants": [
                    {
                        "price": 29.99,
                        "stock": 100,
                        "attributes": [
                            "size_M",
                        ],
                    },
                    {
                        "price": 29.99,
                        "stock": 0,
                        "attributes": [
                            "size_L",
                        ],
                    },
                ],
            },
            {
                "name": "Футболка Adidas Originals",
                "slug": "adidas-originals-tshirt",
                "description": "Футболка с классическим логотипом Adidas. 100% хлопок, удобный крой.",
                "category_id": categories["mens_tshirts"],
                "brand_id": brands["adidas"],
                "variants": [
                    {"price": 34.99, "stock": 70, "attributes": ["size_S"]},
                    {"price": 34.99, "stock": 60, "attributes": ["size_M"]},
                ],
            },
            # Мужские кофты
            {
                "name": "Кофта Puma Sport",
                "slug": "puma-sport-hoodie",
                "description": "Теплая спортивная кофта с капюшоном. Идеальна для прохладной погоды.",
                "category_id": categories["mens_hoodies"],
                "brand_id": brands["puma"],
                "variants": [
                    {"price": 59.99, "stock": 40, "attributes": ["size_L"]},
                    {
                        "price": 59.99,
                        "stock": 35,
                        "attributes": [
                            "size_XL",
                        ],
                    },
                ],
            },
            {
                "name": "Кофта Tommy Hilfiger Classic",
                "slug": "tommy-hilfiger-classic-hoodie",
                "description": "Стильная кофта с фирменной полоской Tommy Hilfiger. Качественный хлопок.",
                "category_id": categories["mens_hoodies"],
                "brand_id": brands["tommy-hilfiger"],
                "variants": [
                    {"price": 79.99, "stock": 30, "attributes": ["size_M"]},
                    {"price": 79.99, "stock": 25, "attributes": ["size_L"]},
                ],
            },
            # Женские футболки
            {
                "name": "Футболка H&M Basic",
                "slug": "hm-basic-tshirt",
                "description": "Базовая женская футболка из мягкого хлопка. Универсальный вариант на каждый день.",
                "category_id": categories["womens_tshirts"],
                "brand_id": brands["hm"],
                "variants": [
                    {
                        "price": 19.99,
                        "stock": 90,
                        "attributes": ["size_S"],
                        "status": VariantStatus.INACTIVE,
                    },
                    {"price": 19.99, "stock": 85, "attributes": ["size_M"]},
                ],
            },
            {
                "name": "Футболка Uniqlo U",
                "slug": "uniqlo-u-tshirt",
                "description": "Футболка премиального качества от Uniqlo. Плотный хлопок, идеальная посадка.",
                "category_id": categories["womens_tshirts"],
                "brand_id": brands["uniqlo"],
                "variants": [
                    {
                        "price": 24.99,
                        "stock": 50,
                        "status": "inactive",
                        "attributes": [
                            "size_XS",
                        ],
                    },
                    {
                        "price": 24.99,
                        "stock": 45,
                        "attributes": [
                            "size_S",
                        ],
                    },
                ],
            },
            # Женские кардиганы
            {
                "name": "Кардиган Zara Oversize",
                "slug": "zara-oversize-cardigan",
                "description": "Модный оверсайз кардиган свободного кроя. Теплый и уютный.",
                "category_id": categories["womens_cardigans"],
                "brand_id": brands["zara"],
                "variants": [
                    {"price": 59.99, "stock": 50, "attributes": ["size_S"]},
                    {"price": 59.99, "stock": 40, "attributes": ["size_M"]},
                ],
            },
            {
                "name": "Кардиган Lacoste Elegance",
                "slug": "lacoste-elegance-cardigan",
                "description": "Элегантный кардиган с фирменным крокодилом Lacoste. Идеален для офиса.",
                "category_id": categories["womens_cardigans"],
                "brand_id": brands["lacoste"],
                "variants": [
                    {"price": 89.99, "stock": 30, "attributes": ["size_S"]},
                    {"price": 89.99, "stock": 25, "attributes": ["size_M"]},
                ],
            },
            # Кроссовки
            {
                "name": "Кроссовки Adidas Ultraboost",
                "slug": "adidas-ultraboost",
                "description": "Легендарные кроссовки с технологией Boost для максимального комфорта.",
                "category_id": categories["sneakers"],
                "brand_id": brands["adidas"],
                "variants": [
                    {"price": 149.99, "stock": 30, "attributes": ["size_42"]},
                    {"price": 149.99, "stock": 25, "attributes": ["size_41"]},
                ],
            },
            {
                "name": "Кроссовки Nike Air Force 1",
                "slug": "nike-air-force-1",
                "description": "Культовые кроссовки Nike с подошвой Air. Вечная классика.",
                "category_id": categories["sneakers"],
                "brand_id": brands["nike"],
                "variants": [
                    {"price": 129.99, "stock": 35, "attributes": ["size_40"]},
                    {"price": 129.99, "stock": 30, "attributes": ["size_39"]},
                ],
            },
            {
                "name": "Кроссовки Puma RS-X",
                "slug": "puma-rs-x",
                "description": "Стильные кроссовки с ретро-дизайном. Удобная амортизация.",
                "category_id": categories["sneakers"],
                "brand_id": brands["puma"],
                "variants": [
                    {"price": 99.99, "stock": 25, "attributes": ["size_43"]},
                    {"price": 99.99, "stock": 20, "attributes": ["size_42"]},
                ],
            },
        ]

        for product_data in products_data:
            product = Product(
                name=product_data["name"],
                slug=product_data["slug"],
                description=product_data["description"],
                category_id=product_data["category_id"],
                brand_id=product_data["brand_id"],
            )
            db.add(product)
            db.flush()

            for i, variant_data in enumerate(product_data["variants"]):
                variant = ProductVariant(
                    product_id=product.id,
                    sku=f"{product_data['slug']}-{i+1:03d}",
                    price=Decimal(str(variant_data["price"])),
                    stock=variant_data["stock"],
                    status=variant_data.get(
                        "status", VariantStatus.ACTIVE
                    ),  # Используем переданный статус или ACTIVE по умолчанию
                )
                db.add(variant)
                db.flush()

                for attr_key in variant_data["attributes"]:
                    if attr_key in attributes:
                        db.add(
                            VariantAttribute(
                                variant_id=variant.id, attribute_id=attributes[attr_key]
                            )
                        )

            for j in range(1, 4):
                db.add(
                    ProductImage(
                        product_id=product.id,
                        url=f"https://example.com/images/{product_data['slug']}-{j}.jpg",
                    )
                )

        db.commit()
        print("📦 Продукты созданы")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании продуктов: {e}")
    finally:
        db.close()


def main():
    print("🚀 Начинаем заполнение базы данных...")
    create_tables()
    categories = create_categories()
    brands = create_brands()
    attributes = create_attributes()
    create_products_and_variants(categories, brands, attributes)
    print("\n✅ База данных успешно заполнена!")


if __name__ == "__main__":
    main()
