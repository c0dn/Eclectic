$(document).ready(function () {
  $(".open-button").click(function () {
    const socket = new WebSocket("ws://localhost:8000");
    $("#chatbot").css("display", "block");
    socket.addEventListener("open", function (event) {
      $(".bubbleWrapper").remove();
      const input_ele = $("input[name=msg]");
      input_ele.removeAttr("disabled");
      const send_btn = $(".send-btn");
      send_btn.removeAttr("disabled");
      $(".send-btn").click(function () {
        const message = input_ele[0].value;
        if (message !== "") {
          socket.send(message.trim());
          input_ele[0].value = "";
          const wrap1 = '<div class="bubbleWrapper">';
          const wrap2 = '<div class="inlineContainer own">';
          const wrap3 = '<div class="chatbot-bubble ownBubble own">';
          const wrap4 = '<div class="content">';
          const m_label = '<b>Me :</b>';
          const m = $("<p></p>").text(message.trim());
          const sub_message_ele = $(wrap4).append(m_label, m);
          const sub2_message_ele = $(wrap3).append(sub_message_ele);
          const sub3_message_ele = $(wrap2).append(sub2_message_ele);
          const main_message_ele = $(wrap1).append(sub3_message_ele);
          const wrap1_bot = '<div class="bubbleWrapper" id="bubble-zoro-loading">';
          const wrap2_bot = '<div class="inlineContainer other">';
          const wrap3_bot = '<div class="chatbot-bubble chatbot-loading otherBubble other">';
          const img_loading = '<img class="loading-container" src="/static/media/loading.gif" alt="chatbot-loading">';
          const sub2_message_ele_bot = $(wrap3_bot).append(img_loading);
          const sub3_message_ele_bot = $(wrap2_bot).append(sub2_message_ele_bot);
          const main_message_ele_bot = $(wrap1_bot).append(sub3_message_ele_bot);
          $("#chatbot-messages").append(main_message_ele_bot, main_message_ele);
          $('#chatbot-messages').scrollTop(10000);
        }
      });
      $(document).on("keypress",function(e) {
        if(e.which === 13) {
          const message = input_ele[0].value;
          if (message !== "") {
            socket.send(message.trim());
            input_ele[0].value = "";
            const wrap1 = '<div class="bubbleWrapper">';
            const wrap2 = '<div class="inlineContainer own">';
            const wrap3 = '<div class="chatbot-bubble ownBubble own">';
            const wrap4 = '<div class="content">';
            const m_label = '<b>Me :</b>';
            const m = $("<p></p>").text(message.trim());
            const sub_message_ele = $(wrap4).append(m_label, m);
            const sub2_message_ele = $(wrap3).append(sub_message_ele);
            const sub3_message_ele = $(wrap2).append(sub2_message_ele);
            const main_message_ele = $(wrap1).append(sub3_message_ele);
            const wrap1_bot = '<div class="bubbleWrapper" id="bubble-zoro-loading">';
            const wrap2_bot = '<div class="inlineContainer other">';
            const wrap3_bot = '<div class="chatbot-bubble chatbot-loading otherBubble other">';
            const img_loading = '<img class="loading-container" src="/static/media/loading.gif" alt="chatbot-loading">';
            const sub2_message_ele_bot = $(wrap3_bot).append(img_loading);
            const sub3_message_ele_bot = $(wrap2_bot).append(sub2_message_ele_bot);
            const main_message_ele_bot = $(wrap1_bot).append(sub3_message_ele_bot);
            $("#chatbot-messages").append(main_message_ele_bot, main_message_ele);
            $('#chatbot-messages').scrollTop(10000);
          }
        }
      });
      $("#close-chat-ui").click(function () {
        $("#chatbot").css("display", "none");
        socket.close();
        input_ele.prop("disabled", true);
        send_btn.prop("disabled", true);
        input_ele[0].value = "";
        $(".bubbleWrapper").remove();
        const wrap1 = '<div class="bubbleWrapper" id="bubble-zoro-loading">';
        const wrap2 = '<div class="inlineContainer other">';
        const wrap3 = '<div class="chatbot-bubble chatbot-loading otherBubble other">';
        const img_loading = '<img class="loading-container" src="/static/media/loading.gif" alt="chatbot-loading">';
        const sub2_message_ele = $(wrap3).append(img_loading);
        const sub3_message_ele = $(wrap2).append(sub2_message_ele);
        const main_message_ele = $(wrap1).append(sub3_message_ele);
        $("#chatbot-messages").append(main_message_ele);
      });
    });
    socket.addEventListener("message", function (event) {
      const zoro_message = event.data;
      $("#bubble-zoro-loading").remove();
      const wrap1_other = '<div class="bubbleWrapper">';
      const wrap2_other = '<div class="inlineContainer other">';
      const wrap3_other = '<div class="chatbot-bubble otherBubble other">';
      const wrap4_other = '<div class="content">';
      const m_label_zoro = '<b>Zoro :</b>';
      const m_zoro = $("<p></p>").text(zoro_message);
      const sub_message_ele_other = $(wrap4_other).append(m_label_zoro, m_zoro);
      const sub2_message_ele_other = $(wrap3_other).append(sub_message_ele_other);
      const sub3_message_ele_other = $(wrap2_other).append(sub2_message_ele_other);
      const main_message_ele_other = $(wrap1_other).append(sub3_message_ele_other);
      $("#chatbot-messages").append(main_message_ele_other);
      $('#chatbot-messages').scrollTop(10000);
    });
    socket.addEventListener("close", function () {
      const input_ele = $("input[name=msg]");
      const send_btn = $(".send-btn");
      input_ele.prop("disabled", true);
      send_btn.prop("disabled", true);
      input_ele[0].value = "";
    });
    socket.addEventListener("error", function () {
      const input_ele = $("input[name=msg]");
      const send_btn = $(".send-btn");
      input_ele.prop("disabled", true);
      send_btn.prop("disabled", true);
      input_ele[0].value = "";
    });
  });
});
