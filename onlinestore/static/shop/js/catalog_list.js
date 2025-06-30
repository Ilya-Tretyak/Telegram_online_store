function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function showToast(message) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style = `
          visibility: hidden;
          min-width: 250px;
          background-color: #333;
          color: #fff;
          text-align: center;
          border-radius: 4px;
          padding: 16px;
          position: fixed;
          z-index: 9999;
          font-size: 17px;
          opacity: 0;
          transition: opacity 0.5s ease-in-out;
          box-shadow: 0 2px 10px rgba(0,0,0,0.3);
          top: 20px;
          left: 20px;
          max-width: 300px;
        `;

        // Мобильная адаптация
        const style = document.createElement('style');
        style.textContent = `
          @media (max-width: 768px) {
            #toast {
              top: 0 !important;
              left: 0 !important;
              width: 100% !important;
              border-radius: 0 !important;
              min-width: auto !important;
              padding: 12px 0 !important;
              font-size: 16px !important;
              box-shadow: none !important;
            }
          }
        `;
        document.head.appendChild(style);

        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.visibility = "visible";
    toast.style.opacity = "1";

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => {
            toast.style.visibility = "hidden";
        }, 500);
    }, 3000);
}

function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

// Инициализация счётчика корзины
updateCartCount(window.initialCartCount || 0);

document.querySelectorAll('.product-card').forEach(card => {
    const btnIncrease = card.querySelector('.quantity-btn:last-of-type');
    const btnDecrease = card.querySelector('.quantity-btn:first-of-type');
    const quantityCountEl = card.querySelector('.quantity-count');
    const buyButton = card.querySelector('.buy-button');

    let quantity = 1;
    quantityCountEl.textContent = quantity;

    btnIncrease.addEventListener('click', () => {
        quantity++;
        quantityCountEl.textContent = quantity;
    });

    btnDecrease.addEventListener('click', () => {
        if (quantity > 1) {
            quantity--;
            quantityCountEl.textContent = quantity;
        }
    });

    buyButton.addEventListener('click', () => {
        // Предполагаем, что у карточки есть data-product-id, если нет - нужно добавить в HTML
        const productId = card.getAttribute('data-product-id');
        if (!productId) {
            console.error('Не найден product-id у товара');
            showToast('Ошибка: Не удалось определить товар.');
            return;
        }

        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({quantity: quantity})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast(data.message + `. Сейчас в корзине: ${data.quantity} шт.`);
                updateCartCount(data.quantity);
                // Сбросить количество в карточке к 1
                quantity = 1;
                quantityCountEl.textContent = quantity;
            } else {
                showToast('Ошибка при добавлении товара в корзину.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showToast('Произошла ошибка при добавлении товара в корзину.');
        });
    });
});



