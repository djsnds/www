"use client";

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Product } from '@/lib/types';
import { toast } from 'sonner';

// Define the type for a single item in the cart
export type CartItem = {
  product: Product;
  size: string;
  quantity: number;
};

// Define the type for the context state and functions
interface CartContextType {
  cart: CartItem[];
  addToCart: (product: Product, size: string) => void;
  removeFromCart: (productId: number, size: string) => void;
  updateQuantity: (productId: number, size: string, quantity: number) => void;
  getCartTotal: () => number;
  getCartCount: () => number;
  clearCart: () => void;
}

// Create the context with a default undefined value
const CartContext = createContext<CartContextType | undefined>(undefined);

// Custom hook to use the cart context
export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

// Provider component
interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider = ({ children }: CartProviderProps) => {
  const [cart, setCart] = useState<CartItem[]>(() => {
    // Lazy initialization from localStorage
    if (typeof window === 'undefined') {
      return [];
    }
    try {
      const savedCart = window.localStorage.getItem('cart');
      return savedCart ? JSON.parse(savedCart) : [];
    } catch (error) {
      console.error("Failed to parse cart from localStorage", error);
      return [];
    }
  });

  useEffect(() => {
    // Persist cart to localStorage whenever it changes
    try {
      window.localStorage.setItem('cart', JSON.stringify(cart));
    } catch (error) {
      console.error("Failed to save cart to localStorage", error);
    }
  }, [cart]);

  const addToCart = (product: Product, size: string) => {
    setCart(prevCart => {
      const existingItemIndex = prevCart.findIndex(
        item => item.product.id === product.id && item.size === size
      );

      if (existingItemIndex > -1) {
        // Update quantity if item already exists
        const updatedCart = [...prevCart];
        updatedCart[existingItemIndex].quantity += 1;
        return updatedCart;
      } else {
        // Add new item to cart
        const newItem: CartItem = {
          product,
          size,
          quantity: 1,
        };
        return [...prevCart, newItem];
      }
    });
    toast.success(`${product.name} (${size}) добавлен в корзину.`);
  };

  const removeFromCart = (productId: number, size: string) => {
    setCart(prevCart => prevCart.filter(
      item => !(item.product.id === productId && item.size === size)
    ));
    toast.info("Товар удален из корзины.");
  };

  const updateQuantity = (productId: number, size: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId, size);
      return;
    }
    setCart(prevCart =>
      prevCart.map(item =>
        item.product.id === productId && item.size === size
          ? { ...item, quantity }
          : item
      )
    );
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => {
      const price = item.product.variants[0]?.price || 0;
      return total + price * item.quantity;
    }, 0);
  };

  const getCartCount = () => {
    return cart.reduce((count, item) => count + item.quantity, 0);
  };

  const clearCart = () => {
    setCart([]);
    // toast.info("Корзина очищена."); // Optional: uncomment if you want a toast message
  };

  const value = {
    cart,
    addToCart,
    removeFromCart,
    updateQuantity,
    getCartTotal,
    getCartCount,
    clearCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}; 