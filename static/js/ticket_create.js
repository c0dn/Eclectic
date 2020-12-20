$(document).ready(function (){
  $("#ticket-create-form").submit(function(e) {
    e.preventDefault();
    const all_input = $("#ticket-create-form :input");
    let counter = 0;
    for (let i = 0; i < all_input.length; i++) {
      const input = all_input[i];
      if (input.value === "" && input.name !== "files") {
        swal({
          title: "Input required",
          text: input.name + " is a required field",
          icon: "error",
        })
      } else{
        counter += 1;
      }
    }
    if (counter === all_input.length) {
      swal({
        title: "Submit request?",
        icon: "warning",
        buttons: true,
        dangerMode: true,
      })
      .then((create) => {
        if (create) {
          const file_list = $("#files")[0].files;
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
            } else if (!(allowed_types.includes(file.type))) {
              swal({
                title: "File type not supported",
                text: "Only images (jpeg, png) or documents (pdf, docx) can be uploaded",
                icon: "error",
              });
            } else{
              counter += 1
            }
          }
          if (counter === file_list.length) {
            swal({
                title: "Request sent",
                icon: "success",
            }).then(() => {
                $("#ticket-create-form")[0].submit();
            });
          }
        }
      });
    }
  });
});
