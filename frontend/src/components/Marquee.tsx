import { cn } from "@/lib/utils";

export function Marquee() {
  const textStyles = "bg-gradient-to-r from-pink-500 via-red-500 to-yellow-500 bg-clip-text text-transparent";

  return (
    <div className="relative flex h-10 w-full flex-row items-center justify-center overflow-hidden bg-gray-900 text-primary-foreground border-b border-gray-700">
      <div className={cn(
          "animate-marquee flex min-w-full shrink-0 items-center justify-around",
          "motion-reduce:animate-none"
        )}>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>Free Shipping on orders over 100$</p>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>100% authentic products</p>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>30-day return policy</p>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>Secure payments</p>
      </div>
       <div className={cn(
          "animate-marquee2 absolute flex min-w-full shrink-0 items-center justify-around",
          "motion-reduce:animate-none"
        )}>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>Free Shipping on orders over 100$</p>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>100% authentic products</p>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>30-day return policy</p>
        <p className={cn("mx-4 text-sm font-semibold", textStyles)}>Secure payments</p>
      </div>
    </div>
  )
} 