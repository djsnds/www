from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime as dt
import models

# Base Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None


class ImageBase(BaseModel):
    url: str
    product_id: int


class AttributeBase(BaseModel):
    type: str
    value: str


class ProductVariantBase(BaseModel):
    price: float
    stock: int
    product_id: int


# Schemas for creating data (e.g., from API requests)
class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None


# Schemas for reading data (e.g., for API responses)
class Image(ImageBase):
    model_config = ConfigDict(from_attributes=True)


class Attribute(AttributeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class VariantAttribute(BaseModel):
    attribute: Attribute
    model_config = ConfigDict(from_attributes=True)


class ProductVariant(ProductVariantBase):
    id: int
    attributes: List[VariantAttribute] = []
    model_config = ConfigDict(from_attributes=True)


class Product(ProductBase):
    id: int
    category: Optional["Category"] = None
    brand: Optional["Brand"] = None
    images: List[Image] = []
    variants: List[ProductVariant] = []
    model_config = ConfigDict(from_attributes=True)


class Brand(BaseModel):
    id: int
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    id: int
    name: str
    slug: str
    children: List["Category"] = []
    model_config = ConfigDict(from_attributes=True)


# Update forward reference
Category.model_rebuild()


# Schemas for router responses
class ProductDetail(Product):  # Inherits from Product
    pass


class ProductList(BaseModel):
    products: List[Product]
    total_count: int


class SubCategory(BaseModel):
    name: str
    slug: str


class FilterOptions(BaseModel):
    brands: List[Brand]
    sizes: List[str]
    subcategories: List[SubCategory]


# Schemas for Checkout/Cart
class CartItem(BaseModel):
    ProductVariantId: int
    quantity: int
    


class CheckoutForm(BaseModel):
    name: str
    phone: str
    shipping_city: str
    cart: List[CartItem]


class OrderItem(BaseModel):
    quantity: int
    unit_price: float
    variant: ProductVariant
    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class VariantStatusSchema(str, Enum):
    ACTIVE = "active"
    SOLD_OUT = "sold_out"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


# AdminProduct
class AdminProductVariant(BaseModel):
    id: int
    price: Decimal
    stock: int
    sku: Optional[str] = None
    status: VariantStatusSchema
    product_id: int
    attributes: List[VariantAttribute] = []
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None
    model_config = ConfigDict(from_attributes=True)


class AdminProduct(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None
    category: Optional["Category"] = None
    brand: Optional["Brand"] = None
    images: List[Image] = []
    variants: List[AdminProductVariant] = []
    model_config = ConfigDict(from_attributes=True)


class AdminProductList(BaseModel):
    products: List[AdminProduct]
    total_count: int


# AdminOrder
class AdminOrderProductVariant(BaseModel):
    id: int
    sku: Optional[str]
    product: "AdminOrderProduct"
    attributes: List["AdminOrderVariantAttribute"] = []

    model_config = ConfigDict(from_attributes=True)


class AdminOrderProduct(BaseModel):
    id: int
    name: str
    images: List[Image] = []

    model_config = ConfigDict(from_attributes=True)


class AdminOrderAttribute(BaseModel):
    type: str
    value: str

    model_config = ConfigDict(from_attributes=True)


class AdminOrderVariantAttribute(BaseModel):
    attribute: AdminOrderAttribute

    model_config = ConfigDict(from_attributes=True)


class AdminOrderItem(BaseModel):
    id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    variant: AdminOrderProductVariant

    model_config = ConfigDict(from_attributes=True)


class AdminOrder(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    customer_name: str
    customer_phone: str
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_country: Optional[str] = None
    notes: Optional[str] = None
    created_at: dt.datetime
    updated_at: Optional[dt.datetime] = None
    shipped_at: Optional[dt.datetime] = None
    delivered_at: Optional[dt.datetime] = None
    items: List[AdminOrderItem] = []

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: models.OrderStatus