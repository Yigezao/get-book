var nums = 10; //每页出现的数据量
var order = "synUpdateType|DESC,date|DESC,ik_subject|DESC,id|DESC";//排序
var pages = 0;//总条数
var number = 1;//序号
var where = "";//检索条件
var searchname = "";
var nav = 0;//导航ID
var ajaxKeys = "";//检索词集合
$(function () {
    nav = getUrlParam("nav");
    where = getUrlParam("search");
    where = $.base64.decode(where, 'utf8')
    searchname = getUrlParam("searchname");
    searchname = $.base64.decode(searchname, 'utf8')
    ajaxKeys = getUrlParam("ajaxKeys");
    if (ajaxKeys) {
        ajaxKeys = $.base64.decode(ajaxKeys, 'utf8');
    }

    if (AntiSqlValid2(where) && AntiSqlValid2(searchname)) {
        searchcount(where, 1, nums, order, ajaxKeys);
        addEsSearchLog(where, order, ajaxKeys);
        AddSearchLog(where, searchname, pages);
        $("#lbl_numbers").html(pages);
        if (searchname != '' && searchname != undefined && searchname.indexOf("\\\\\\") > 0) {
            searchname = searchname.replaceAll("\\\\\\", "")
            if (searchname.indexOf("\\") > 0) {
                searchname = searchname.replaceAll("\\", "")
            }
            $("#searchname").html(searchname);
        } else {
            $("#searchname").html(searchname);
        }
        var allpages = Math.ceil(pages / nums);//总页数
        layui.use(['laypage'], function () {
            var laypage = layui.laypage;
            //调用分页
            laypage({
                cont: 'page'
                , pages: allpages //得到总页数
                , skip: true
                , jump: function (obj) {
                    number = ((obj.curr - 1) * nums) + 1;
                    if (obj.curr == allpages) {//判断是否是最后一页
                        $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + pages);
                    } else {
                        $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + obj.curr * nums);
                    }
                    if(where.indexOf("IKCR=") > -1 || where.indexOf("IKCE=") > -1 || where.indexOf("creators:*") > -1){
                        order = "";
                        $("#order_default").attr("class", "current");
                        $("#order_time").attr("class", "");
                    }else{
                        order = "synUpdateType|DESC,date|DESC,ik_subject|DESC,id|DESC";
                    }
                    search(where, obj.curr, nums, order, ajaxKeys);
                    $('body,html').animate({scrollTop: 0}, 1000); //1000代表1秒时间回到顶点
                }
            });
        });
        //按时间排序
        $("#order_time").click(function () {
            $("#order_default").attr("class", "");
            $("#order_time").attr("class", "current");
            order = "synUpdateType|DESC,date|DESC,ik_subject|DESC,id|DESC";
            searchcount(where, 1, nums, order, ajaxKeys);
            var allpages = Math.ceil(pages / nums);//总页数
            layui.use(['laypage'], function () {
                var laypage = layui.laypage;
                //调用分页
                laypage({
                    cont: 'page'
                    , pages: allpages //得到总页数
                    , skip: true
                    , jump: function (obj) {
                        number = ((obj.curr - 1) * nums) + 1;
                        if (obj.curr == allpages) {//判断是否是最后一页
                            $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + pages);
                        } else {
                            $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + obj.curr * nums);
                        }
                        search(where, obj.curr, nums, order, ajaxKeys);
                    }
                });
            });
        });
        //按默认排序
        $("#order_default").click(function () {
            $("#order_default").attr("class", "current");
            $("#order_time").attr("class", "");
            order = "synUpdateType|DESC,id|ASC";
            searchcount(where, 1, nums, order, ajaxKeys);
            layui.use(['laypage'], function () {
                var laypage = layui.laypage;
                //调用分页
                laypage({
                    cont: 'page'
                    , pages: Math.ceil(pages / nums) //得到总页数
                    , skip: true
                    , jump: function (obj) {
                        number = ((obj.curr - 1) * nums) + 1;
                        $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + obj.curr * nums);
                        search(where, obj.curr, nums, order, ajaxKeys);
                    }
                });
            });
        });
        //按简文列表
        $("#show_articlelist").click(function () {
            $("#show_articlelist").attr("class", "current");
            $("#show_titlelist").attr("class", "");
            $("#ul_articlelist").show();
            $("#tab_articlelist").hide();
        });
        //按标题列表
        $("#show_titlelist").click(function () {
            $("#show_articlelist").attr("class", "");
            $("#show_titlelist").attr("class", "current");
            $("#ul_articlelist").hide();
            $("#tab_articlelist").show();
        });
        //在结果中检索
        $("#result_search").click(function () {
            result_Search();
        });
        //左侧分组
        if (pages > 0) {
            //返回文献类型分的组
            FacetType(where, "type", 10)
            //检索返回作者分的组
            FacetCreator(where, "creators", 10);
            //返回按年分组
            FacetYears(where, "years", 10);
            //古籍类型分组
            FacetClassname(where, "classname", 10)

            //期刊分组
            FacetMedias(where, "cbw_name", 10)

            //关键词分组
            FacetKeyWordS(where, "keyword_s", 10)
        }
        //导航栏定位
        $(".search-type li").removeClass();
        $(".search-type li").each(function () {
            if ($(this).attr("data-val") == nav) {
                $(this).attr("class", "zx-current");
            }

        });
    }

});


