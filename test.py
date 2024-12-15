import requests
from bs4 import BeautifulSoup
import sqlite3

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        print("Статус відповіді сервера:", response.status_code)
        if response.status_code == 200:
            print("HTML отримано успішно!")
            return response.text
        else:
            print("Помилка отримання сторінки. Код статусу:", response.status_code)
            return None
    except Exception as e:
        print("Помилка запиту:", e)
        return None

def parse_products(html): # парсинг товаров
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    items = soup.find_all('div', class_='goods-tile')  # Клас для контейнера товару

    if not items:
        print("Товари не знайдені!")
        return products

    for item in items:
        title_tag = item.find('span', class_='goods-tile__title') # название товара
        title = title_tag.text.strip() if title_tag else 'Назва відсутня'

        price_tag = item.find('span', class_='goods-tile__price-value') # цена
        price = price_tag.text.strip().replace('\xa0', '') if price_tag else 'Ціна відсутня'

        rating_tag = item.find('span', class_='goods-tile__stars') # рейтинг
        rating = rating_tag.get('aria-label') if rating_tag else 'Рейтинг відсутній'

        products.append((title, price, rating))

    print(f"Кількість знайдених товарів: {len(products)}")

    return products

def save_to_db(data):  # сохранение данных в таблице
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apple_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price TEXT,
            rating TEXT
        )
    ''')

    cursor.executemany('INSERT INTO apple_products (name, price, rating) VALUES (?, ?, ?)', data)
    conn.commit()
    print("Дані успішно збережено у базу даних SQLite.")
    conn.close()


# Основний блок програми
if __name__ == '__main__':
    url = 'https://rozetka.com.ua/ua/mobile-phones/c80003/producer=apple/'
    html = get_html(url)

    if html:
        print("Розпочинаємо парсинг сторінки...")
        products = parse_products(html)

        if products:
            print("\n--- Знайдені товари ---")
            for product in products:
                print(product)

            save_to_db(products)
        else:
            print("Не вдалося знайти товари. Перевірте код або структуру сторінки.")
    else:
        print("Не вдалося завантажити сторінку. Завершення програми.")

