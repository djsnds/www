"use client";

import { useState } from 'react';
import Image from 'next/image';
import { Product } from '@/lib/types';
import { Button } from '@/components/ui/button';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useCart } from '@/context/CartContext';
import { toast } from 'sonner';
import { CartItem } from '@/lib/types';

interface ProductViewProps {
  product: Product | null;
}

export function ProductView({ product }: ProductViewProps) {
  const { addToCart } = useCart();
  const [selectedSize, setSelectedSize] = useState<string | null>(null);

  if (!product) {
    return <div>Загрузка информации о товаре...</div>;
  }

  const price = product.variants?.[0]?.price;

  const handleAddToCart = () => {
    if (!selectedSize) {
      toast.error("Пожалуйста, выберите размер.");
      return;
    }
    const selectedVariant = product.variants.find(
      (variant) => variant.attributes.some(
        (attr) => attr.attribute.type === 'size' && attr.attribute.value === selectedSize
      )
    );
    if (selectedVariant && selectedVariant.stock > 0) {
      const cartItem: CartItem = {
        id: selectedVariant.id,
        name: product.name,
        price: selectedVariant.price,
        quantity: 1,
        image: product.images?.[0]?.url ?? '',
        size: selectedSize,
        sku: selectedVariant.sku,
        stock: selectedVariant.stock,
      };
      addToCart(cartItem);
    } else {
      toast.error("Выбранный размер не доступен.");
    }
  };

  return (
    <div className="grid md:grid-cols-2 gap-8">
      <div className="relative">
        <Carousel>
          <CarouselContent>
            {product.images && product.images.length > 0 ? (
              product.images.map((image, index) => (
                <CarouselItem key={index}>
                  <Image
                    src={`/products/${image.url}`}
                    alt={`${product.name} image ${index + 1}`}
                    width={600}
                    height={600}
                    className="w-full h-auto object-cover rounded-lg"
                    priority={index === 0}
                  />
                </CarouselItem>
              ))
            ) : (
              <CarouselItem>
                <Image
                  src={'https://placehold.co/600x400/EEE/31343C?text=No+Image'}
                  alt="No image available"
                  width={600}
                  height={600}
                  className="w-full h-auto object-cover rounded-lg"
                />
              </CarouselItem>
            )}
          </CarouselContent>
          <CarouselPrevious className="absolute left-2 top-1/2 -translate-y-1/2" />
          <CarouselNext className="absolute right-2 top-1/2 -translate-y-1/2" />
        </Carousel>
      </div>
      <div>
        <h1 className="text-3xl font-bold">{product.name}</h1>
        {product.description && <p className="text-muted-foreground mt-2">{product.description}</p>}
        {price !== undefined && (
          <p className="text-2xl font-semibold mt-4">{price.toFixed(2)} руб.</p>
        )}
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-900">Выберите размер</h3>
          <RadioGroup
            value={selectedSize ?? ""}
            onValueChange={setSelectedSize}
            className="mt-2 flex flex-wrap gap-2"
          >
            {product.variants.map((variant) => {
              const sizeAttr = variant.attributes.find(
                (attr) => attr.attribute.type === "size"
              );
              if (!sizeAttr) return null;

              const size = sizeAttr.attribute.value;
              const isInStock = variant.stock > 0;

              return (
                <div key={size} className="flex items-center">
                  <RadioGroupItem
                    value={size}
                    id={`size-${size}`}
                    disabled={!isInStock}
                  />
                  <Label
                    htmlFor={`size-${size}`}
                    className={`ml-2 ${
                      !isInStock
                        ? "cursor-not-allowed text-muted-foreground"
                        : "cursor-pointer"
                    }`}
                  >
                    {size}
                  </Label>
                </div>
              );
            })}
          </RadioGroup>
        </div>
        <Button onClick={handleAddToCart} disabled={!selectedSize} className="mt-6 w-full">
          {selectedSize ? 'Добавить в корзину' : 'Выберите размер'}
        </Button>
      </div>
    </div>
  );
} 