"use client";

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { CartItem } from '@/lib/types';
import { toast } from 'sonner';

// Define the type for the context state and functions
interface CartContextType {
  cart: CartItem[];
  addToCart: (item: CartItem) => void;
  removeFromCart: (variantId: number) => void;
  updateQuantity: (variantId: number, quantity: number) => void;
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

  const addToCart = (newItem: CartItem) => {
    setCart(prevCart => {
      const existingItemIndex = prevCart.findIndex(
        item => item.id === newItem.id
      );

      let updatedCart;
      if (existingItemIndex > -1) {
        updatedCart = [...prevCart];
        const existingItem = updatedCart[existingItemIndex];
        const newQuantity = existingItem.quantity + newItem.quantity;
        
        if (newQuantity > existingItem.stock) {
          toast.error(`Нельзя добавить больше, чем есть в наличии (${existingItem.stock} шт.)`);
          return prevCart;
        }
        
        updatedCart[existingItemIndex].quantity = newQuantity;
      } else {
        if (newItem.quantity > newItem.stock) {
          toast.error(`Нельзя добавить больше, чем есть в наличии (${newItem.stock} шт.)`);
          return prevCart;
        }
        updatedCart = [...prevCart, newItem];
      }
      toast.success(`${newItem.name} (${newItem.size}) добавлен в корзину.`);
      return updatedCart;
    });
  };

  const removeFromCart = (variantId: number) => {
    setCart(prevCart => prevCart.filter(item => item.id !== variantId));
    toast.info("Товар удален из корзины.");
  };

  const updateQuantity = (variantId: number, quantity: number) => {
    setCart(prevCart =>
      prevCart.map(item => {
        if (item.id === variantId) {
          if (quantity <= 0) {
            // This will be handled by the filter in the return statement
            return null; 
          }
          if (quantity > item.stock) {
            toast.error(`Нельзя заказать больше, чем есть в наличии (${item.stock} шт.)`);
            return item;
          }
          return { ...item, quantity };
        }
        return item;
      }).filter(Boolean) as CartItem[]
    );
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => total + item.price * item.quantity, 0);
  };

  const getCartCount = () => {
    return cart.reduce((count, item) => count + item.quantity, 0);
  };

  const clearCart = () => {
    setCart([]);
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