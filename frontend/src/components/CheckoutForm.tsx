"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { useCart, CartItem } from "@/context/CartContext";
import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";

const formSchema = z.object({
    name: z.string().min(2, "Имя должно содержать не менее 2 символов."),
    phone: z.string().min(10, "Неверный формат номера телефона."),
    deliveryMethod: z.enum(["pickup", "delivery"], {
      required_error: "Необходимо выбрать способ доставки.",
    }),
    address: z.string().optional(),
    contactMethod: z.array(z.string()).refine((value) => value.some((item) => item), {
      message: "Необходимо выбрать хотя бы один способ связи.",
    }),
    privacyPolicy: z.boolean().refine((value) => value === true, {
      message: "Необходимо согласиться с политикой конфиденциальности.",
    }),
  }).refine((data) => {
    if (data.deliveryMethod === "delivery") {
      return data.address && data.address.length > 0;
    }
    return true;
  }, {
    message: "Адрес доставки обязателен при выборе доставки.",
    path: ["address"],
  });

interface CheckoutFormProps {
  setOpen: (open: boolean) => void;
}

export function CheckoutForm({ setOpen }: CheckoutFormProps) {
  const { cart, clearCart, getCartTotal } = useCart();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      phone: "",
      deliveryMethod: "pickup",
      address: "",
      contactMethod: [],
      privacyPolicy: false,
    },
  });

  const deliveryMethod = form.watch("deliveryMethod");

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsSubmitting(true);
    try {
      const orderDetails = {
        ...values,
        cart: cart.map((item: CartItem) => ({
          productId: item.product.id,
          name: item.product.name,
          size: item.size,
          quantity: item.quantity,
          price: item.product.variants[0]?.price || 0,
        })),
        totalPrice: getCartTotal(),
      };

      const response = await fetch('http://127.0.0.1:8000/api/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderDetails),
      });

      if (response.ok) {
        toast.success("Спасибо за ваш заказ!", {
          description: "Наш менеджер свяжется с вами в ближайшее время.",
        });
        clearCart();
        setOpen(false);
      } else {
        const errorData = await response.json();
        console.error("Ошибка при оформлении заказа:", errorData);
        toast.error("Не удалось оформить заказ. Пожалуйста, попробуйте еще раз.");
      }
    } catch (error) {
      console.error("Сетевая ошибка или ошибка в запросе:", error);
      toast.error("Произошла ошибка. Пожалуйста, проверьте ваше соединение и попробуйте снова.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const contactMethods = [
    { id: "whatsapp", label: "WhatsApp" },
    { id: "telegram", label: "Telegram" },
    { id: "call", label: "Звонок" },
  ];

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Имя</FormLabel>
              <FormControl>
                <Input placeholder="Иван" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Телефон</FormLabel>
              <FormControl>
                <Input placeholder="+7 (999) 123-45-67" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="deliveryMethod"
          render={({ field }) => (
            <FormItem className="space-y-3">
              <FormLabel>Способ доставки</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex flex-col space-y-1"
                >
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="pickup" />
                    </FormControl>
                    <FormLabel className="font-normal">Самовывоз</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="delivery" />
                    </FormControl>
                    <FormLabel className="font-normal">Доставка по России</FormLabel>
                  </FormItem>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {deliveryMethod === "delivery" && (
          <FormField
            control={form.control}
            name="address"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Город доставки</FormLabel>
                <FormControl>
                  <Input placeholder="Москва" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}
        <FormField
          control={form.control}
          name="contactMethod"
          render={() => (
            <FormItem>
              <div className="mb-4">
                <FormLabel>Способ связи</FormLabel>
              </div>
              {contactMethods.map((item) => (
                <FormField
                  key={item.id}
                  control={form.control}
                  name="contactMethod"
                  render={({ field }) => {
                    return (
                      <FormItem
                        key={item.id}
                        className="flex flex-row items-start space-x-3 space-y-0"
                      >
                        <FormControl>
                          <Checkbox
                            checked={field.value?.includes(item.id)}
                            onCheckedChange={(checked: boolean) => {
                              return checked
                                ? field.onChange([...(field.value || []), item.id])
                                : field.onChange(
                                    field.value?.filter(
                                      (value) => value !== item.id
                                    )
                                  );
                            }}
                          />
                        </FormControl>
                        <FormLabel className="font-normal">
                          {item.label}
                        </FormLabel>
                      </FormItem>
                    );
                  }}
                />
              ))}
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
            control={form.control}
            name="privacyPolicy"
            render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                        <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                        />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                        <FormLabel>
                            Я согласен с <Link href="/privacy-policy" className="underline hover:text-primary">политикой конфиденциальности</Link>
                        </FormLabel>
                    </div>
                </FormItem>
            )}
        />
        <FormMessage>{form.formState.errors.privacyPolicy?.message}</FormMessage>

        <Button type="submit" disabled={isSubmitting || cart.length === 0} className="w-full">
          {isSubmitting ? "Обработка..." : `Подтвердить заказ на ${getCartTotal().toFixed(2)} руб.`}
        </Button>
      </form>
    </Form>
  );
} 