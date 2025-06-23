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
import { useCart } from "@/context/CartContext";
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
      privacyPolicy: false,
    },
  });

  const deliveryMethod = form.watch("deliveryMethod");

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsSubmitting(true);
    try {
      const orderPayload = {
        name: values.name,
        phone: values.phone,
        shipping_city: values.address || "Самовывоз",
        cart: cart.map((item) => ({
          ProductVariantId: item.id,
          quantity: item.quantity,
        })),
      };

      const response = await fetch('http://127.0.0.1:8000/api/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderPayload),
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
                  Я согласен с {" "}
                  <Link href="/privacy-policy" className="underline" target="_blank">
                    политикой конфиденциальности
                  </Link>
                </FormLabel>
              </div>
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Оформление..." : "Оформить заказ"}
        </Button>
      </form>
    </Form>
  );
} 