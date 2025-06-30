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

let quantity = 1;

const quantityCountEl = document.getElementById('quantity-count');
const btnIncrease = document.getElementById('quantity-increase');
const btnDecrease = document.getElementById('quantity-decrease');
const addToCartBtn = document.getElementById('add-to-cart');
const toast = document.getElementById("toast");

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

function showToast(message) {
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

// Инициализация счётчика корзины из шаблона
updateCartCount(window.initialCartCount || 0);

addToCartBtn.addEventListener('click', () => {
    const productId = addToCartBtn.getAttribute('data-product-id');

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
        } else {
            showToast('Ошибка при добавлении товара в корзину.');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showToast('Произошла ошибка при добавлении товара в корзину.');
    });
});

