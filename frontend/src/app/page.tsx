import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function HomePage() {
  return (
    <section className="container flex flex-col items-center justify-center text-center py-20 md:py-32">
      <h1 className="text-4xl md:text-6xl font-bold tracking-tighter mb-4">
        Discover Your Style
      </h1>
      <p className="max-w-2xl text-lg text-muted-foreground mb-8">
        Explore our curated collection of high-quality clothing and sneakers. Find the perfect pieces to express yourself.
      </p>
      <div className="flex flex-wrap justify-center gap-4">
        <Button asChild size="lg">
          <Link href="/men-clothing">Men's Collection</Link>
        </Button>
        <Button asChild size="lg" variant="secondary">
          <Link href="/women-clothing">Women's Collection</Link>
        </Button>
        <Button asChild size="lg" variant="outline">
          <Link href="/sneakers">Shop Sneakers</Link>
        </Button>
      </div>
    </section>
  );
} 