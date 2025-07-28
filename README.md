# 🛍️ Telegram Shop

**Онлайн-магазин с Telegram-ботом и Django MiniApp**  
Полноценное ecommerce-решение, включающее:
- Telegram-бот на `aiogram 3`
- Мини-приложение (MiniApp) на `Django`, интегрированное в Telegram через WebApp
- Поддержка онлайн-оплаты, уведомлений и аналитики

---

## 📌 О проекте
### 🧑‍💻 Для клиентов
  Бот и мини-приложение предоставляют пользователю единый и интуитивный интерфейс:
  - Переход в MiniApp для просмотра каталога
  - Добавления товара в избранное
  - Добавление товара в корзину
  - Оформление заказа
  - Онлайн-оплата прямо в Telegram
  - Уведомления о статусах заказа



### 👨‍💼 Для администраторов
  - Уведомления о новых заказах в боте
  - Панель управления заказами с 4 статусами
  - Управление каталогом (через Django-админку)
  - Связь заказов с Telegram-пользователями



---

## 🏗 Структура проекта 
```text
├── onlinestore/
│   ├── api/                    # Django-приложение MiniApp
│   ├── bot/                    # Telegram-бот
|   ├── media/                  # Загруженные изображения товаров
│   ├── onlinestore/            # Настройки Django
│   ├── shop/                   # Бизнес-логика магазина
|   ├── static/                 # Загруженные изображения товаров
|   ├── manage.py
│   └── requirements.txt
└── README.md                   # Документация проекта
```

## ⚙️ Технологический стек

<p align="center"> 
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python"> 
  <img src="https://img.shields.io/badge/Aiogram-3.0-blue?logo=telegram" alt="Aiogram"> 
  <img src="https://img.shields.io/badge/Django-4.2-green?logo=django" alt="Django"> 
  <img src="https://img.shields.io/badge/PostgreSQL-14-blue?logo=postgresql" alt="PostgreSQL"> 
  <img src="https://img.shields.io/badge/Telegram%20Bot%20API-WebApp-blue?logo=telegram" alt="Telegram WebApp"> 
</p>

---

## Демонстрация

📸 Демонстрация интерфейса
<div align="center">
  <table>
    <tr> 
      <td align="center"> <img src="img_for_github/1.png" width="300"></td> 
      <td align="center"> <img src="img_for_github/2.png" width="300"></td> 
    </tr> 
    <tr> 
      <td align="center"> <img src="img_for_github/3.png" width="300"></td>
      <td align="center"> <img src="img_for_github/4.png" width="300"></td>
    </tr>
    <tr> 
      <td align="center"> <img src="img_for_github/5.png" width="300"></td> 
      <td align="center"> <img src="img_for_github/6.png" width="300"></td> 
    </tr> 
    <tr> 
      <td align="center"> <img src="img_for_github/7.png" width="300"></td>
      <td align="center"> <img src="img_for_github/8.png" width="300"></td>
    </tr>
    <tr> 
      <td align="center"> <img src="img_for_github/9.png" width="300"></td>
      <td align="center"> <img src="img_for_github/10.png" width="300"></td> 
    </tr> 
  </table> 
</div>
