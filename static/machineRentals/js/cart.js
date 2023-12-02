function addToCart(id, quantity, products) {
    let cart = JSON.parse(localStorage.getItem('cart'));
    if (cart == null) {
        cart = [];
    }
    let item = cart.find(function (element) {
        return element.id == id;
    });
    if (item == null) {
        cart.push({id: id, quantity: quantity});
    } else {
        item.quantity += quantity;
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartSummary(products);
    addSummary();
}

function removeFromCart(id, quantity, products) {
    let cart = JSON.parse(localStorage.getItem('cart'));
    if (cart == null) {
        cart = [];
    }
    let item = cart.find(function (element) {
        return element.id == id;
    });
    if (item != null) {
        item.quantity -= quantity;
        if (item.quantity <= 0) {
            cart.splice(cart.indexOf(item), 1);
        }
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartSummary(products);
    addSummary();
}

function deleteItemFromCart(id, products) {
    let cart = JSON.parse(localStorage.getItem('cart'));
    if (cart == null) {
        cart = [];
    }
    let item = cart.find(function (element) {
        return element.id == id;
    });
    if (item != null) {
        cart.splice(cart.indexOf(item), 1);
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartSummary(products);
    addSummary();
}

// update cart summary in local storage in the format {subtotal: 100, shipping: 10}
function updateCartSummary(products) {
    let cart = JSON.parse(localStorage.getItem('cart'));
    if (cart == null) {
        cart = [];
    }
    let subtotal = 0;
    let shipping = 0;
    cart.forEach(function (item) {
        let product = products.find(function (element) {
            return element.id == item.id;
        });
        subtotal += product.price * item.quantity;
        shipping += product.shipping * item.quantity;
    });
    let cartSummary = {subtotal: subtotal, shipping: shipping};
    localStorage.setItem('cartSummary', JSON.stringify(cartSummary));
}

function addSummary() {
    const cartSummaryElm = document.getElementById('cart-summary');
    if (cartSummaryElm == null) return;
    let cartSummary = localStorage.getItem('cartSummary');
    cartSummary = JSON.parse(cartSummary) || {};
    cartSummaryElm.innerHTML = `
            <div class="border-bottom pb-2">
            <div class="d-flex justify-content-between mb-3">
                <h6>Subtotal</h6>
                <h6>$${cartSummary.subtotal || "0.00"}</h6>
            </div>
            <div class="d-flex justify-content-between">
                <h6 class="font-weight-medium">Shipping</h6>
                <h6 class="font-weight-medium">$${cartSummary.shipping || "0.00"}</h6>
            </div>
        </div>
        <div class="pt-2">
            <div class="d-flex justify-content-between mt-2">
                <h5>Total</h5>
                <h5>$${cartSummary.subtotal + cartSummary.shipping || "0.00"}</h5>
            </div>
            <button class="btn btn-block btn-primary font-weight-bold my-3 py-3">Proceed To Checkout</button>
        </div>
    `;
}