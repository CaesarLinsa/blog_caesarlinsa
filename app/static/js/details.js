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
    $(".reply").click(function () {
        if($(this).text() == "回复"){
            $(this).text("收起");
            var reply_block = $(this).next();
            reply_block[0].style.display="block";
        }else{
            $(this).text("回复");
            var reply_block = $(this).next();
            reply_block[0].style.display="none";
        }

    })

});