//检索返回结果列表
function search(search, pageIndex, pageSize, order, ajaxKeys) {
    if (AntiSqlValid(search) == true) {
        var obj = {}, sType = getUrlParam("sType");
        obj.search = search;
        obj.pageNum = pageIndex;
        obj.pageSize = pageSize;
        obj.sort = order;
        obj.sType = sType;
        obj.ajaxKeys = ajaxKeys;
        obj.customShowCondition = searchname;
        $.ajax({
            type: "POST",
            url: "/searchHandler/search",
            data: obj,
            async: false,
            success: function (data) {
                var html = "";
                var htmllist = "<tr><th width='40%;' scope='col'>题名</th><th width='13%;' scope='col'>作者</th><th class='hidden-xs' width='14%;' scope='col'>来源</th><th class='hidden-xs' width='15%;' scope='col'>发表时间 </th><th class='hidden-xs' width='10%;' scope='col'>下载 </th><th width='10%;' scope='col'>阅读</th></tr>";
                if (data != "") {
                    var jsons = data.data;
                    if (jsons != null) {
                        pages = jsons["total"];
                        jsons["result"] = jsons["rows"];
                        var idArr = [];
                        for (var i = 0; i < jsons["result"].length; i++) {
                            idArr.push({id: jsons["result"][i]["data_id"], type: jsons["result"][i]["type"]})
                        }
                        var downread = getReadDown(idArr);
                        for (var i = 0; i < jsons["result"].length; i++) {
                            if (jsons["result"][i]["type"] == "古籍") {
                                htmllist += "<tr><td class='htmllist_tab1'><a href='javascript:void(0)' onclick='hrefinfo(this)' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-synUpdateType='" + jsons["result"][i]["synUpdateType"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["id"] + "' data-barcodenum='" + jsons["result"][i]["id"] + "' title='" + changValue(StrReplace(jsons["result"][i]["title"]) + (changValue(jsons["result"][i]["num"]) != "暂无" ? jsons["result"][i]["num"] : "")) + "'>" + number + "、" + changValue(jsons["result"][i]["ik_title"] + (changValue(jsons["result"][i]["num"]) != "暂无" ? jsons["result"][i]["num"] : "")) + "</a></td><td class='htmllist_tab2' title='" + changValue(jsons["result"][i]["creator"]) + "'>" + (changValue(jsons["result"][i]["ik_creator"]).length > 10 ? changValue(jsons["result"][i]["ik_creator"]).substr(0, 10) : changValue(jsons["result"][i]["ik_creator"])) + "</td>";
                            } else if (jsons["result"][i]["type"] == "外文图书") {
                                htmllist += "<tr><td class='htmllist_tab1'><a href='javascript:void(0)' onclick='hrefinfo(this)' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-synUpdateType='" + jsons["result"][i]["synUpdateType"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["barcodenum"] + "' title='" + changValue(StrReplace(jsons["result"][i]["title"])) + "'>" + number + "、" + changValue(jsons["result"][i]["ik_title"]) + "</a></td><td class='htmllist_tab2' title='" + GetCreatorlisttitle(jsons["result"][i]["creator"]) + "'><p class='zuozheshengnuehao'>" + GetCreatorlisthtml(jsons["result"][i]["ik_creator"]) + "</p></td>";
                            } else {
                                if(jsons["result"][i]["synUpdateType"] == "2") {
                                    htmllist += "<tr><td class='htmllist_tab1'><a href='javascript:void(0)' onclick='hrefinfo(this)' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-synUpdateType='" + jsons["result"][i]["synUpdateType"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "' title='" + changValue(StrReplace(jsons["result"][i]["title"])) + "'>" + number + "、<span class='biaotiYx'>" + changValue(jsons["result"][i]["ik_title"]) + "</span><p class='yxbiaoshi'></p>" + "</a></td><td class='htmllist_tab2' title='" + GetCreatorlisttitle(jsons["result"][i]["creator"]) + "'><p class='zuozheshengnuehao'>" + GetCreatorlisthtml(jsons["result"][i]["ik_creator"]) + "</p></td>";
                                } else if (jsons["result"][i]["collections"] != undefined && jsons["result"][i]["collections"] != null && jsons["result"][i]["collections"] == 3){
                                    htmllist += "<tr><td class='htmllist_tab1'><a href='javascript:void(0)' onclick='hrefinfo(this)' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "' title='" + changValue(StrReplace(jsons["result"][i]["title"])) + "'>" + number + "、<span class='biaotiYx'>" + changValue(jsons["result"][i]["ik_title"]) + "</span><p class='jikanwenti'></p></a><i class=\"jikan_biaoshi2\"></i></td><td class='htmllist_tab2' title='" + GetCreatorlisttitle(jsons["result"][i]["ik_creator"]) + "'>" + GetCreatorlisthtml(jsons["result"][i]["ik_creator"]) + "</td>";
                                } else {
                                    htmllist += "<tr><td class='htmllist_tab1'><a href='javascript:void(0)' onclick='hrefinfo(this)' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "' title='" + changValue(StrReplace(jsons["result"][i]["title"])) + "'>" + number + "、" + changValue(jsons["result"][i]["ik_title"]) + "</a></td><td class='htmllist_tab2' title='" + GetCreatorlisttitle(jsons["result"][i]["ik_creator"]) + "'>" + GetCreatorlisthtml(jsons["result"][i]["ik_creator"]) + "</td>";
                                }
                            }
                            if (changValue(jsons["result"][i]["cbw_name"]) != "暂无") {
                                htmllist += "<td class='hidden-xs htmllist_tab3'>《<labe title=" + jsons["result"][i]["cbw_name"] + ">" + changValue(jsons["result"][i]["cbw_name"]) + "</lable>》</td>";
                            } else {
                                htmllist += "<td class='hidden-xs'>无</td>";
                            }
                            htmllist += "<td class='hidden-xs htmllist_tab4'>";
                            if (jsons["result"][i]["type"] == "古籍") {
                                htmllist += (changValue(jsons["result"][i]["pubdatenote"]) != "暂无" ? jsons["result"][i]["pubdatenote"] : "");
                            } else if (jsons["result"][i]["type"] == "外文图书") {
                                if (changValue(jsons["result"][i]["years"]) != "暂无") {
                                    htmllist += jsons["result"][i]["years"] + "年";
                                } else {
                                    htmllist += "无";
                                }
                            } else {
                                if (changValue(jsons["result"][i]["years"]) != "暂无") {
                                    htmllist += jsons["result"][i]["years"] + "年";
                                }
                                if (jsons["result"][i]["synUpdateType"] == 2 && jsons["result"][i]["month"] != "" && jsons["result"][i]["month"] != null) {
                                    htmllist += jsons["result"][i]["month"] + "月";
                                }else if (changValue(jsons["result"][i]["num"]) != "暂无") {
                                    htmllist += "第" + jsons["result"][i]["num"] + "期";
                                }
                                if (changValue(jsons["result"][i]["years"]) == "暂无" && changValue(jsons["result"][i]["num"]) == "暂无") {
                                    htmllist += "无";
                                }
                            }

                            htmllist += "</td>";

                            html += "<li>";
                            //根据文献类型拼装标题
                            if (jsons["result"][i]["type"] == "古籍") {
                                html += "<div class='julei-list'>" + number + "、<a href='javascript:void(0);' onclick='hrefinfo(this);return false;' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-synUpdateType='" + jsons["result"][i]["synUpdateType"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "' data-barcodenum='" + jsons["result"][i]["barcodenum"] + "'>" + jsons["result"][i]["ik_title"] + (changValue(jsons["result"][i]["num"]) != "暂无" ? jsons["result"][i]["num"] : "") + "</a>";
                            } else if (jsons["result"][i]["type"] == "外文图书") {
                                html += "<div class='julei-list'>" + number + "、<a href='javascript:void(0);' onclick='hrefinfo(this);return false;' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-synUpdateType='" + jsons["result"][i]["synUpdateType"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["barcodenum"] + "'>" + jsons["result"][i]["ik_title"] + "</a>";
                            } else {
                                if (jsons["result"][i]["synUpdateType"] == "2") {
                                    html += "<div class='julei-list'>" + number + "、<a href='javascript:void(0);' onclick='hrefinfo(this);return false;' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-synUpdateType='" + jsons["result"][i]["synUpdateType"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "'>" + jsons["result"][i]["ik_title"] + "<p class='yxbiaoshi'></p>" + "</a>";
                                } else if (jsons["result"][i]["collections"] != undefined && jsons["result"][i]["collections"] != null && jsons["result"][i]["collections"] == 3){
                                    html += "<div class='julei-list'>" + number + "、<a href='javascript:void(0);' onclick='hrefinfo(this);return false;' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "'>" + jsons["result"][i]["ik_title"] + "<i class=\"jikan_biaoshi\"></i></a>";
                                } else {
                                    html += "<div class='julei-list'>" + number + "、<a href='javascript:void(0);' onclick='hrefinfo(this);return false;' data-encryptedUrl='" + jsons["result"][i]["encryptedUrl"] + "' data-type='" + jsons["result"][i]["type"] + "' data-name='" + jsons["result"][i]["tab_name"] + "' data-id='" + jsons["result"][i]["data_id"] + "'>" + jsons["result"][i]["ik_title"] + "</a>";
                                }
                            }
                            //根据文献类型拼装下载和阅读地址
                            if (jsons["result"][i]["type"] == "古籍") {
                                if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                    html += "<a class='house' target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "\",\"0\",\"" + jsons["result"][i]["classname"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + (changValue(jsons["result"][i]["num"]) != "暂无" ? jsons["result"][i]["num"] : "") + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'>阅读全文</a>";
                                    // html += "<a class='house r100'  onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\");return false;' href='javascript:void(0);'>全文下载</a>";
                                }
                            } else if (jsons["result"][i]["type"] == "外文期刊文章") {
                                if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                    html += "<a class='house' target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["id"].replace("CASS", "") + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'>阅读全文</a>";
                                }
                            } else if (jsons["result"][i]["type"] == "外文图书") {
                                if (changValue(jsons["result"][i]["barcodenum"]) != "暂无") {
                                    html += "<a class='house r100'  onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "&title=" + StrReplace(jsons["result"][i]["title"]) + "\",\"0\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'>全文下载</a>";
                                }
                            } else {
                                if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                    html += "<a class='house' target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["id"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'>阅读全文</a>";
                                }
                                if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                    html += "<a class='house r100'  onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["id"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'>全文下载</a>";
                                }
                            }
                            html += "</div>";
                            //根据文献类型拼装简文内容
                            if (jsons["result"][i]["type"] == "古籍") {
                                if (changValue(jsons["result"][i]["cbw_name"]) != "暂无") {
                                    html += "<p><strong>出版者</strong>：" + changValue(jsons["result"][i]["ik_creator"]) + "</p>";
                                }
                                html += "<p><strong>出版时间</strong>：" + (changValue(jsons["result"][i]["pubdatenote"]) != "暂无" ? jsons["result"][i]["pubdatenote"] : "") + "</p>";
                                if (changValue(jsons["result"][i]["section"]) != "暂无") {
                                    html += "<p><strong>版   本</strong>：" + jsons["result"][i]["section"] + "</p>";
                                }
                                if (changValue(jsons["result"][i]["data_id"]) != "暂无") {
                                    html += "<p><strong>索书号</strong>： " + jsons["result"][i]["isbn"] + "</p>";
                                }
                                html += "<p><strong>分   类</strong>：" + jsons["result"][i]["classname"] + " </p>";
                            } else if (jsons["result"][i]["type"] == "外文期刊文章") {
                                if (changValue(jsons["result"][i]["cbw_name"]) != "暂无") {
                                    if (jsons["result"][i]["endpage"] != null) {
                                        html += "<p><strong>出　　处</strong>：《" + jsons["result"][i]["cbw_name"] + "》" + GetDatabaseCollectKind(jsons["result"][i]["lngcollectids"]) + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["num"]) != "暂无" ? "第" + jsons["result"][i]["num"] + "期" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"] + "-" + jsons["result"][i]["endpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "") + "</p>";
                                    } else {
                                        html += "<p><strong>出　　处</strong>：《" + jsons["result"][i]["cbw_name"] + "》" + GetDatabaseCollectKind(jsons["result"][i]["lngcollectids"]) + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["num"]) != "暂无" ? "第" + jsons["result"][i]["num"] + "期" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "") + "</p>";
                                    }
                                }
                                if (changValue((jsons["result"][i]["ik_creator"] == null ? jsons["result"][i]["ik_creator_e"] : jsons["result"][i]["ik_creator"])) != "暂无") {
                                    html += "<p><strong>作　　者</strong>：" + GetCreatorlist((jsons["result"][i]["ik_creator"] == null ? jsons["result"][i]["ik_creator_e"] : jsons["result"][i]["ik_creator"])) + "</p>";
                                }
                                if (changValue(jsons["result"][i]["imburse"]) != "暂无") {
                                    html += "<p><strong>基金项目</strong>：" + jsons["result"][i]["imburse"] + "</p>";
                                }
                                if (changValue(jsons["result"][i]["remark"]) != "暂无") {
                                    html += "<p><strong>摘　　要</strong>： " + jsons["result"][i]["remark"] + "</p>";
                                }
                                if (changValue(jsons["result"][i]["ik_subject"]) != "暂无" && jsons["result"][i]["ik_subject"] && jsons["result"][i]["ik_subject"].trim() != '') {
                                    html += "<p><strong>关 键 词</strong>：" + GetKeyWord(jsons["result"][i]["ik_subject"]) + " </p>";
                                }

                            } else if (jsons["result"][i]["type"] == "外文图书") {
                                if (changValue(jsons["result"][i]["tspress"]) != "暂无") {
                                    //html += "<p><strong>出版社</strong>：《" + jsons["result"][i]["tspress"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "") + "</p>";
                                    html += "<p><strong>出版社</strong>：《" + jsons["result"][i]["tspress"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + "</p>";
                                }
                                html += "<p><strong>出版地</strong>：" + changValue(jsons["result"][i]["address"]) + "</p>";
                                html += "<p><strong>著    者</strong>：" + changValue(jsons["result"][i]["ik_creator"]) + "</p>";
                                html += "<p><strong>编    者</strong>： " + changValue(jsons["result"][i]["ik_creator_e"]) + "</p>";
                                html += "<p><strong>译    者</strong>：" + changValue(jsons["result"][i]["translator"]) + " </p>";
                            } else {
                                if (changValue(jsons["result"][i]["cbw_name"]) != "暂无") {
                                    if (jsons["result"][i]["endpage"] != null) {
                                        if (jsons["result"][i]["synUpdateType"] == 2 && jsons["result"][i]["month"] != "" && jsons["result"][i]["month"] != null) {
                                            html += "<p><strong>出　　处</strong>："
                                                + "<a href=\"/journal/secure/details?params=" + jsons["result"][i]["qkEncryptedUrl"] + "\" target='_blank' class='chuchu_style'>《" +
                                                jsons["result"][i]["cbw_name"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["month"]) != "暂无" ? jsons["result"][i]["month"] + "月" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"] + "-" + jsons["result"][i]["endpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "")
                                                + "</a>" + "</p>"
                                        } else {
                                            if (jsons["result"][i]["id"].indexOf('_sys') != -1) {
                                                html += "<p><strong>出　　处</strong>："
                                                    + "<a href=\"/journal/secure/details?params=" + jsons["result"][i]["qkEncryptedUrl"] + "\" target='_blank' class='chuchu_style'>《" +
                                                    jsons["result"][i]["cbw_name"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["num"]) != "暂无" ? "第" + jsons["result"][i]["num"] + "期" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"] + "-" + jsons["result"][i]["endpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "")
                                                    + "</a>" + "</p>"
                                            } else {
                                                html += "<p><strong>出　　处</strong>："
                                                    + "<a href=\"/journal/secure/details?params=" + jsons["result"][i]["qkEncryptedUrl"] + "\" target='_blank' class='chuchu_style'>《" +
                                                    jsons["result"][i]["cbw_name"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["num"]) != "暂无" ? "第" + jsons["result"][i]["num"] + "期" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"] + "-" + jsons["result"][i]["endpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "")
                                                    + "</a>" + "</p>"
                                            }
                                        }
                                    } else {
                                        if (jsons["result"][i]["synUpdateType"] == 2 && jsons["result"][i]["month"] != "" && jsons["result"][i]["month"] != null) {
                                            html += "<p><strong>出　　处</strong>："
                                                + "<a href=\"/journal/secure/details?params=" + jsons["result"][i]["qkEncryptedUrl"] + "\" target='_blank' class='chuchu_style'>《" +
                                                jsons["result"][i]["cbw_name"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["month"]) != "暂无" ? jsons["result"][i]["month"] + "月" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"] + "-" + jsons["result"][i]["endpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "")
                                                + "</a>" + "</p>"
                                        } else {
                                            if (jsons["result"][i]["id"].indexOf('_sys') != -1) {
                                                html += "<p><strong>出　　处</strong>：《"
                                                    + "<a href=\"/journal/secure/details?params=" + jsons["result"][i]["qkEncryptedUrl"] + "\" target='_blank' class='chuchu_style'>《" +
                                                    jsons["result"][i]["cbw_name"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["num"]) != "暂无" ? "第" + jsons["result"][i]["num"] + "期" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "")
                                                    + "</a>" + "</p>"
                                            } else {
                                                html += "<p><strong>出　　处</strong>：《"
                                                    + "<a href=\"/journal/secure/details?params=" + jsons["result"][i]["qkEncryptedUrl"] + "\" target='_blank' class='chuchu_style'>《" +
                                                    jsons["result"][i]["cbw_name"] + "》" + " " + (changValue(jsons["result"][i]["years"]) != "暂无" ? jsons["result"][i]["years"] + "年" : "") + (changValue(jsons["result"][i]["num"]) != "暂无" ? "第" + jsons["result"][i]["num"] + "期" : "") + (changValue(jsons["result"][i]["beginpage"]) != "暂无" ? (jsons["result"][i]["beginpage"] == 0 ? "" : jsons["result"][i]["beginpage"]) : "") + (changValue(jsons["result"][i]["pagecount"]) != "暂无" ? ",共" + jsons["result"][i]["pagecount"] + "页" : "")
                                                    + "</a>" + "</p>"
                                            }
                                        }
                                    }
                                }
                                const currentItem = jsons["result"][i] || {};
                                const creatorCn = currentItem["ik_creator"] && currentItem["ik_creator"].trim() || '';
                                if (GetCreatorlist(creatorCn) !== '无') {
                                    const creatorEn = currentItem["ik_creator_e"] && currentItem["ik_creator_e"].trim() || '';
                                    if (GetCreatorlist(creatorEn) !== '无' && !isInvalidBracket(creatorEn)) {
                                        html += `<p><strong class="text_jus">作　　者：</strong>${GetCreatorlist(creatorCn)}<span>${creatorEn}</span></p>`;
                                    }else{
                                        html += `<p><strong class="text_jus">作　　者：</strong>${GetCreatorlist(creatorCn)}</p>`;
                                    }
                                }
                                if (isValidValue(jsons["result"][i]["imburse"])) {
                                    html += "<p><strong>基金项目</strong>：" + jsons["result"][i]["imburse"] + "</p>";
                                }
                                if (isValidValue(jsons["result"][i]["remark"])) {
                                    html += "<p><strong>摘　　要</strong>： " + escapeHtml(jsons["result"][i]["remark"]) + "</p>";
                                }
                                if(GetKeyWord(jsons["result"][i]["ik_subject"]) != ''){
                                    html += "<p><strong>关 键 词</strong>：" + GetKeyWord(jsons["result"][i]["ik_subject"]) + " </p>";
                                }
                            }
                            //var temp = Get_DowndorRead(jsons["result"][i]["type"], jsons["result"][i]["data_id"]);
                            var temp = downread[i];
                            if (temp != null) {
                                temp = [temp];
                                if (jsons["result"][i]["type"] == "古籍") {
                                    html += "<p class='number'>在线阅读：<strong>" + (temp[0]["readCount"] == null ? 0 : temp[0]["readCount"]) + "</strong></p>";
                                } else {
                                    html += "<p class='number'>下载次数：<strong>" + (temp[0]["downCount"] == null ? 0 : temp[0]["downCount"]) + "</strong>在线阅读：<strong>" + (temp[0]["readCount"] == null ? 0 : temp[0]["readCount"]) + "</strong></p>";
                                }
                                htmllist += "<td class='hidden-xs'>";

                                if (jsons["result"][i]["type"] == "古籍") {
                                    // htmllist += "<a target='_blank' onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "&title=" + StrReplace(jsons["result"][i]["title"]) + "\",\"0\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\");return false;'><img src='/images/ico51.png' /></a>";
                                } else if (jsons["result"][i]["type"] == "外文图书") {
                                    htmllist += "<a target='_blank' onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "&title=" + StrReplace(jsons["result"][i]["title"]) + "\",\"0\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;'><img src='/images/ico51.png' /></a>";
                                } else if (jsons["result"][i]["type"] == "外文期刊文章") {

                                } else {
                                    if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                        htmllist += "<a target='_blank' onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["id"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\")'><img src='/images/ico51.png' /></a>";
                                    }
                                }

                                htmllist += (temp[0]["downCount"] == null ? 0 : temp[0]["downCount"]) + "</td><td>";

                                if (jsons["result"][i]["type"] == "古籍") {
                                    htmllist += "<a target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "\",\"0\",\"" + jsons["result"][i]["classname"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + (changValue(jsons["result"][i]["num"]) != "暂无" ? jsons["result"][i]["num"] : "") + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\")'><img src='/images/ico5.png' /></a>";
                                } else if (jsons["result"][i]["type"] == "外文期刊文章") {
                                    if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                        htmllist += "<a target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["id"].replace("CASS", "") + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\")'><img src='/images/ico5.png' /></a>";
                                    }
                                } else if (jsons["result"][i]["type"] == "外文图书") {

                                } else {
                                    if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                        htmllist += "<a target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["id"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\")'><img src='/images/ico5.png' /></a>";
                                    }
                                }


                                htmllist += (temp[0]["readCount"] == null ? 0 : temp[0]["readCount"]) + "</td></tr>";
                            } else {
                                html += "<p class='number'>下载次数：<strong>0</strong>在线阅读：<strong>0</strong></p>";

                                htmllist += "<td class='hidden-xs'>";
                                if (jsons["result"][i]["type"] == "古籍") {

                                } else if (jsons["result"][i]["type"] == "外文期刊文章") {

                                } else if (jsons["result"][i]["type"] == "外文图书") {
                                    htmllist += "<a target='_blank' onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "&title=" + StrReplace(jsons["result"][i]["title"]) + "\",\"0\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;'><img src='/images/ico51.png' /></a>";
                                } else {
                                    if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                        htmllist += "<a target='_blank' onclick='AddHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",1,-1,\"/Literature/readurl?id=" + jsons["result"][i]["id"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'><img src='/images/ico51.png' /></a>";
                                    }
                                }
                                htmllist += "0</td><td>";
                                if (jsons["result"][i]["type"] == "古籍") {
                                    htmllist += "<a target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["barcodenum"] + "\",\"0\",\"" + jsons["result"][i]["classname"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + (changValue(jsons["result"][i]["num"]) != "暂无" ? jsons["result"][i]["num"] : "") + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\")'><img src='/images/ico5.png' /></a>";
                                } else if (jsons["result"][i]["type"] == "外文期刊文章") {
                                    htmllist += "<a target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["id"].replace("CASS", "") + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'><img src='/images/ico5.png' /></a>";
                                } else if (jsons["result"][i]["type"] == "外文图书") {

                                } else {
                                    if (changValue(jsons["result"][i]["id"]) != "暂无") {
                                        htmllist += "<a target='_blank' onclick='ViewHandleCount(this,\"" + jsons["result"][i]["type"] + "\",\"" + jsons["result"][i]["data_id"] + "\",-1,1,\"/Literature/readurl?id=" + jsons["result"][i]["id"] + "\",\"" + jsons["result"][i]["gch"] + "\",\"" + jsons["result"][i]["class"] + "\",\"" + StrReplace(jsons["result"][i]["title"]) + "\",\"" + jsons["result"][i]["creator"] + "\",\"" + "\");return false;' href='javascript:void(0);'><img src='/images/ico5.png' /></a>";
                                    }
                                }

                                htmllist += "0</td></tr>";
                            }
                            html += "</li>";

                            number++;
                        }

                    }
                }

                if (html.length > 0) {
                    $("#ul_articlelist").html(html);
                    $("#tab_articlelist").html(htmllist);
                }
            }
        });
    }
};

