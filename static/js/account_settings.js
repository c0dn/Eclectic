$(document).ready(function () {
  let timerId= setInterval(() => {
    if ($("html").hasClass("fontawesome-i2svg-complete")) {
      $("html").trigger("svgloaded");
    }
  }, 1000);
  $("html").on( "svgloaded", function() {
    clearInterval(timerId);
    $("#eclectic-password-change").submit(function (e) {
      e.preventDefault();
      const c_pass = $("#eclectic-c-pass")[0].value.trim();
      const n_pass = $("#eclectic-n-pass")[0].value.trim();
      const nc_pass = $("#eclectic-nc-pass")[0].value.trim();
      postData("/api-service/account/validate/password/", {"current": c_pass, "new": n_pass, "confirm": nc_pass})
        .then(data => {
          if (data.success === "true") {
            swal({
              title: "Password changed",
              icon: "success",
            }).then(() => {
                $("#eclectic-password-change")[0].submit();
            });
          } else{
            swal({
              title: "Error",
              text: data.message,
              icon: "error",
            });
          }
        });
    });
    $("#eclectic-number-edit").click(function () {
      const c_number = document.getElementById("eclectic-number").childNodes[7].nodeValue.trim();
      swal({
        text: "Enter your new phone number",
        content: {
        element: "input",
        attributes: {
          placeholder: "Your new number",
          type: "text",
          value: c_number
          },
        },
        button: {
          text: "Change",
          closeModal: true,
        },
      })
      .then(number => {
        if (!number) {
         swal({
           title: "Error",
           text: "Input cannot be blank",
           icon: "error"
         });
         throw null;
        }
        return postData("/api-service/account/update/number/", {"data": number})
      })
      .then(data => {
        if (data.success === "true") {
          swal({
            title: "Number changed",
            text: "Number changed successfully",
            icon: "success",
          })
            .then(() => {
              document.getElementById("eclectic-number").childNodes[7].nodeValue = data.new_number;
            });
        } else {
           swal({
            title: "Error",
            text: data.message,
            icon: "error",
          })
        }
      })
      .catch(err => {
        if (err) {
          swal("Error", "Unable to change phone number", "error");
        } else {
          swal.stopLoading();
          swal.close();
        }
      });
    });
    $("#eclectic-email-edit").click(function () {
      const c_email = document.getElementById("eclectic-email").childNodes[7].nodeValue.trim();
      swal({
        text: "Enter your new email address",
        content: {
        element: "input",
        attributes: {
          placeholder: "Your new email address",
          type: "text",
          value: c_email
          },
        },
        button: {
          text: "Change",
          closeModal: true,
        },
      })
      .then(email => {
        if (!email) {
         swal({
           title: "Error",
           text: "Input cannot be blank",
           icon: "error"
         });
         throw null;
        }
        return postData("/api-service/account/update/email/", {"data": email})
      })
      .then(data => {
        if (data.success === "true") {
          swal({
            title: "Email changed",
            text: "Email address changed successfully",
            icon: "success",
          })
            .then(() => {
              document.getElementById("eclectic-email").childNodes[7].nodeValue = data.new_email;
            });
        } else {
           swal({
            title: "Error",
            text: data.message,
            icon: "error",
          })
        }
      })
      .catch(err => {
        if (err) {
          swal("Error", "Unable to change email address", "error");
        } else {
          swal.stopLoading();
          swal.close();
        }
      });
    });
  });
  $("#eclectic-address-form").submit(function (e) {
    e.preventDefault();
    swal({
      title: "Address changed",
      icon: "success",
    }).then(() => {
      $("#eclectic-address-form")[0].submit();
    });
  });
});