async function validate_form() {
  let error_list = [];
  const all_input = $("#eclectic-register-form :input");
  for (let i = 0; i < all_input.length; i++) {
    const input = all_input[i];
    if (input.name === "phoneNumber") {
      const number = input.value;
      await postData("/api-service/register/validate/number/", {"data": number})
      .then(data => {
        if (data.success !== "true") {
          error_list.push(data.message);
        }
      });
    } else if (input.name === "password") {
      const n_pass = input.value;
      const nc_pass = $("#register-confirm-pass")[0].value;
      await postData("/api-service/register/validate/password/", {"new": n_pass, "confirm": nc_pass})
        .then(data => {
          if (data.success !== "true") {
            error_list.push(data.message);
          }
        });
    } else if (input.name === "email") {
      const email = input.value;
      await postData("/api-service/register/validate/email/", {"data": email})
        .then(data => {
          if (data.success !== "true") {
            error_list.push(data.message);
          }
        })
    }
  }
  return error_list
}

$(document).ready(function (){
  $("#eclectic-register-form").submit(function(e) {
    e.preventDefault();
    validate_form().then(error_list => {
      if (error_list.length === 0) {
        swal({
          title: "Registration Successful",
          icon: "success"
        }).then(() => {
          $("#eclectic-register-form")[0].submit();
        });
      } else {
        const error_message = error_list.join("\n");
        swal({
          title: "Invalid inputs",
          icon: "error",
          text: error_message
        });
      }
    });
  });
});