// 判断空各种情况
function isValidValue(val) {
    if (val === undefined || val === null || val === '' || val === 'null') {return false;}
    const validCharReg = /[a-zA-Z0-9\u4e00-\u9fa5\u3040-\u30FF\u3130-\u318F\u0E00-\u0E7F]/;
    if (typeof val === 'string') {
        const trimmedVal = val.trim();
        if (trimmedVal === '') {return false;}
        const arrayMatchList = trimmedVal.match(/\[[\s\S]*?\]/g);
        if (arrayMatchList) {
            return arrayMatchList.some(arrStr => {
                try {
                    const arr = JSON.parse(arrStr);
                    if (Array.isArray(arr)) {
                        return arr.some(item => {
                            if (typeof item === 'number' && !isNaN(item)) {
                                return true;
                            }
                            if (typeof item === 'string') {
                                const trimmedItem = item.trim();
                                return trimmedItem !== '' && trimmedItem !== 'null' && validCharReg.test(trimmedItem);
                            }
                            return false;
                        });
                    }
                } catch (e) {
                    return validCharReg.test(arrStr);
                }
                return false;
            });
        }
        return validCharReg.test(trimmedVal);
    }
    return true;
};

//记录检索日志
function addEsSearchLog(search, order, ajaxKeys) {
    var obj = {}, sType = getUrlParam("sType");
    obj.search = search;
    obj.sort = order;
    obj.sType = sType;
    obj.ajaxKeys = ajaxKeys;
    obj.customShowCondition = searchname;
    $.ajax({
        type: "POST",
        url: "/searchHandler/addEsSearchLog",
        data: obj,
        success: function (data) {
        }
    });
}

