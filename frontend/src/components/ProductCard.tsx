import Image from 'next/image';
import { Product } from '@/lib/types';
import {
  Card,
  CardContent,
  CardHeader,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface ProductCardProps {
  product: Product;
  className?: string;
  onCardClick: (product: Product) => void;
}

export function ProductCard({ product, className, onCardClick }: ProductCardProps) {
  const price = product.variants[0]?.price;

  return (
    <Card 
      className={cn('w-full max-w-sm cursor-pointer overflow-hidden transition-shadow duration-300 hover:shadow-xl', className)}
      onClick={() => onCardClick(product)}
    >
      <CardHeader className="p-0">
        <div className="relative aspect-[4/5] w-full">
          <Image
            src={product.images && product.images.length > 0 ? product.images[0].url : 'https://placehold.co/600x400/EEE/31343C?text=No+Image'}
            alt={product.name}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            priority
          />
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <h3 className="text-lg font-semibold truncate">{product.name}</h3>
        <p className="text-sm text-muted-foreground">{product.brand?.name}</p>
        {price !== undefined && (
          <p className="mt-2 text-lg font-bold">${price.toFixed(2)}</p>
        )}
      </CardContent>
    </Card>
  );
} 