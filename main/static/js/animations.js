$(document).ready(function(){

    $('#confirmDeliveryLoading').hide('')
    $('.loader').hide('')

    $('.datetimepicker1').datetimepicker({
      pickTime: false,
      format: 'MM / dd / yyyy'
    });

    var item = $('.item');
    item.css('height',item.width() - 10);

    $('body').keydown(function(e){
        if (!$(".modal").hasClass('in')){
            $('.search-box').focus();
            if (!$(".search-box").is(':focus')) {
                $(".search-box").val('');
            }
        }
    });

   $('#historyPicker').datetimepicker().on('changeDate', function(e) {
        search_history($('#searchHistory').val());
    });

   $('#salePicker').datetimepicker().on('changeDate', function(e) {
        search_sale($('#searchSale').val());
    });

    $('#qtyPlus').on('click', function () {
        var current_qty = $('#quantity').val();
        var current_stock = $('#qtyStock').html();
        
        if (parseInt(current_qty) < parseInt(current_stock)){
            var new_qty = parseInt(current_qty) + 1;
            $('#quantity').val(new_qty);
        }
    });

    $('#qtyMinus').on('click', function () {
        var current_qty = $('#quantity').val();
        if (current_qty > 1){
            var new_qty = parseInt(current_qty) - 1;
            $('#quantity').val(new_qty);
        }
    });

    $('#customerName').on('keyup', function () {
        if ($('#customerName').val() != ''){
            $('.payment-selection-cover').hide();
        }
        else{
            $('.payment-selection-cover').show();
        }
    });

    $('#amountTendered').on('keyup', function () {
        compute_change();
    });

    $('#amountTendered').on('change', function () {
        compute_change();
    });

    $('#deliveryAmountTendered').on('keyup', function () {
        compute_delivery_change();
    });

    $('#deliveryAmountTendered').on('change', function () {
        compute_delivery_change();
    });

    $('#payAmountTendered').on('keyup', function () {
        compute_pay_change()
    });

    $('#payAmountTendered').on('change', function () {
        compute_pay_change()
    });

    $('#cashTransactionModal').on('hidden.bs.modal', function () {
        $('#amountTendered').val('');
        $('#amountTendered').change();
    });

    $('#deliveryModal').on('hidden.bs.modal', function () {
        $('#deliveryAmountTendered').val('');
        $('#deliveryAmountTendered').change();
    });

    $('#paymentSelectionModal').on('shown.bs.modal', function () {
        $('#customerName').focus();
    });

    $('#useLoyaltyModal').on('shown.bs.modal', function () {
        $('#loyaltyCardNo').focus();
    });

    $('#cardPaymentModal').on('shown.bs.modal', function () {
        $('#cardPaymentInput').focus();
    });

    $('#addToExisting').on('click', function () {
        show_existing_transactions();
    });

    $('#paymentSelectionModal').on('hidden.bs.modal', function () {
        $('#customerName').val('');
        $('.payment-selection-cover').show();
    });

    $('#addItemConsumptionModal').on('hidden.bs.modal', function () {
        $('#newItemQty').val('');
        $('#itemConsumptionSelect').val('').selectpicker('refresh');
    });

    $('.add-item-consumption-modal-body').find('.form-control').on('change', function () { 
        /*var name = $('#newProductName').val();
        var category = $('#newProductCategory').val();
        var price = $('#newProductPrice').val();
        var markup = $('#newProductMarkup').val();*/
        var item = $('#itemConsumptionSelect').find("option:selected").val();
        var consumption = $('#newItemQty').val();

        if ((item != '') && (consumption != '') && (!isNaN(consumption))){
            $('#saveConsumption').attr('disabled',false);
        }
        else{
            $('#saveConsumption').attr('disabled',true);   
        }
    });

    $('.add-item-consumption-modal-body').find('.form-control').on('keyup', function () { 
        var item = $('#itemConsumptionSelect').find("option:selected").val();
        var consumption = $('#newItemQty').val();

        if ((item != '') && (consumption != '') && (!isNaN(consumption))){
            $('#saveConsumption').attr('disabled',false);
        }
        else{
            $('#saveConsumption').attr('disabled',true);   
        }
    });

    $('#saveConsumption').on('click', function () {
        $('#saveConsumption').attr('disabled',true);
        var item = $('#itemConsumptionSelect').find("option:selected").val();
        var consumption = $('#newItemQty').val();
        save_item_consumption(item,consumption);
    });

    $('#newProductModal').on('hidden.bs.modal', function () {
        clear_consumption_items();
    });

    $('.new-product-input-container').find('.form-control').on('keyup', function () { 
        var name = $('#newProductName').val();
        var category = $('#newProductCategory').val();
        var price = $('#newProductPrice').val();
        var markup = $('#newProductMarkup').val();

        validate_product(name,category,price,markup);
    });

    $('#saveProductBtn').on('click', function () {
        var name = $('#newProductName').val();
        var category = $('#newProductCategory').val();
        var price = $('#newProductPrice').val();
        var markup = $('#newProductMarkup').val();

        save_product(name,category,price,markup);
    });

    $('#walletTransactionModal').on('hidden.bs.modal', function () {
        $('#ewalletFormContainer').html(`
            <div class="loader" id="ewalletLoading">
                <img src="../static/images/assets/loading.gif">
            </div>
            <div>
                <div>
                <label for="amountTendered">Please tap ID onto reader:</label>
                </div>
            </div><br />
            <div>
                <form id="walletForm2" onsubmit="get_ewallet_info(event)">
                    <input autocomplete="off" type="password" id="walletId" class="form-control" placeholder="ID number">
                </form>
            </div>
        `)
        $('.loader').hide();
        $('#walletId').focus();
        $('#walletDoneBtn').attr('disabled', true);
    });

})