//检索返回结果数量
function searchcount(search, pageIndex, pageSize, order, ajaxKeys) {
    var obj = {}, sType = getUrlParam("sType");
    obj.search = search;
    obj.pageNum = 1;
    obj.pageSize = 1;
    obj.sort = null;
    $.ajax({
        type: "POST",
        url: "/searchHandler/search",
        data: obj,
        async: false,
        success: function (data) {
            if (data != "") {
                var jsons = data.data;
                if (jsons != null) {
                    // pages = jsons["pages"];
                    pages = jsons["total"];
                }
            }
        }
    });
}

//获取收录数据库名
function GetDatabaseCollectKind(ids) {
    var html = "";
    if (ids != null) {
        var obj = {};
        obj.lngCollectID = ids;
        $.ajax({
            type: "POST",
            url: "/searchHandler/getdatabasecollectkind",
            data: JSON.stringify(obj),
            contentType: "application/json; charset=utf-8",
            async: false,
            dataType: 'json',
            success: function (data) {
                var jsons = data.data;
                if (jsons != null) {
                    for (var i = 0; i < jsons.length; i++) {
                        html += "<a href='javascript:void(0)' style='margin-left: 5px;margin-right: 5px;'>" + jsons[i]["databaseName"] + "</a>";
                    }
                }
            }
        });
    }
    return html;
}

