$(document).ready(function () {
  $("#eclectic-open-btn").click(function () {
    window.location.href = "/dashboard/support/?closed=false";
  });
  $("#eclectic-closed-btn").click(function () {
    window.location.href = "/dashboard/support/?closed=true";
  });
  $("#eclectic-all-btn").click(function () {
    window.location.href = "/dashboard/support/";
  });
  $("#eclectic-message-form").on("change","#messages-file" , function(){
    const file_list = $("#messages-file")[0].files;
    let counter = 0;
    for (let i = 0; i < file_list.length; i++) {
      const file = file_list[i];
      const allowed_types = ["image/jpeg", "image/png", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
      if (file.size > 5242880) {
        swal({
          title: "Attached file is too big",
          text: file.name + " is too big. Max file size is 5MB.",
          icon: "error",
        });
        $("#messages-file")[0].value = "";
      } else if (!(allowed_types.includes(file.type))) {
        swal({
          title: "File type not supported",
          text: "Only images (jpeg, png) or documents (pdf, docx) can be uploaded",
          icon: "error",
        });
        $("#messages-file")[0].value = "";
      } else{
        counter += 1
      }
    }
    if (counter === file_list.length) {
      swal({
          title: "File uploaded",
          icon: "success",
      }).then(() => {
          $("#eclectic-message-form :input[name=message]")[0].value = "";
          $("#eclectic-message-form")[0].submit();
      });
    }
  });
  $("#eclectic-message-form").submit(function (e) {
    e.preventDefault();
    const message = $("#eclectic-message-form :input[name=message]")[0].value;
    if (message === "") {
      swal({
        title: "Error",
        text: "message cannot be blank",
        icon: "error"
      })
    } else {
      $("#eclectic-message-form")[0].submit();
    }
  });
  $("#eclectic-ticket-close").click(function () {
    swal({
      title: "Are you sure?",
      text: "Once closed, our staff will no longer be able to assist you",
      icon: "warning",
      buttons: true,
      dangerMode: true,
    })
    .then((willclose) => {
      if (willclose) {
        var ticket_id = parseInt(this.value);
        postData("/api-service/ticket/close/", {"id":ticket_id})
          .then((data) => {
            if (data.success === "true") {
              swal({
                title: "Ticket closed",
                text: "You will no longer be able to send messages to our staff",
                icon: "success",
              })
                .then(() => {
                  window.location.href = "/dashboard/support/";
                });
            } else {
              swal({
                title: "Error closing ticket",
                text: "Please contact our staff to resolve this issue",
                icon: "error",
              })
            }
          });
      } else {
        swal({
          title: "Ticket will not be closed",
          icon: "info"
        });
      }
    });
  });
  $('#messages-container').scrollTop(10000);
});