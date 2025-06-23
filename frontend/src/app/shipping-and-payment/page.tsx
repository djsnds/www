export default function ShippingAndPaymentPage() {
  return (
    <div className="container mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-4xl font-bold tracking-tight mb-8">Доставка и оплата</h1>
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold mb-3">ДОСТАВКА ПО РОССИИ</h2>
          <div className="prose max-w-none text-muted-foreground">
            <ul className="list-disc pl-5 space-y-2">
              <li>Доставку в регионы России осуществляем Почтой России, СДЭК или другими удобными для вас транспортными компаниями.</li>
              <li>Стоимость доставки по России — 400 рублей.</li>
              <li>Также отправляем Авито-доставкой.</li>
            </ul>
          </div>
        </div>
        <div>
          <h2 className="text-2xl font-semibold mb-3">ОПЛАТА</h2>
          <div className="prose max-w-none text-muted-foreground">
            <p>
              Доставку в другие города осуществляем после 100% предоплаты. Если вы сомневаетесь в нашей порядочности, можем отправить товар через Авито-доставку (Безопасная сделка).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 