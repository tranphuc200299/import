/*------------------------------------------------------------------
Project:    importCFS
Version:    0.1
Last change:    03/01/2023
Author: phuong.c
-------------------------------------------------------------------*/

let handle_event;
$(function () {
    "use strict";

    /*--------------------------------------------------------
     * FORM
    ----------------------------------------------------------*/
    const gSetField = $("#gSetField").val()
    if (gSetField) {
        if ($(`#${gSetField}`).length) {
            $(`#${gSetField}`).focus()
        }
    }

    /*--------------------------------------------------------
     * POPUP
    ----------------------------------------------------------*/
    /*
     * Get the button that opens the modal
     */
    $(document).on('click', '[data-toggle="modal"]', function (e) {
        e.preventDefault()
        let modalSelection = $(this).data('target')
        $(modalSelection).show()
    })

    $('.modal').on('click', '#btnClose, .popClose', function (e) {
        e.preventDefault()
        $(this).closest('.modal').hide()
    })


    $(".datepicker").datepicker({
        changeMonth: true,
        changeYear: true,
        closeText: '閉じる',
        prevText: '前',
        nextText: '次',
        currentText: '今日',
        monthNames: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        monthNamesShort: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        dayNames: ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日'],
        dayNamesShort: ['日', '月', '火', '水', '木', '金', '土'],
        dayNamesMin: ['日', '月', '火', '水', '木', '金', '土'],
        weekHeader: '週',
        dateFormat: 'yy/mm/dd',
        firstDay: 0,
        isRTL: false,
        showMonthAfterYear: true,
        yearSuffix: '年',
        showButtonPanel: true,
        yearRange: "1970:2100"
    });

    /*--------------------------------------------------------
     * Change text
    ----------------------------------------------------------*/
    handle_event = function (input_ids, event_type) {
        const csrf_token = $("input[name=csrfmiddlewaretoken]").val();
        const data = {
            'csrfmiddlewaretoken': csrf_token,
            'action': `${input_ids[0]}_` + event_type
        };
        for (let i = 0; i < input_ids.length; i++) {
            const value = $(`#${input_ids[i]}`).val();
            data[input_ids[i]] = value
        }
        $.ajax({
            url: "",
            data: data,
            type: 'post'
        }).done(function (responseData) {
            const keys = Object.keys(responseData)
            for (const index in keys) {
                let key = keys[index];
                let value;
                if (key == "gSetField") {
                    value = responseData.gSetField
                    $(`#${'gSetField'}`).focus()
                    $(`#${'gSetField'}`).val(value)
                } else {
                    value = responseData[key]
                    if (key.startsWith("cmd")) {
                        key = key.replace("_enable", "")
                        if (value == "False") {
                            $(`#${key}`).attr("disabled", "disabled");
                            $(`#${key}`).addClass("inactive")
                            $(`#${key}_enable`).val("False")

                        } else {
                            $(`#${key}`).removeAttr("disabled");
                            $(`#${key}`).removeClass("inactive")
                            $(`#${key}_enable`).val("True")
                        }
                    } else {
                        if (key == "MsgDsp") {
                            document.getElementById("modalTitle").innerHTML = value.title;
                            document.getElementById("modalBody").innerHTML = value.msg;
                            $("#modalInfo").show()
                        }
                        else
                        {
                            $(`#${key}`).val(value)
                        }
                    }
                }
            }
        }).fail(function () {
            console.log('Get data failed');
        });
    }
})
