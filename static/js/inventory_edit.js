$(document).ready(function () {
  $("#eclectic-inventory-edit :input[name=title]").change(function() {
    $("#eclectic-inventory-edit").data("changed",true);
  });
  $("#eclectic-inventory-edit").submit(function(e) {
    e.preventDefault();
    if ($("#eclectic-inventory-edit").data("changed")) {
      const name = $("#eclectic-inventory-edit :input[name=title]")[0].value;
      postData("/api-service/inventory/validate/", {"data":name})
        .then(data => {
          if (data.success === "true") {
            swal({
              title: "Are you sure?",
              icon: "warning",
              buttons: true,
              dangerMode: true,
            })
            .then((willcreate) => {
              if (willcreate) {
                swal({
                  title: "Product details edited",
                  icon: "success"
                })
                  .then(() => {
                    $("#eclectic-inventory-edit")[0].submit();
                  })
              }
            });
          } else {
            swal({
              title: "Error when editing product info",
              icon: "error",
              text: data.message
            })
          }
        });
    } else {
      swal({
        title: "Product details edited",
        icon: "success"
      })
        .then(() => {
          $("#eclectic-inventory-edit")[0].submit();
        });
    }
  });
});