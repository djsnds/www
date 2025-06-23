import Link from 'next/link';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-neutral-900 text-neutral-300 mt-16">
      <div className="container mx-auto px-4 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-sm">
          {/* About Section */}
          <div>
            <h3 className="text-base font-semibold text-white mb-4">Sneaker Shop</h3>
            <p className="text-neutral-400">
              Ваш источник лучших и самых стильных кроссовок. Мы предлагаем кураторский выбор от ведущих брендов для настоящих ценителей.
            </p>
          </div>

          {/* Links Section */}
          <div>
            <h3 className="text-base font-semibold text-white mb-4">Информация</h3>
            <ul className="space-y-2">
              <li><Link href="/about-us" className="hover:text-white transition-colors">О нас</Link></li>
              <li><Link href="/shipping-and-payment" className="hover:text-white transition-colors">Доставка и оплата</Link></li>
              <li><Link href="/privacy-policy" className="hover:text-white transition-colors">Политика конфиденциальности</Link></li>
            </ul>
          </div>

          {/* Contacts Section */}
          <div>
            <h3 className="text-base font-semibold text-white mb-4">Контакты</h3>
            <ul className="space-y-2 text-neutral-400">
              <li>ИП Пласкогубцев Степан Степанович</li>
              <li><a href="tel:+79777777777" className="hover:text-white transition-colors">Телефон: 8 (977) 777-77-77</a></li>
              <li><a href="https://wa.me/79777777777" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">WhatsApp</a></li>
              <li><a href="https://t.me/sdnsjd" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Telegram: @sdnsjd</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-neutral-800 text-center text-xs text-neutral-500">
          <p>&copy; {currentYear} Sneaker Shop. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
} 