//处理solr返回的关键词
function GetKeyWord(value) {
    var html = "";
    var temp = "";
    if (!ms.util.isEmpty(value) && value.trim() != "") {
        temp = value.replace(/\[[^\]]+\]/g, "");
        var list = temp.split(';');
        for (var i = 0; i < list.length; i++) {
            html += "<font href='javascript:void(0)' style='margin-left: 5px;margin-right: 5px;'>" + list[i] + "</font>";
        }
    }
    return html;
}

//处理solr返回的作者
function GetCreatorlist(value) {
    var html = "";
    var temp = "";
    if (value != "null" && value != null && value != "" && typeof (value) != "undefined") {
        temp = formatBracketStr(value);
        var list = temp.split(';');
        var sousuobiaoti = ""
        if (searchname.indexOf("作者=") > -1 && searchname != '') {
            var indexs = searchname.indexOf("作者=");
            if (searchname.indexOf(" ") > -1) {
                var jpp = searchname.substring(indexs + 3, searchname.length).replace("\"", "").replace("\"", "").split(" ");
                sousuobiaoti = jpp[0].replace(/^\s+|\s+$/g, '')
            } else {
                var jpp = searchname.substring(indexs + 3, searchname.length).replace("\"", "").replace("\"", "");
                sousuobiaoti = jpp.replace(/^\s+|\s+$/g, '')
            }
        }
        for (var i = 0; i < list.length; i++) {
            if (searchname != '') {
                if (list[i].indexOf(sousuobiaoti) > -1) {
                    var reg2 = new RegExp(sousuobiaoti).toString()
                    var reg = reg2.replace(/\//g, '')
                    html += "<font href='javascript:void(0)' style='margin-left: 5px;margin-right: 5px;'>" + list[i].replace(reg, "<font color='red'><b>" + reg + "</b></font>") + "</font>";
                } else {
                    html += "<font href='javascript:void(0)' style='margin-left: 5px;margin-right: 5px;'>" + list[i] + "</font>";
                }
            } else {
                html += "<font href='javascript:void(0)' style='margin-left: 5px;margin-right: 5px;'>" + list[i] + "</font>";
            }
        }
    } else {
        html = "无";
    }
    return html;
}

function formatBracketStr(str, extractContent = false) {
    let res = str.trim();
    if (!res) return '';
    const spaceBracketReg = /\[\s+\]/g;
    const textFollowEmptyReg = /([^\[\]])\[\]/g;
    let prev = '';
    while (res !== prev) {
        prev = res;
        res = res.replace(spaceBracketReg, '[]');
        res = res.replace(textFollowEmptyReg, '$1');
        res = res.replace(/\[\]/g, '');
    }
    if (!res.trim()) {
        res = '[]';
    }
    if (extractContent) {
        const contentReg = /^\[(.*)\]$/;
        const match = res.match(contentReg);
        res = match ? match[1].trim() : res;
    }
    return res;
};

function isInvalidBracket(value) {
    if (typeof value === 'string') {
        const noSpaceStr = value.replace(/\s+/g, '');
        return noSpaceStr === '[]';
    }
    if (Array.isArray(value)) {
        if (value.length === 0) return true;
        return value.every(item => {
            if(typeof item === 'string' && item.trim() === '') {
                return '';
            }
        });
    }
    return value;
};

//处理作者超长
function GetCreatorlisthtml(value) {
    var html = "";
    var temp = "";
    if (value != "null" && value != null && value != "" && typeof (value) != "undefined") {
        temp = value.replace(/\[[\s\S]*?\]/g, "");
        var list = temp.split(';');
        var creaters = "";
        var textLength = 0;
        var maxTextLength = 10;
        for (var i = 0; i < list.length; i++) {
            var item = list[i].trim();
            if (item === "") continue;
            var itemText = item.replace(/<[^>]+>/g, "");
            var itemLen = itemText.length;
            if (textLength + itemLen <= maxTextLength) {
                if (creaters !== "") {
                    creaters += " ";
                }
                creaters += item;
                textLength += itemLen;
            } else if (textLength < maxTextLength) {
                var remainLength = maxTextLength - textLength;
                var truncatedItem = truncateWithTags(item, remainLength);
                if (creaters !== "") {
                    creaters += " ";
                }
                creaters += truncatedItem + "...";
                textLength = maxTextLength;
                break;
            } else {
                if (creaters !== "") {
                    creaters += "...";
                }
                break;
            }
        }
        if (creaters !== "") {
            html = "<span style='margin-left:5px;margin-right:5px;cursor:default;' title='" + GetCreatorlisttitle(value) + "'>" + creaters + "</span>";
        }
    }
    return html;
}

function truncateWithTags(htmlStr, maxChars) {
    var result = "";
    var charCount = 0;
    var inTag = false;
    var tagBuffer = "";
    for (var i = 0; i < htmlStr.length; i++) {
        var char = htmlStr[i];
        if (char === '<') {
            inTag = true;
            tagBuffer = char;
        } else if (char === '>') {
            inTag = false;
            tagBuffer += char;
            result += tagBuffer;
            tagBuffer = "";
        } else if (inTag) {
            tagBuffer += char;
        } else {
            if (charCount < maxChars) {
                result += char;
                charCount++;
            } else {
                break;
            }
        }
    }
    return result;
}

function GetCreatorlisttitle(value) {
    var temp = "";
    var fullText = "";

    if (value != "null" && value != null && value != "" && typeof (value) != "undefined") {
        temp = value.replace(/\[[\s\S]*?\]/g, "");
        var list = temp.split(';');

        for (var i = 0; i < list.length; i++) {
            var item = list[i].trim();
            if (item === "") continue;

            var itemText = item.replace(/<[^>]+>/g, "");

            if (fullText !== "") {
                fullText += " ";
            }
            fullText += itemText;
        }

        fullText = fullText.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
    }

    return fullText;
}

//处理solr返回的作者
function GetCreator(value) {
    var html = "";
    var temp = "";
    if (value != null) {
        temp = value.replace(/\[[^\]]+\]/g, "");
        var list = temp.split(';');
        html += "<a href='javascript:void(0)' style='margin-left: 5px;margin-right: 5px;'>" + list[0] + "</a>";
    }
    return html;
}

