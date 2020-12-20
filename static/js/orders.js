$(document).ready(function () {
  $("#eclectic-deliver-btn").click(function () {
    window.location.href = "/dashboard/orders/?delivered=false";
  });
  $("#eclectic-history-btn").click(function () {
    window.location.href = "/dashboard/orders/?delivered=true";
  });
  $("#eclectic-all-btn").click(function () {
    window.location.href = "/dashboard/orders/";
  });
});