$(document).ready(function (){
  $("#eclectic-login-form").submit(function(e) {
    e.preventDefault();
    const username = $("#eclectic-login-form :input[name=username]")[0].value;
    const password = $("#eclectic-login-form :input[name=password]")[0].value;
    postData("/api-service/login/validate/", {"username":username, "password":password})
      .then(data => {
        if (data.success === "true") {
          swal({
          title: "Welcome "+data.user,
          text: "Logged in successfully",
          icon: "success"
        }).then(() => {
          $("#eclectic-login-form")[0].submit();
        });
        } else{
          swal({
            title: "Login Failed",
            icon: "error",
            text: data.message
          })
        }
      });
  });
});