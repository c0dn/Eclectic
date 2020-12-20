async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST",
    mode: "cors",
    cache: "no-cache",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json"
    },
    redirect: "follow",
    referrerPolicy: "no-referrer",
    body: JSON.stringify(data)
  });
  return await response.json();
}
$(document).ready(function() {
  $.post("/api-service/corn/");
  $(".eclectic-menu-btn").click(function () {
    var target_element = $(".eclectic-topnav");
    if (target_element.hasClass("responsive")) {
      target_element.removeClass("responsive");
    } else {
      target_element.addClass("responsive");
    }
  });
  $("#eclectic-forget-form").submit(function (e) {
    e.preventDefault();
    swal({
      title: "Email sent",
      icon: "success",
      text: "If the email address entered matches an existing user account, a password reset link will be sent to the email address."
    })
      .then(() => {
        $("#eclectic-forget-form")[0].submit();
    });
  });
  $("#eclectic-reset-form").submit(function (e) {
    e.preventDefault();
    const n_pass = $("#eclectic-reset-form :input[name=password1]")[0].value;
    const nc_pass = $("#eclectic-reset-form :input[name=password2]")[0].value;
    postData("/api-service/register/validate/password/", {"new": n_pass, "confirm": nc_pass})
      .then(data => {
        if (data.success === "true") {
          swal({
            title: "Password reset successful",
            icon: "success"
          })
            .then(() => {
              $("#eclectic-reset-form")[0].submit();
          });
        } else {
          swal({
            title: "Password invalid",
            icon: "error",
            text: data.message
          })
        }
    });
  });
  $("#menu-trigger").on("click", function () {
    $(this).toggleClass("menu-clicked");
    $("#side").toggleClass("slide-in");
    $("#main").toggleClass("slide-content");
   });
  $(".hamburger").click(function () {
    $("#responsive-sidenav").css("width", "100%");
  });
  $(".closebtn").click(function () {
    $("#responsive-sidenav").css("width", "0");
  });
});

