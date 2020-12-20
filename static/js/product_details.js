$(document).ready(function () {
  $(".retail-price :input[name=quantity]").change(function () {
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
        })
    }
  });
  $("#eclectic-add-cart").submit(function(e) {
    e.preventDefault();
    swal({
      title: "Item Added to cart",
      icon: "success",
    }).then(() => {
      $("#eclectic-add-cart")[0].submit();
    });
  });
});