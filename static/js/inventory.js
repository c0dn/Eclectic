$(document).ready(function () {
  const file = document.getElementById("file");
  const preview = document.querySelector('.preview');
  file.addEventListener('change', updateImageDisplay);
  function updateImageDisplay() {
    let para;
    while (preview.firstChild) {
      preview.removeChild(preview.firstChild);
    }
    var curFiles = file.files;
    if (curFiles.length === 0) {
      para = document.createElement('p');
      para.textContent = 'No files currently selected for upload';
      preview.appendChild(para);
    } else {
      const image_container = document.createElement('div');
      preview.appendChild(image_container);
      para = document.createElement('p');
      para.textContent = 'File Name : ' + curFiles[0].name;
      para.className = "file_name";
      const image = document.createElement('img');
      image.className = "upload_image";
      image.src = window.URL.createObjectURL(curFiles[0]);
      image_container.appendChild(image);
      image_container.appendChild(para);
    }
  }
  $("#eclectic-inventory-add").submit(function(e) {
    e.preventDefault();
    const name = $("#eclectic-inventory-add :input[name=title]")[0].value;
    const file_list = $("#eclectic-inventory-add :input[name=file]")[0].files;
    let counter = 0;
    if (file_list.length === 0) {
      swal({
        title: "Error when creating new product",
        icon: "error",
        text: "No File selected"
      })
    } else {
      for (let i = 0; i < file_list.length; i++) {
      const file = file_list[i];
      const allowed_types = ["image/jpeg", "image/png"];
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
                  title: "Product added",
                  icon: "success"
                })
                  .then(() => {
                    $("#eclectic-inventory-add")[0].submit();
                  })
              }
            });
          } else {
            swal({
              title: "Error when creating new product",
              icon: "error",
              text: data.message
            })
          }
        });
    }
    }
  });
});