//获取下载量和阅读量
function Get_DowndorRead(type, articleid) {
    var obj = {};
    obj.type = type;
    obj.articleid = articleid;
    var temp = "";
    $.ajax({
        type: "POST",
        url: "/articlelistHandler/getdowndorread",
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(obj),
        async: false,
        success: function (data) {
            temp = data.data;
        }
    });
    return temp;
}

//批量获取下载量和阅读量
function getReadDown(idArr) {
    var temp = "";
    $.ajax({
        type: "POST",
        url: "/articlelistHandler/getdowndAndread",
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(idArr),
        async: false,
        success: function (data) {
            temp = data.data;
        }
    });
    return temp;
}

//转到详情页
function hrefinfo(obj) {
    var id = $(obj).attr("data-id");
    var type = $(obj).attr("data-name");
    var datatype = $(obj).attr("data-type");
    var typename = $(obj).attr("data-type");
    var synUpdateType = $(obj).attr("data-synUpdateType");
    var encryptedUrl = $(obj).attr("data-encryptedUrl");
    var barcodenum = "";
    if (datatype == "中文期刊文章") {
        datatype = "journalArticle";
    }
    if (datatype == "集刊文章") {
        datatype = "collectionsArticle";
    }
    if (datatype == "外文期刊文章") {
        datatype = "eJournalArticle";
    }
    if (datatype == "古籍") {
        barcodenum = $(obj).attr("data-barcodenum");
        datatype = "Ancient";
    }
    if (datatype == "外文图书") {
        barcodenum = $(obj).attr("data-id");
        datatype = "Book";
    }
    if (datatype == "方志") {
        datatype = "LocalRecords";
    }
    if (datatype == "会议论文") {
        datatype = "Conference";
    }
    if (datatype == "学位论文") {
        datatype = "Degree";
    }
    if (AntiSqlValid(id) == true && AntiSqlValid(type) == true && AntiSqlValid(datatype) == true && AntiSqlValid(typename) == true && AntiSqlValid(barcodenum) == true) {
        // window.open("/Literature/articleinfo?id=" + $.base64.encode(id, 'utf8') + "&type=" + $.base64.encode(datatype, 'utf8') + "&datatype=" + $.base64.encode(type, 'utf8') + "&typename=" + $.base64.encode(typename, 'utf8') + "&nav=" + nav + "&barcodenum=" + $.base64.encode(barcodenum, 'utf8'));
        window.open(encodeURI("/Literature/secure/articleinfo?params=" + encryptedUrl + "&pageUrl=" + encodeURIComponent(window.location.href)), '_blank')
    }
}

//获取url中的参数
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return decodeURI(r[2]);
    return null; //返回参数值
}

//添加检索日志
function AddSearchLog(search, searchname, pages) {
    if (AntiSqlValid(search) == true) {
        SearchLink = window.location.href;
        var obj = {};
        obj.search = search;
        obj.searchname = searchname;
        obj.pages = pages;
        obj.SearchLink = SearchLink;
        $.ajax({
            type: "POST",
            url: "/searchHandler/addsearchlog",
            data: JSON.stringify(obj),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {

            }
        });
    }
}

