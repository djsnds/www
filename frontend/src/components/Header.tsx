"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { CartView } from './CartView';

const categories = [
  { name: "Men's Clothing", href: '/mens' },
  { name: "Women's Clothing", href: '/womens' },
  { name: 'Sneakers', href: '/sneakers' },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex gap-6 md:gap-10">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-lg font-bold">ACME Store</span>
          </Link>
          <nav className="hidden md:flex gap-6">
            {categories.map((category) => (
              <Link
                key={category.href}
                href={`${category.href}?page=1`}
                className={cn(
                  'text-sm font-medium transition-colors hover:text-primary',
                  pathname.startsWith(category.href) ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                {category.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center space-x-4">
          <CartView />
        </div>
      </div>
    </header>
  );
} 