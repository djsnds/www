from database import Base

from datetime import datetime
from enum import Enum
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func
import uuid


class TimestampMixin:
    """Миксин для автоматического управления временными метками"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class VariantStatus(str, Enum):
    """Статусы варианта продукта"""

    ACTIVE = "active"
    SOLD_OUT = "sold_out"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class OrderStatus(str, Enum):
    """Статусы заказа"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Category(Base, TimestampMixin):
    """Категории товаров с поддержкой иерархии"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan"
    )
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="category"
    )

    __table_args__ = (
        Index("ix_categories_slug", "slug"),
        Index("ix_categories_parent_id", "parent_id"),
    )


class Brand(Base, TimestampMixin):
    """Бренды товаров"""

    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand")

    __table_args__ = (Index("ix_brands_slug", "slug"),)


class Product(Base, TimestampMixin):
    """Основная модель продукта"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="products"
    )
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_products_slug", "slug"),
        Index("ix_products_category", "category_id"),
        Index(
            "ix_products_brand",
            "brand_id",
        ),
    )


class ProductVariant(Base, TimestampMixin):
    """Варианты продукта (размер, цвет и т.д.)"""

    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    status: Mapped[VariantStatus] = mapped_column(
        String(20), default=VariantStatus.ACTIVE, nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    attributes: Mapped[List["VariantAttribute"]] = relationship(
        "VariantAttribute", back_populates="variant", cascade="all, delete-orphan"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="variant"
    )

    __table_args__ = (
        Index("ix_variants_product_id", "product_id"),
        Index("ix_variants_sku", "sku"),
        Index("ix_variants_status_stock", "status", "stock"),
    )

    @validates("price")
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError("Price must be positive")
        return value

    @validates("stock")
    def validate_stock(self, key, value):
        if value < 0:
            raise ValueError("Stock cannot be negative")
        return value


class Attribute(Base, TimestampMixin):
    """Атрибуты продуктов (цвет, размер и т.д.)"""

    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    variants: Mapped[List["VariantAttribute"]] = relationship(
        "VariantAttribute", back_populates="attribute"
    )

    __table_args__ = (
        UniqueConstraint("type", "value", name="uq_attributes_type_value"),
        Index("ix_attributes_type", "type"),
    )


class VariantAttribute(Base):
    """Связь вариантов продуктов с атрибутами"""

    __tablename__ = "variant_attributes"

    variant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    attribute_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attributes.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant", back_populates="attributes"
    )
    attribute: Mapped["Attribute"] = relationship(
        "Attribute", back_populates="variants"
    )

    __table_args__ = (
        Index("ix_variant_attributes_variant_id", "variant_id"),
        Index("ix_variant_attributes_attribute_id", "attribute_id"),
    )


class ProductImage(Base, TimestampMixin):
    """Изображения продуктов"""

    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="images")

    __table_args__ = (Index("ix_images_product_id", "product_id"),)


class Order(Base, TimestampMixin):
    """Заказы"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[OrderStatus] = mapped_column(
        String(20), default=OrderStatus.PENDING, nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Customer information
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Shipping information
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shipping_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shipping_country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_orders_status", "status"),
        Index("ix_orders_customer_name", "customer_name"),
        Index("ix_orders_customer_phone", "customer_phone"),
    )


class OrderItem(Base, TimestampMixin):
    """Элементы заказа"""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_variants.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant", back_populates="order_items"
    )

    __table_args__ = (
        Index("ix_order_items_variant_id", "variant_id"),
        Index("ix_order_items_order_id", "order_id"),
    )
