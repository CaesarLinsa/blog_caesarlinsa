var comment_id;

$(function () {
    // 点击删除a连接时，删除文章
    $("#delete").click(function () {

        var article_id = $(this).attr('article_id');
        $.ajax({
            type: "DELETE",
            url: "/article/delete/" + article_id,
            success:function(msg){
                window.location.href="/article/list"
            }
        })
    });
    // 点击回复时，下面展开form框，"回复"变为"收起"
    $("body").on("click", ".reply", function () {
        if($(this).text() == "回复"){
            comment_id = $(this).attr("comment_id");
            $(this).text("收起");
            //绘制form表单
            var FROM = $("<form>");
            var INPUT=$("<input>");
            var SUBMIT=$("<submit id='sub'>");
            INPUT.addClass("form-control");
            INPUT.attr('type', 'text');
            INPUT.addClass("input_content");
            SUBMIT.addClass("btn btn-primary");
            SUBMIT.attr("comment_id", comment_id);
            SUBMIT.text("提交");
            FROM.append(INPUT).append(SUBMIT);
            $(this).after(FROM);
        }else{
            $(this).text("回复");
            var reply_block = $(this).next();
            reply_block[0].remove();
        }

    });
    //在form表单中输入内容，提交后，post发送
    $("body").on('click', "#sub",  function () {
        article_id = $("#delete").attr("article_id");
        comment_id = $(this).attr("comment_id");
        var data = $(".input_content").val();
        var sub = $(this);
        $.post("/reply/" + article_id + "/"+ comment_id,
            {values: data},
            function (data) {
                var reply = sub.parent().prev();
                reply.text("回复");
                reply.next()[0].remove();
                var span = $("<div>");
                var a = $("<a>");
                a.attr('href','javascript:;');
                a.attr('comment_id',comment_id);
                a.text("回复");
                a.addClass("reply");
                span.text(data.data);
                span.append(a);
                reply.after(span);
            })
    });
});