//在结果中检索
function result_Search() {
    var Rsearch = "";
    var RsearchName = "";
    var RajaxKeys = "";
    if ($("#txt_rsearch1").val().length > 0) {
        var temp = $("#select_R1").val();
        var txt_r = removeSpecialChars(addEscape($("#txt_rsearch1").val()));
        var txt_r_x_o = removeSpecialChars($("#txt_rsearch1").val());
        if (txt_r) {
            if (temp == "TS") {
                Rsearch = "(IKTE=\"" + txt_r + "\" OR IKPYTE=\"" + txt_r + "\" OR IKST=\"" + txt_r + "\" OR IKET=\"" + txt_r + "\" OR IKSE=\"" + txt_r + "\")";
                RsearchName = "题名/关键词=\"" + txt_r_x_o + "\"";
            } else if (temp == "TITE") {
                Rsearch = "(IKTE=" + txt_r + " OR IKPYTE=" + txt_r + " OR IKET=" + txt_r + ")";
                RsearchName = "题名=\"" + txt_r_x_o + "\"";
            } else if (temp == "CRTR") {
                Rsearch = "((CRTR=*" + txt_r + "* OR IKCE=\"" + txt_r + "\")" + " AND ik_creator:\"" + txt_r + "\"^20 OR (IKCRE=\"" + txt_r + "\"))";
                RsearchName = "作者=\"" + txt_r_x_o + "\"";
            } else if (temp == "IKST") {
                Rsearch = "(IKST=" + txt_r + " OR IKSE=" + txt_r + ")";
                RsearchName = "关键词=\"" + txt_r_x_o + "\"";
            } else if (temp == "ISSN") {
                Rsearch = "ISSN=*" + txt_r + "*";
                RsearchName = "ISSN=\"" + txt_r_x_o + "\"";
            }
            RajaxKeys += txt_r;
        }
    }
    if ($("#txt_rsearch2").val().length > 0) {
        var temp = $("#select_R2").val();
        var txt_r2 = removeSpecialChars(addEscape($("#txt_rsearch2").val()));
        var txt_r_x_t = removeSpecialChars($("#txt_rsearch2").val());
        if (Rsearch.length > 0) {
            if (txt_r2) {
                if (temp == "TS") {
                    Rsearch += " AND (IKTE=\"" + txt_r2 + "\" OR IKPYTE=\"" + txt_r2 + "\" OR IKST=\"" + txt_r2 + "\" OR IKET=\"" + txt_r2 + "\" OR IKSE=\"" + txt_r2 + "\")";
                    RsearchName += " 且 题名/关键词=\"" + txt_r_x_t + "\"";
                } else if (temp == "TITE") {
                    Rsearch += " AND (IKTE=" + txt_r2 + " OR IKPYTE=" + txt_r2 + " OR IKET=" + txt_r2 + ")";
                    RsearchName += "  且  题名=\"" + txt_r_x_t + "\"";
                } else if (temp == "CRTR") {
                    Rsearch += " AND (((CRTR=*" + txt_r2 + "* OR IKCE=\"" + txt_r2 + "\")" + " AND ik_creator:\"" + txt_r2 + "\"^20) OR (IKCRE=\"" + txt_r2 + "\"))";
                    RsearchName += "  且  作者=\"" + txt_r_x_t + "\"";
                } else if (temp == "IKST") {
                    Rsearch += " AND (IKST=" + txt_r2 + " OR IKSE=" + txt_r2 + ")";
                    RsearchName += "  且  关键词=\"" + txt_r_x_t + "\"";
                } else if (temp == "ISSN") {
                    Rsearch += " AND ISSN=*" + txt_r2 + "*";
                    RsearchName += "  且  ISSN=\"" + txt_r_x_t + "\"";
                }
                RajaxKeys += "," + txt_r2;
            }
        } else {
            if (txt_r2) {
                if (temp == "TS") {
                    Rsearch += " (IKTE=\"" + txt_r2 + "\" OR IKPYTE=\"" + txt_r2 + "\" OR IKST=\"" + txt_r2 + "\" OR IKET=\"" + txt_r2 + "\" OR IKSE=\"" + txt_r2 + "\")";
                    RsearchName += "题名/关键词=\"" + txt_r_x_t + "\"";
                } else if (temp == "TITE") {
                    Rsearch += "(IKTE=" + txt_r2 + " OR IKPYTE=" + txt_r2 + " OR IKET=" + txt_r2 + ")";
                    RsearchName += "题名=\"" + txt_r_x_t + "\"";
                } else if (temp == "CRTR") {
                    Rsearch += "((CRTR=*" + txt_r2 + "* OR IKCE=\"" + txt_r2 + "\")" + " AND ik_creator:\"" + txt_r2 + "\"^20) OR (IKCRE=\"" + txt_r2 + "\")";
                    RsearchName += "作者=\"" + txt_r_x_t + "\"";
                } else if (temp == "IKST") {
                    Rsearch += "(IKST=" + txt_r2 + " OR IKSE=" + txt_r2 + ")";
                    RsearchName += "关键词=\"" + txt_r_x_t + "\"";
                } else if (temp == "ISSN") {
                    Rsearch += "ISSN=*" + txt_r2 + "*";
                    RsearchName += "ISSN=\"" + txt_r_x_t + "\"";
                }
                RajaxKeys += txt_r2;
            }
        }
    }
    if ($("#date_Rstart").val().length > 0) {
        var time1 = new Date($("#date_Rstart").val());
        if ($("#date_Rend").val().length > 0) {
            var time2 = new Date($("#date_Rend").val());
            if (Rsearch.length > 0) {
                Rsearch += " AND DATE=[" + time1.format("yyyy-MM-ddThh:mm:ssZ") + " TO " + time2.format("yyyy-MM-ddThh:mm:ssZ") + "]";
            } else {
                Rsearch += " DATE=[" + time1.format("yyyy-MM-ddThh:mm:ssZ") + " TO " + time2.format("yyyy-MM-ddThh:mm:ssZ") + "]";
            }

            if (RsearchName.length > 0) {
                RsearchName += "且 时间=" + time1.format("yyyy-MM-dd") + " 至 " + time2.format("yyyy-MM-dd");
            } else {
                RsearchName += " 时间=" + time1.format("yyyy-MM-dd") + " 至 " + time2.format("yyyy-MM-dd");
            }

        } else {
            if (Rsearch.length > 0) {
                Rsearch += " AND DATE=[" + time1.format("yyyy-MM-ddThh:mm:ssZ") + " TO * ]";
            } else {
                Rsearch += " DATE=[" + time1.format("yyyy-MM-ddThh:mm:ssZ") + " TO * ]";
            }
            if (RsearchName.length > 0) {
                RsearchName += "且 时间=" + time1.format("yyyy-MM-dd") + " 至今";
            } else {
                RsearchName += " 时间=" + time1.format("yyyy-MM-dd") + " 至今";
            }

        }

    }
    if (Rsearch.length > 0) {
        Rsearch = where + " AND (" + Rsearch + ")";
        if (RsearchName.length > 0) {
            if (AntiSqlValid2(RsearchName) == true) {
                searchname = searchname + " 且 (" + RsearchName + ")";
            }
        }
        if (RajaxKeys && ajaxKeys) {
            RajaxKeys += ',' + ajaxKeys;
        } else if (ajaxKeys) {
            RajaxKeys = ajaxKeys;
        }

        if (AntiSqlValid(Rsearch) == true && AntiSqlValid(searchname) == true && AntiSqlValid(nav) == true) {
            Rsearch = $.base64.encode(Rsearch, 'utf8');
            searchname = $.base64.encode(searchname, 'utf8');

            var url = "/Literature/articlelist?sType=0&search=" + Rsearch + "&searchname=" + searchname + "&nav=" + nav;
            if (RajaxKeys) {
                RajaxKeys = $.base64.encode(RajaxKeys, 'utf8');
                url += "&ajaxKeys=" + RajaxKeys
            }

            window.location.href = url;
        }
    }
}

//检索返回按年分的组
function FacetYears(search, filed, limit) {
    var obj = {};
    obj.search = search;
    obj.filed = filed;
    obj.limit = limit;
    $.ajax({
        type: "POST",
        url: "/searchHandler/solrseachfacet",
        data: JSON.stringify(obj),
        async: false,
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (data) {
            var jsons = data.data;
            var html = "";
            if (jsons != null) {
                for (var i = 0; i < jsons.length; i++) {
                    if (jsons[i]["value"] > 0 && changValue2(jsons[i]["key"]) != "") {
                        for (var j = 0; j < jsons.length - 1 - i; j++) {
                            if (jsons[j]["key"] > jsons[j + 1]["key"]) { //相邻元素两两对比
                                var temp = jsons[j + 1]["key"]; //元素交换
                                jsons[j + 1]["key"] = jsons[j]["key"];
                                jsons[j]["key"] = temp;
                            }
                        }
                        html += "<li><tt>" + jsons[j]["value"] + "篇</tt><input data-type='Y' value='YEAR=\"" + jsons[j]["key"] + "\"' data-name='年份|" + jsons[j]["key"] + "' type='checkbox'><span>" + jsons[j]["key"] + "</span></li>";
                    }
                }
            }
            if (html.length > 0) {
                $("#u_years").html(html);
            } else {
                $("#face_years").hide();
            }

        }
    });
}

//检索返回文献类型分的组
function FacetType(search, filed, limit) {
    var obj = {};
    obj.search = search;
    obj.filed = filed;
    obj.limit = limit;
    $.ajax({
        type: "POST",
        url: "/searchHandler/solrseachfacet",
        data: JSON.stringify(obj),
        async: false,
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (data) {
            var jsons = data.data;
            var html = "";
            if (jsons != null) {
                for (var i = 0; i < jsons.length; i++) {
                    if (jsons[i]["value"] > 0 && changValue2(jsons[i]["key"]) != "") {
                        html += "<li><tt>" + jsons[i]["value"] + "篇</tt><input data-type='T' value='TYPE=\"" + jsons[i]["key"] + "\"' data-name='类型|" + jsons[i]["key"] + "'  type='checkbox'><span>" + jsons[i]["key"] + "</span></li>";
                    }
                }
            }
            if (html.length > 0) {
                $("#u_type").html(html);
            } else {
                $("#face_type").hide();
            }
        }
    });
}

