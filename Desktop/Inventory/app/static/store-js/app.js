jQuery(document).ready(function() {
    "use strict";
    /*  Menu */
    var carts = [];
    var toLoad = localStorage.getItem("carts");
    if (toLoad) {
        carts = JSON.parse(toLoad);
        refreshCartContent();
    }
    
    var hulla = new hullabaloo();
    $('.cart-clear').click(function(){
        localStorage.removeItem('carts');
        carts = [];
        refreshCartContent();
    });

    $('.btn-cart').click(function () {
        var id      = this.getAttribute('data-id');
        var name    = this.getAttribute('data-name');
        var image   = this.getAttribute('data-image');
        var price   = this.getAttribute('data-price');
        var alreadyPurchased = false;
        carts.forEach(item => {
            if (item.id == id) {
                item.count ++ ;
                alreadyPurchased = true;
            }
        });
        
        if (!alreadyPurchased) {
            carts.push({id: id, name: name, image: image, price: price, count: 1});
        }
        
        refreshCartContent();
        
        hulla.send("Succesfully added to cart", "success");

    });

    $('#cart-sidebar').on('click', '.remove-cart', function () {
        carts.splice(this.getAttribute('data-id'), 1);
        refreshCartContent();
        hulla.send("Succesfully removed from cart", "success");
    });

    function refreshCartContent() {
        var content = '';
        var totalPrice = 0;
        var totalCount = 0;
        var cartData = [];
        carts.forEach((item, index) => {
            content += 
                `<li class="item odd last">
                    <a href="#"
                        title="Ipsums Dolors Untra"
                        class="product-image"><img
                        src="${item.image?item.image: '../static/products-images/product-img1.jpg'}"
                        alt="Lorem ipsum dolor" width="65"></a>
                    <div class="product-details">
                        <a  data-id="${index}"
                            title="Remove This Item"
                            class="remove-cart">
                            <i class="pe-7s-close"></i>
                        </a>
                        <p class="product-name"><a href="#">${item.name}</a></p>
                        <strong>${item.count}</strong> x <span class="price">$${item.price}</span>
                    </div>
                </li>`;
            totalPrice += item.count * item.price;
            totalCount += item.count;
            cartData.push(item.id + ',' + item.count);
        });
        $('.cart_count').text(totalCount);
        $("#cart-data").val(cartData.join(';'));
        $("#cart-total-price").html('$' + totalPrice);
        $("#cart-sidebar").html(content);
        var toSave = JSON.stringify(carts);
        localStorage.setItem("carts", toSave);
    }
})