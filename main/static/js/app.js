/*------------------------------------------------------------------
Project:    importCFS
Version:    0.1
Last change:    03/01/2023
Author: phuong.c
-------------------------------------------------------------------*/


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
        monthNames: ['1月','2月','3月','4月','5月','6月', '7月','8月','9月','10月','11月','12月'],
        monthNamesShort: ['1月','2月','3月','4月','5月','6月', '7月','8月','9月','10月','11月','12月'],
        dayNames: ['日曜日','月曜日','火曜日','水曜日','木曜日','金曜日','土曜日'],
        dayNamesShort: ['日','月','火','水','木','金','土'],
        dayNamesMin: ['日','月','火','水','木','金','土'],
        weekHeader: '週',
        dateFormat: 'yy/mm/dd',
        firstDay: 0,
        isRTL: false,
        showMonthAfterYear: true,
        yearSuffix: '年',
        showButtonPanel: true,
        yearRange: "1970:2100"
    });
})
