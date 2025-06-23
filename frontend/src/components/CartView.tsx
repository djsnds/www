"use client";

import Image from 'next/image';
import { useCart } from "@/context/CartContext";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import {
  Sheet,
  SheetContent,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckoutForm } from "./CheckoutForm";
import { useState, useEffect } from "react";
import { ShoppingCart, Minus, Plus, Trash2 } from 'lucide-react';

export function CartView() {
  const { cart, updateQuantity, removeFromCart, getCartTotal, getCartCount } = useCart();
  const [isSheetOpen, setSheetOpen] = useState(false);
  const [isDialogOpen, setDialogOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleCheckoutSuccess = () => {
    setSheetOpen(false);
    setDialogOpen(false);
  };

  const cartCount = getCartCount();

  return (
    <Sheet open={isSheetOpen} onOpenChange={setSheetOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="relative">
          <ShoppingCart className="h-5 w-5" />
          {isMounted && cartCount > 0 && (
            <span className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
              {cartCount}
            </span>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent className="flex flex-col sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>Корзина</SheetTitle>
        </SheetHeader>
        <Separator />
        {cart.length > 0 ? (
          <>
            <ScrollArea className="flex-grow pr-4">
              <div className="space-y-6">
                {cart.map((item) => {
                  const imageUrl = 
                    item.image
                      ? `/products/${item.image}` 
                      : 'https://placehold.co/600x400/EEE/31343C?text=No+Image';

                  return (
                    <div key={item.id} className="flex items-start gap-4">
                      <Image
                        src={imageUrl}
                        alt={item.name}
                        width={80}
                        height={100}
                        className="object-cover rounded-md"
                      />
                      <div className="flex-1">
                        <h3 className="font-semibold">{item.name}</h3>
                        <p className="text-sm text-muted-foreground">Размер: {item.size}</p>
                        <p className="text-sm">
                          {item.price.toFixed(2)} руб.
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          >
                            <Minus className="h-4 w-4" />
                          </Button>
                          <span>{item.quantity}</span>
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          >
                            <Plus className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground"
                        onClick={() => removeFromCart(item.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
            <Separator />
            <SheetFooter>
              <div className="w-full space-y-4">
                <div className="flex justify-between font-bold text-lg">
                  <span>Итого:</span>
                  <span>{getCartTotal().toFixed(2)} руб.</span>
                </div>
                <Dialog open={isDialogOpen} onOpenChange={setDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full">Оформить заказ</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Оформление заказа</DialogTitle>
                    </DialogHeader>
                    <CheckoutForm setOpen={handleCheckoutSuccess} />
                  </DialogContent>
                </Dialog>
              </div>
            </SheetFooter>
          </>
        ) : (
          <div className="flex-grow flex items-center justify-center">
            <p>Ваша корзина пуста.</p>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
} 