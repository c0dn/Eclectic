$(document).ready(function () {
  $("select.year-select").change(function () {
    let year = $(this).children("option:selected").val();
    window.location.href = "/dashboard/report/?year="+year;
  });
});