//检索返回作者分的组
function FacetCreator(search, filed, limit) {
    var obj = {};
    obj.search = search;
    obj.filed = filed;
    obj.limit = limit;
    $.ajax({
        type: "POST",
        url: "/searchHandler/solrseachfacet",
        data: JSON.stringify(obj),
        contentType: "application/json; charset=utf-8",
        async: false,
        dataType: 'json',
        success: function (data) {
            var jsons = data.data;
            var html = "";
            if (jsons != null) {
                for (var i = 0; i < jsons.length; i++) {
                    //if (jsons[i]["Value"] > 0 && changValue2(jsons[i]["Key"]) != "") {
                    //    html += "<li><tt>" + jsons[i]["Value"] + "篇</tt><input data-type='C' value='CRTR=\"" + jsons[i]["Key"].split(',')[0] + "\"' data-name='作者|" + jsons[i]["Key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["Key"].split(',')[0] + "</span></li>";
                    //}
                    if (jsons[i]["value"] > 0 && changValue2(jsons[i]["key"]) != "") {
                        html += "<li><tt>" + jsons[i]["value"] + "篇</tt><input data-type='C' value='IKCE=\"" + jsons[i]["key"].split(',')[0] + "\"' data-name='作者|" + jsons[i]["key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["key"].split(',')[0] + "</span></li>";
                    }
                }
            }
            if (html.length > 0) {
                $("#u_creator").html(html);
            } else {
                $("#face_creator").hide();
            }
        }
    });
}

//检索返回期刊分的组
function FacetMedias(search, filed, limit) {
    var obj = {};
    obj.search = search;
    obj.filed = filed;
    obj.limit = limit;
    $.ajax({
        type: "POST",
        url: "/searchHandler/solrseachfacet",
        data: JSON.stringify(obj),
        contentType: "application/json; charset=utf-8",
        async: false,
        dataType: 'json',
        success: function (data) {
            var jsons = data.data;
            var html = "";
            if (jsons != null) {
                for (var i = 0; i < jsons.length; i++) {
                    //if (jsons[i]["Value"] > 0 && changValue2(jsons[i]["Key"]) != "") {
                    //    html += "<li><tt>" + jsons[i]["Value"] + "篇</tt><input data-type='C' value='CRTR=\"" + jsons[i]["Key"].split(',')[0] + "\"' data-name='作者|" + jsons[i]["Key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["Key"].split(',')[0] + "</span></li>";
                    //}
                    if (jsons[i]["value"] > 0 && changValue2(jsons[i]["key"]) != "") {
                        html += "<li><tt>" + jsons[i]["value"] + "篇</tt><input data-type='C' value='CNEM=\"" + jsons[i]["key"].split(',')[0] + "\"' data-name='期刊|" + jsons[i]["key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["key"].split(',')[0] + "</span></li>";
                    }
                }
            }
            if (html.length > 0) {
                $("#u_medias").html(html);
            } else {
                $("#face_medias").hide();
            }
        }
    });
}

//检索返回关键词分的组
function FacetKeyWordS(search, filed, limit) {
    var obj = {};
    obj.search = search;
    obj.filed = filed;
    obj.limit = limit;
    $.ajax({
        type: "POST",
        url: "/searchHandler/solrseachfacet",
        data: JSON.stringify(obj),
        contentType: "application/json; charset=utf-8",
        async: false,
        dataType: 'json',
        success: function (data) {
            var jsons = data.data;
            var html = "";
            if (jsons != null) {
                for (var i = 0; i < jsons.length; i++) {
                    //if (jsons[i]["Value"] > 0 && changValue2(jsons[i]["Key"]) != "") {
                    //    html += "<li><tt>" + jsons[i]["Value"] + "篇</tt><input data-type='C' value='CRTR=\"" + jsons[i]["Key"].split(',')[0] + "\"' data-name='作者|" + jsons[i]["Key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["Key"].split(',')[0] + "</span></li>";
                    //}
                    if (jsons[i]["value"] > 0 && changValue2(jsons[i]["key"]) != "") {
                        html += "<li><tt>" + jsons[i]["value"] + "篇</tt><input data-type='C' value='IKKS=\"" + jsons[i]["key"].split(',')[0] + "\"' data-name='关键词|" + jsons[i]["key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["key"].split(',')[0] + "</span></li>";
                    }
                }
            }
            if (html.length > 0) {
                $("#u_keyWords").html(html);
            } else {
                $("#face_keyWords").hide();
            }
        }
    });
}


//检索返回古籍分类的组
function FacetClassname(search, filed, limit) {
    var obj = {};
    obj.search = search;
    obj.limit = limit;
    obj.filed = filed;
    $.ajax({
        type: "POST",
        url: "/searchHandler/solrseachfacet",
        data: JSON.stringify(obj),
        contentType: "application/json; charset=utf-8",
        async: false,
        dataType: 'json',
        success: function (data) {
            var jsons = data.data;
            var html = "";
            if (jsons != null) {
                for (var i = 0; i < jsons.length; i++) {
                    if (jsons[i]["value"] > 0 && changValue2(jsons[i]["key"]) != "") {
                        html += "<li><tt>" + jsons[i]["value"] + "篇</tt><input data-type='G' value='CLNE=\"" + jsons[i]["key"].split(',')[0] + "\"' data-name='分类|" + jsons[i]["key"].split(',')[0] + "' type='checkbox'><span>" + jsons[i]["key"].split(',')[0] + "</span></li>";
                    }
                }
            }
            if (html.length > 0) {
                $("#u_classname").html(html);
            } else {
                $("#face_classname").hide();
            }
        }
    });
}

//防止SQL注入
function AntiSqlValid2(text) {
    re = /select |update |insert |delete |exec |count |;|>|<|%/i;
    var temp = true;
    if (re.test(text)) {
        temp = false;
    }
    return temp;
}

//中图分类展示
function ShowClass(obj) {
    var temp = $(obj).find("img").attr("data-type");
    if (temp == "add") {
        $(obj).find("img").attr("src", "/images/small-hide.png");
        $(obj).find("img").attr("data-type", "hide");
        $(obj).parent().next().show();
    }
    if (temp == "hide") {
        $(obj).find("img").attr("src", "/images/samll-add.png");
        $(obj).find("img").attr("data-type", "add");
        $(obj).parent().next().hide();
    }

}

//点击分类查询
function clickClass(values) {
    var sear = " AND CLAS=" + values + "*";
    var sname = " 且 分类号=\"" + values + "\"";

    if (AntiSqlValid(sear) == true && AntiSqlValid(sname) == true) {
        number = 1;
        pages = 0;
        $("#Hid_class").attr("data-value", sear);
        searchcount(where + sear, 1, nums, order);
        AddSearchLog(where + sear, searchname + sname, pages);
        var allpages = Math.ceil(pages / nums);//总页数
        layui.use(['laypage'], function () {
            var laypage = layui.laypage;
            //调用分页
            laypage({
                cont: 'page'
                , pages: allpages //得到总页数
                , skip: true
                , jump: function (obj) {
                    number = ((obj.curr - 1) * nums) + 1;
                    if (obj.curr == allpages) {//判断是否是最后一页
                        $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + pages);
                    } else {
                        $("#lbl_pagenumber").html(((obj.curr - 1) * nums) + 1 + "-" + obj.curr * nums);
                    }
                    search(where + sear, obj.curr, nums, order);
                    $('body,html').animate({scrollTop: 0}, 1000); //1000代表1秒时间回到顶点
                }
            });
        });
        $("#lbl_numbers").html(pages);
        $("#searchname").html(searchname + sname);
    }
}

//防止SQL注入
function AntiSqlValid2(text) {
    re = /select |update |insert |delete |exec |count |;|>|<|%/i;
    var temp = true;
    if (re.test(text)) {
        temp = false;
    }
    return temp;
}

//处理特殊字符
function StrReplace(str) {
    return str.replace(/<\/?.+?>/g, "").replace(/\"/g, '“').replace(/\'/g, '‘').replace(/,/g, '').replace(/[&\|\\\*^%$#@\-]/g, "").replace(/[\'\"\\\/\b\f\n\r\t]/g, '');
}
