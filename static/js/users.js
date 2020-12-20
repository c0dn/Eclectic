$(document).ready(function () {
  $(".eclectic-deactivate-btn").click(function () {
    swal({
      title: "Are you sure?",
      text: "Once deactivated, user will no longer be able to login",
      icon: "warning",
      buttons: true,
      dangerMode: true,
    })
    .then((willclose) => {
      if (willclose) {
        const usr_id = parseInt(this.value);
        postData("/api-service/user/deactivate/", {"id":usr_id})
          .then((data) => {
            if (data.success === "true") {
              swal({
                title: "Account deactivated",
                icon: "success",
              })
                .then(() => {
                  window.location.href = "/dashboard/users/";
                });
            }
          });
      } else {
        swal({
          title: "Account will not be deactivated",
          icon: "info"
        });
      }
    });
  });
});