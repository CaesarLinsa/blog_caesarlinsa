
$(function () {
    $("#delete").click(function () {

        var article_id = $(this).attr('article_id');
        $.ajax({
            type: "DELETE",
            url: "/article/delete/" + article_id,
            success:function(msg){
                alert("删除成功")
            }
        })

    });

});
