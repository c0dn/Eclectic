$(document).ready(function () {
    $(".remove-item").click(function () {
        swal({
          title: "Are you sure?",
          text: "Remove item from cart?",
          icon: "warning",
          buttons: true,
          dangerMode: true,
        })
        .then((willremove) => {
          if (willremove) {
            const parents = $(this).parents();
            const parent_q = parents[1].querySelector(".eclectic-quantity");
            const q_child = $(parent_q).children();
            const product_id = q_child[0].value;
            const delete_data = {
                "id": product_id,
            };
            $.ajax({
                url: "/api-service/cart/delete/",
                type: "DELETE",
                contentType: "application/json",
                data: JSON.stringify(delete_data),
                success: function() {
                    swal({
                      title: "Item removed",
                      text: "Item removed from cart",
                      icon: "success",
                    }).then(() => {
                        parents[1].remove();
                        let total = 0;
                        const all_items = $(".cart-entry");
                        for (let i = 0; i < all_items.length; i++) {
                            const p_ele = all_items[i].querySelector(".eclectic-quantity");
                            const element = $(p_ele).children();
                            const u_price = parseFloat(all_items[i].querySelector(".eclectic-price").textContent);
                            let q = parseInt(element[1].value);
                            if (isNaN(q)) {
                                q = 0;
                            }
                            const sub_t = q * u_price;
                            total += sub_t;
                        }
                        $(".eclectic-total > span").text(total.toFixed(2).toString());
                        if (all_items.length === 0) {
                            $(".eclectic-table-wrapper").remove();
                            $(".checkout-btn-container").remove();
                            const div = $('<h2 class="eclectic-not-found"></h2>').text("Empty Cart");
                            $("div.margin-left-dashboard").append(div);
                        }
                    });
               }
            });
          }
        });
    });
    $(".eclectic-cart-input").change(function () {
        const quantity = parseInt($(this)[0].value);
        const max = parseInt($(this)[0].max);
        if (quantity > max) {
          swal({
            title: "Insufficient stock",
            icon: "error",
            text: "Sorry, we only have " + max.toString() + " in stock."
          })
            .then(() => {
              $(this)[0].value = max;
              const ele = $(this);
              const parent_ele = ele.parents()[1];
              const unit_price = parseFloat(parent_ele.querySelector(".eclectic-price").textContent);
              const total = max * unit_price;
              parent_ele.querySelector(".eclectic-item-total").textContent = total.toFixed(2).toString();
              const all_items = $(".cart-entry");
              let total_total = 0;
              for (i = 0; i < all_items.length; i++) {
                  const p_ele = all_items[i].querySelector(".eclectic-quantity");
                  const element = $(p_ele).children();
                  const u_price = parseFloat(all_items[i].querySelector(".eclectic-price").textContent);
                  let q = parseInt(element[1].value);
                  if (isNaN(q)) {
                      q = 0;
                  }
                  const sub_t = q * u_price;
                  total_total += sub_t;
                }
                $(".eclectic-total > span").text(total_total.toFixed(2).toString());
            })
        }
    });
    $(".eclectic-cart-input").on("input", function() {
        const ele = $(this);
        const quantity = parseInt(ele[0].value);
        const parent_ele = ele.parents()[1];
        let total = 0;
        if (isNaN(quantity)) {
            parent_ele.querySelector(".eclectic-item-total").textContent = 0.00.toFixed(2).toString();
        } else {
            const unit_price = parseFloat(parent_ele.querySelector(".eclectic-price").textContent);
            total = quantity * unit_price;
            parent_ele.querySelector(".eclectic-item-total").textContent = total.toFixed(2).toString();
        }
        total = 0;
        const all_items = $(".cart-entry");
        for (i = 0; i < all_items.length; i++) {
            const p_ele = all_items[i].querySelector(".eclectic-quantity");
            const element = $(p_ele).children();
            const u_price = parseFloat(all_items[i].querySelector(".eclectic-price").textContent);
            let q = parseInt(element[1].value);
            if (isNaN(q)) {
                q = 0;
            }
            const sub_t = q * u_price;
            total += sub_t;
        }
        $(".eclectic-total > span").text(total.toFixed(2).toString());
    });
    $("#checkout").click(function () {
        let error = false;
        const all_inputs = $(".eclectic-cart-input");
        for (let i = 0; i < all_inputs.length; i++) {
            const current_input = all_inputs[i];
            const max = parseInt(current_input.max);
            const value = parseInt(current_input.value);
            if (value > max) {
              swal({
                  title: "Insufficient stock",
                  icon: "error",
              });
              error = true;
            }
        }
        if (!error) {
            let dat = [];
            const children = $(".cart-entry");
            for (let i = 0; i < children.length; i++) {
                const parent_ele = children[i].querySelector(".eclectic-quantity");
                const ele = $(parent_ele).children();
                const product_id = ele[0].value;
                const quantity = ele[1].value;
                if (parseInt(quantity) <= 0) {
                    swal({
                        title: "Error",
                        icon: "error",
                        text: "Quantity cannot be 0/negative number"
                    });
                }
                const i_dat = {
                    "id": product_id,
                    "quantity": quantity,
                };
                dat.push(i_dat);
            }
            $.ajax({
                url: "/api-service/cart/confirm/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify(dat),
                success: function(result) {
                    const stripe = Stripe("pk_test_TTKhfH0AEyWBHKxIRoiL24HK009XQKg3y2");
                    stripe.redirectToCheckout({
                      sessionId: result.id
                    }).then(function (result) {
                      console.log(result.error.message);
                    });
               }
            });
        }
    });
    window.addEventListener("unload", function update() {
        const children = $(".cart-entry");
        const dat = [];
        for (let i = 0; i < children.length; i++) {
            const parent_ele = children[i].querySelector(".eclectic-quantity");
            const ele = $(parent_ele).children();
            const product_id = ele[0].value;
            const quantity = ele[1].value;
            const i_dat = {
                "id": product_id,
                "quantity": quantity,
            };
            dat.push(i_dat);
        }
        navigator.sendBeacon("/api-service/cart/update/", JSON.stringify(dat))
    });
});
