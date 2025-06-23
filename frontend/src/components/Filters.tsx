"use client";

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { ChevronDown } from 'lucide-react';
import { Brand, SubCategory } from '@/lib/types';

interface FiltersProps {
  brands: Brand[];
  sizes: string[];
  subcategories?: SubCategory[];
}

export function Filters({ brands, sizes, subcategories = [] }: FiltersProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const handleSortChange = (value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value === 'default') {
      params.delete('sort_by');
    } else {
      params.set('sort_by', value);
    }
    params.set('page', '1');
    router.push(`${pathname}?${params.toString()}`);
  };

  const handleFilterChange = (
    type: 'brands' | 'sizes' | 'subcategory_slugs',
    value: string,
    checked: boolean
  ) => {
    const params = new URLSearchParams(searchParams);
    let currentValues = params.getAll(type);

    if (checked) {
      currentValues.push(value);
    } else {
      currentValues = currentValues.filter((v) => v !== value);
    }

    params.delete(type);

    if (currentValues.length > 0) {
      currentValues.forEach((val) => params.append(type, val));
    }

    params.set('page', '1');
    router.push(`${pathname}?${params.toString()}`);
  };

  const sortOptions = [
    { value: 'price_asc', label: 'Price: Low to High' },
    { value: 'price_desc', label: 'Price: High to Low' },
    { value: 'name_asc', label: 'Name: A to Z' },
    { value: 'name_desc', label: 'Name: Z to A' },
  ];

  const currentSort = searchParams.get('sort_by') || 'default';
  
  const selectedBrands = searchParams.getAll('brands');
  const selectedSizes = searchParams.getAll('sizes');
  const selectedSubcategories = searchParams.getAll('subcategory_slugs');

  return (
    <div className="flex flex-wrap items-center gap-4">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">
            Brand <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Filter by Brand</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {brands.map((brand) => (
            <DropdownMenuCheckboxItem
              key={brand.slug}
              checked={selectedBrands.includes(brand.slug)}
              onCheckedChange={(checked) => handleFilterChange('brands', brand.slug, !!checked)}
            >
              {brand.name}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">
            Size <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Filter by Size</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {sizes.map((size) => (
            <DropdownMenuCheckboxItem
              key={size}
              checked={selectedSizes.includes(size)}
              onCheckedChange={(checked) => handleFilterChange('sizes', size, !!checked)}
            >
              {size}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {subcategories && subcategories.length > 0 && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              Category <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuLabel>Filter by Category</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {subcategories.map((subcategory) => (
              <DropdownMenuCheckboxItem
                key={subcategory.slug}
                checked={selectedSubcategories.includes(subcategory.slug)}
                onCheckedChange={(checked) =>
                  handleFilterChange('subcategory_slugs', subcategory.slug, !!checked)
                }
              >
                {subcategory.name}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      <div className="flex items-center gap-2">
        <Label htmlFor="sort-by" className="text-sm font-medium">
          Sort by
        </Label>
        <Select onValueChange={handleSortChange} value={currentSort}>
          <SelectTrigger id="sort-by" className="w-[180px]">
            <SelectValue placeholder="Default" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="default">Default</SelectItem>
            {sortOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
} 