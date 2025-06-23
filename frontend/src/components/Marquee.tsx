import { cn } from "@/lib/utils";

// An icon to be used as a separator
const DiamondIcon = ({ className }: { className?: string }) => (
  <svg
    width="15"
    height="15"
    viewBox="0 0 15 15"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn("h-3 w-3", className)}
  >
    <path
      d="M7.49991 0.877045L14.1228 7.5L7.49991 14.1228L0.877014 7.5L7.49991 0.877045Z"
      fill="currentColor"
    />
  </svg>
);

// New content configuration with more colors
const marqueeItems = [
  { text: "Лимитированные релизы", color: "text-red-400" },
  { text: "Стиль в каждом шаге", color: "text-amber-400" },
  { text: "Экспресс-доставка", color: "text-lime-400" },
  { text: "Только оригиналы", color: "text-cyan-400" },
  { text: "Новая коллекция", color: "text-fuchsia-400" },
  { text: "Гарантия качества", color: "text-white" },
];

const MarqueeContent = () => (
  <>
    {marqueeItems.map((item, index) => (
      <div key={index} className="mx-6 flex items-center justify-center gap-6">
        <p className={cn("text-sm font-medium", item.color)}>{item.text}</p>
        <DiamondIcon className="text-neutral-600" />
      </div>
    ))}
  </>
);

export function Marquee() {
  return (
    <div className="relative flex h-10 w-full flex-row items-center overflow-hidden bg-neutral-900 border-b border-neutral-800">
      <div className="animate-marquee flex min-w-full shrink-0 items-center justify-around">
        <MarqueeContent />
      </div>
       <div className="animate-marquee2 absolute flex min-w-full shrink-0 items-center justify-around">
        <MarqueeContent />
      </div>
    </div>
  );
} 