"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useParams, useRouter } from 'next/navigation';
import { ProductGrid } from '@/components/ProductGrid';
import { Filters } from '@/components/Filters';
import { Pagination } from '@/components/Pagination';
import { Product, Brand, SubCategory } from '@/lib/types';
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from '@/components/ui/dialog';
import { ProductView } from '@/components/ProductView';
import { VisuallyHidden } from '@radix-ui/react-visually-hidden';
import { Skeleton } from '@/components/ui/skeleton';

const categoryTitles: Record<string, string> = {
  'men-clothing': "Men's Clothing",
  'women-clothing': "Women's Clothing",
  'sneakers': 'Sneakers',
};

function CategoryPageContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const categoryParam = Array.isArray(params.category) ? params.category[0] : params.category;
  const category = categoryParam as 'men-clothing' | 'women-clothing' | 'sneakers';

  const [products, setProducts] = useState<Product[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [availableBrands, setAvailableBrands] = useState<Brand[]>([]);
  const [availableSizes, setAvailableSizes] = useState<string[]>([]);
  const [availableSubcategories, setAvailableSubcategories] = useState<SubCategory[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!category || !categoryTitles[category]) return;

    const fetchProducts = async () => {
      setIsLoading(true);
      setError(null);
      const limit = 12;
      try {
        const page = parseInt(searchParams.get('page') || '1', 10);
        const skip = (page - 1) * limit;

        const query = new URLSearchParams(searchParams.toString());
        query.set('category_slug', category);
        query.set('limit', limit.toString());
        query.set('skip', skip.toString());
        
        const response = await fetch(`http://127.0.0.1:8000/api/products?${query.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch products');
        const data = await response.json();
        
        setProducts(data.products);
        setTotalPages(Math.ceil(data.total_count / limit));
        setCurrentPage(page);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'An unknown error occurred.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProducts();
  }, [searchParams, category]);

  useEffect(() => {
    if (!category || !categoryTitles[category]) return;

    const fetchFilters = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/products/filters?category_slug=${category}`);
        if (!response.ok) throw new Error('Failed to fetch filters');
        const data = await response.json();
        setAvailableBrands(data.brands);
        setAvailableSizes(data.sizes);
        setAvailableSubcategories(data.subcategories);
      } catch (error) {
        console.error("Filter fetch error:", error);
      }
    };

    fetchFilters();
  }, [category]);

  if (!category || !categoryTitles[category]) {
    // You might want to navigate to a 404 page instead
    router.push('/404');
    return null;
  }

  const handleCardClick = (product: Product) => setSelectedProduct(product);
  const handleModalClose = () => setSelectedProduct(null);

  return (
    <>
      <div className="container my-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            {categoryTitles[category]}
          </h1>
          <Filters
            brands={availableBrands}
            sizes={availableSizes}
            subcategories={availableSubcategories}
          />
        </div>
        
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-64 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-16 text-red-500">
            <h2 className="text-2xl font-semibold">Error loading products</h2>
            <p className="text-muted-foreground mt-2">{error}</p>
          </div>
        ) : products.length > 0 ? (
          <>
            <ProductGrid products={products} onCardClick={handleCardClick} />
            <Pagination currentPage={currentPage} totalPages={totalPages} />
          </>
        ) : (
          <div className="text-center py-16">
            <h2 className="text-2xl font-semibold">No products found</h2>
            <p className="text-muted-foreground mt-2">
              Try adjusting your filters or check back later.
            </p>
          </div>
        )}
      </div>

      <Dialog open={!!selectedProduct} onOpenChange={handleModalClose}>
        <DialogContent className="max-w-4xl">
          {selectedProduct && (
            <>
              <DialogTitle asChild>
                <VisuallyHidden>
                  <h2>{selectedProduct.name}</h2>
                </VisuallyHidden>
              </DialogTitle>
              <ProductView product={selectedProduct} />
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

export default function CategoryPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CategoryPageContent />
    </Suspense>
  );
} 