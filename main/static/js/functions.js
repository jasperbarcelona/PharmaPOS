var item_array = {};

function search_items(keyword){
  $.post('/item/search',{
    keyword:keyword
  },
  function(data){
    if (!keyword == ''){
      $('.items-container').html(data)
    }
    else{
      $('#itemTab').html(data)
    }
    var item = $('.item');
    item.css('height',item.width() - 10);
  });
}

function new_item(){
  var name = $('#newItemName').val();
  var stock = $('#newItemStock').val();
  $.post('/items/new',{
    name:name,
    stock:stock
  },
  function(data){
    $('.new-item-modal-body').find('.form-control').val('');
    $('#newItemModal').modal('hide');
    $('.inventory-table-container').find('table').find('tbody').html(data['template']);
    $('#itemConsumptionSelect').html(data['options']);
    $('.selectpicker').selectpicker('refresh');
  });
}

function use_loyalty(){
  var card_no = $('#loyaltyCardNo').val()
  $.post('/loyalty/use',{
    card_no:card_no
  },
  function(data){
    $('#useLoyaltyModal').modal('hide');
  });
}

function search_inventory(keyword){
  $.post('/inventory/search',{
    keyword:keyword
  },
  function(data){
    $('.inventory-table-container').find('table').find('tbody').html(data);
  });
}

function search_history(date){
  $.post('/history/search',{
    date:date
  },
  function(data){
    $('.history-container').html(data);
  });
}

function search_sale(date){
  $.post('/sale/search',{
    date:date
  },
  function(data){
    $('.sales-table-container').html(data);
  });
}

function open_product_qty(id){
  $.post('/item/qty/get',{
      product_id:id
  },
  function(data){
    if (data['item_stock'] > 0){
      $('#quantity').val(1);
      $('#orderBtn').attr('disabled',false);
    }
    else{
      $('#quantity').val(0);
      $('#orderBtn').attr('disabled',true);
    }
    $('.qty-modal-header').html(data['item_name']);
    $('.product-details-container').html(data['template']);
  });
}

function add_product(){
  var qty = $('#quantity').val();
  var options_id = [];
  var options_name = [];

  options_id.push($('#Drink :selected').val());
  options_name.push($('#Drink :selected').text());

  options_id.push($('#Sauce :selected').val());
  options_name.push($('#Sauce :selected').text());

  test_func(qty,options_id,options_name)
}

function test_func(qty,options_id,options_name){
  $.post('/item/order/add',{
    qty:qty,
    options_id:options_id,
    options_name:options_name
  },
  function(data){
    $('.no-transaction').hide();
    $('#qtyModal').modal('hide');
    $('.transaction-panel-body').html(data['transaction_template']);
    $('#inventoryTab').html(data['inventory_template']);
    $('.sales-table-container').html(data['sales_template']);
    $('#currentTransactionPanel').find('.panel-footer').find('button').attr('disabled',false);
  });
}

function get_item_to_delete(id){
  $.post('/item/delete/get',{
      product_id:id
  },
  function(data){
    $('.delete-item-name').html(data['product_name']);
  });
}

function get_item_to_delete_transaction(id){
  $('#transactionInfoModal').modal('hide');
  $.post('/transaction/item/delete/get',{
      product_id:id
  },
  function(data){
    $('.delete-transaction-item-name').html(data['product_name']);
  });
}

function delete_from_transaction(id){
  $('#deleteFromTransactionModal').modal('hide');
  $.post('/transaction/item/delete',{
      product_id:id
  },
  function(data){
    $('#inventoryTab').html(data['inventory_template']);
    $('.sales-table-container').html(data['sales_template']);
    $('.history-container').html(data['history_template']);
    $('#transactionInfoBody').html(data['transaction_info_template']);
    $('#transactionInfoModal').modal('show');
  });
}


function delete_from_order(){
  $.post('/item/delete',
  function(data){
    if (data['item_count'] < 1){
          $('#currentTransactionPanel').find('.panel-footer').find('button').attr('disabled',true);
    }
    $('#deleteOrderModal').modal('hide');
    $('.transaction-panel-body').html(data['transaction_template']);
    $('#inventoryTab').html(data['inventory_template']);
    $('.sales-table-container').html(data['sales_template']);
  });
}

function cancel_transaction(){
  $.post('/transaction/cancel',
  function(data){
    $('#cancelTransactionModal').modal('hide');
    $('.transaction-panel-body').html(data);
    $('#currentTransactionPanel').find('.panel-footer').find('button').attr('disabled',true);
  });
}

function get_amount_tendered(){
  $.post('/transaction/cash/amount',
  function(data){
    $('#cashTotal').html(data['total']);
    $('#paymentSelectionModal').modal('hide');
    $('#cashTransactionModal').modal('show');
    $('#amountTendered').val('');
    $('#amountTendered').change();
    setTimeout(function() {
      $('#amountTendered').focus();
    }, 500);
  });
}

function get_ewallet_info(e){
  e.preventDefault();
  $('#ewalletLoading').show();
  var id_no = $('#walletId').val();
  $.post('/ewallet/info',{
    id_no:id_no
  },
  function(data){
    $('#ewalletFormContainer').html(data['template']);
    var total = $('#walletTotal').html();
    if (parseFloat(data['credits']) >= parseFloat(total)){
      $('#availableCredits').css('color','green');
      $('#walletDoneBtn').attr('disabled', false);
    }
    else{
      $('#availableCredits').css('color','#d9534f');
      $('#walletDoneBtn').attr('disabled', true);
    }
  });
}

function get_ewallet(){
  $.post('/transaction/cash/amount',
  function(data){
    $('#walletTotal').html(data['total']);
    $('#paymentSelectionModal').modal('hide');
    $('#walletTransactionModal').modal('show');
    $('#walletId').val('');
    $('#walletId').change();
    setTimeout(function() {
      $('#walletId').focus();
    }, 500);
  });
}

function delivery_amount_tendered(){
  var customer_name = $('#customerName').val()
  $.post('/transaction/cash/amount',{
    customer_name:customer_name
  },
  function(data){
    $('#deliveryCashTotal').html(data['total']);
    $('#paymentSelectionModal').modal('hide');
    $('#deliveryModal').modal('show');
    $('#deliveryAmountTendered').val('');
    $('#deliveryAmountTendered').change();
    setTimeout(function() {
      $('#deliveryAmountTendered').focus();
    }, 500);
  });
}

function compute_change(){
  var due = $('#cashTotal').html();
  var tendered = $('#amountTendered').val();
  if (tendered == ''){
    var change = 0
  }
  else{
    var change = parseFloat(tendered) - parseFloat(due);
  }
  if (parseFloat(tendered) >= parseFloat(due)){
    $('#changeDue').css('color','green');
    $('.changePhp').css('color','green');
    $('#tenderedDoneBtn').attr('disabled',false);
  }
  else{
    $('#changeDue').css('color','red');
    $('.changePhp').css('color','red');
    $('#tenderedDoneBtn').attr('disabled',true);
  }
  $('#changeDue').html(change);
}

function compute_delivery_change(){
  var due = $('#deliveryCashTotal').html();
  var tendered = $('#deliveryAmountTendered').val();
  if (tendered == ''){
    var change = 0
  }
  else{
    var change = parseFloat(tendered) - parseFloat(due);
  }
  if (parseFloat(tendered) >= parseFloat(due)){
    $('#deliveryChangeDue').css('color','green');
    $('.changePhp').css('color','green');
    $('#deliveryTenderedDoneBtn').attr('disabled',false);
  }
  else{
    $('#deliveryChangeDue').css('color','red');
    $('.changePhp').css('color','red');
    $('#deliveryTenderedDoneBtn').attr('disabled',true);
  }
  $('#deliveryChangeDue').html(change);
}

function compute_pay_change(){
  var due = $('#payTotal').html();
  var tendered = $('#payAmountTendered').val();
  if (tendered == ''){
    var change = 0
  }
  else{
    var change = parseFloat(tendered) - parseFloat(due);
  }
  if (parseFloat(tendered) >= parseFloat(due)){
    $('#paychangeDue').css('color','green');
    $('.changePhp').css('color','green');
    $('#laterDoneBtn').attr('disabled',false);
  }
  else{
    $('#paychangeDue').css('color','red');
    $('.changePhp').css('color','red');
    $('#laterDoneBtn').attr('disabled',true);
  }
  $('#paychangeDue').html(change);
}

function pay_later(){
  var customer_name = $('#customerName').val()
  $.post('/transaction/finish/later',{
    customer_name:customer_name
  },
  function(data){
    if (data['status'] == 'success'){
      $('#paymentSelectionModal').modal('hide');
      $('#successModal').modal('show');
      $('.transaction-panel-body').html(data['transaction_template']);
      $('.history-container').html(data['history_template']);
      $('#finishTransactionBtn').attr('disabled',true);
      $('#cancelTransactionBtn').attr('disabled',true);
    }
  });
}

function finish_cash_transaction(){
  var tendered = $('#amountTendered').val();
  $.post('/transaction/finish/cash',{
    tendered:tendered
  },
  function(data){
    if (data['status'] == 'success'){
      $('#cashTransactionModal').modal('hide');
      $('#successModal').modal('show');
      $('.transaction-panel-body').html(data['transaction_template']);
      $('.history-container').html(data['history_template']);
      $('#finishTransactionBtn').attr('disabled',true);
    }
  });
}

function finish_wallet_transaction(){
  $('#walletDoneBtn').button('loading');
  $.post('/transaction/finish/wallet',
  function(data){
    if (data['status'] == 'success'){
      $('#walletTransactionModal').modal('hide');
      $('#successModal').modal('show');
      $('.transaction-panel-body').html(data['transaction_template']);
      $('.history-container').html(data['history_template']);
      $('#finishTransactionBtn').attr('disabled',true);
      $('#walletDoneBtn').button('complete');
    }
    else{
      $('#walletDoneBtn').button('complete');
    }
  });
}

function show_existing_transactions(){
  $.post('/transaction/existing',
  function(data){
    $('#addToExistingModalBody').html(data);
    $('#paymentSelectionModal').modal('hide');
    $('#addToExistingModal').modal('show');
  });
}

function show_points(id){
  $.post('/loyalty/points',{
    id:id
  },
  function(data){
    $('#loyaltyModalBody').html(data['template']);
    $('#loyaltyModalHeader').html('Card No: ' + data['card_no']);
  });
}

function finish_pay_transaction(id){
  var tendered = $('#payAmountTendered').val();
  $.post('/transaction/finish/later/pay',{
    tendered:tendered
  },
  function(data){
    if (data['status'] == 'success'){
      $('#payTransactionModal').modal('hide');
      $('#transactionInfoModal').modal('hide');
      $('#successModal').modal('show');
      $('.history-container').html(data['history_template']);
    }
  });
}

function refresh(){
  $.post('/order/list/update',
  function(data){
    $('.order-list-container').html(data);
    setTimeout(refresh,5000);
  });
}

function order_status(id,status){
  $.post('/order/status/update',{
    id:id,
    status:status
  },
  function(data){
    $('.order-list-container').html(data);
  });
}

function get_transaction_info(id){
  $.post('/transaction/info',{
    id:id,
  },
  function(data){
    $('#transactionInfoBody').html(data);
  });
}

function get_tendered_later(id){
  $.post('/transaction/later/amount',{
    id:id
  },
  function(data){
    $('#payTotal').html(data['total']);
    $('#payAmountTendered').val('');
    $('#payAmountTendered').change();
    setTimeout(function() {
      $('#payAmountTendered').focus();
    }, 500);
  });
}

function save_transaction_id(id){
  $.post('/transaction/id/save',{
    id:id
  },
  function(data){
    $('#confirmExistingName').html(data['customer_name']);
    $('#confirmExistingTotal').html('&#8369; ' + data['total']);
    $('#addToExistingModal').modal('hide');
    $('#addToExistingConfirm').modal('show');
  });
}

function add_orders_to_existing(){
  $.post('/transaction/existing/add',
  function(data){
    $('#addToExistingConfirm').modal('hide');
    $('#successModal').modal('show');
    $('.transaction-panel-body').html(data['transaction_template']);
    $('.history-container').html(data['history_template']);
    $('#finishTransactionBtn').attr('disabled',true);
    $('#cancelTransactionBtn').attr('disabled',true);
  });
}

function update_history(){
  $.post('/transaction/history/get',
  function(data){
    $('.history-container').html(data['history_template']);
  });
}

function void_transaction(id){
  $.post('/transaction/void/id',{
    id:id
  },
  function(data){
  });
}

function void_transaction_confirmed(){
  $.post('/transaction/void/confirm',
  function(data){
    $('.history-container').html(data['history_template']);
    $('#voidPasswordModal').modal('hide');
    $('.sales-table-container').html(data['sales_template']);
    $('#transactionInfoModal').modal('hide');
  });
}

function get_item_to_adjust(id){
  $.post('/item/adjust/get',{
    item_id:id
  },
  function(data){
    $('#currentStock').html(data['current_stock']);
    $('#adjustItemName').html(data['item_name']);
  });
}

function delete_item(){
  var plus = $('#addText').val();
  var minus = $('#subtractText').val();
  if (plus == ''){
    plus = 0;
  }
  if (minus == ''){
    minus = 0;
  }
  $.post('/item/delete',
  function(data){
    if (data['status'] == 'success'){
      $('#inventoryTab').html(data['inventory_template']);
      $('#adjustmentModal').modal('hide');
      $('#addText').val('');
      $('#subtractText').val('');
    }
  });
}

function adjust_stock(){
  var plus = $('#addText').val();
  var minus = $('#subtractText').val();
  if (plus == ''){
    plus = 0;
  }
  if (minus == ''){
    minus = 0;
  }
  $.post('/item/adjust',{
    plus:plus,
    minus:minus
  },
  function(data){
    if (data['status'] == 'success'){
      $('#inventoryTable').find('#'+data['item_id']).find('.stock-td').html(data['new_stock']);
      $('#adjustmentModal').modal('hide');
      $('#addText').val('');
      $('#subtractText').val('');
    }
  });
}

function get_delivery_data(){
  $.post('/delivery/data/get',
  function(data){
    $('.delivery-data-body').html(data);
    $('.delivery-loading-container').hide();
  });
}

function confirm_delivery(transaction_id){
  var transaction_name = $('#activeOrdersTable').find('tbody').find('#'+transaction_id).find('.delivery-name').html();
  $.post('/delivery/transaction/save',{
    transaction_id:transaction_id,
    transaction_name:transaction_name
  },  
  function(data){
    $('#confirmDeliveryName').html(data['customer_name']);
    $('#confirmDeliveryModal').modal('show');
  });
}

function add_orders_to_delivery(){
  $('#confirmDeliveryBtn').attr('disabled',true);
  $('#confirmDeliveryLoading').show();
  var tendered = $('#deliveryAmountTendered').val();
  $.post('/delivery/add',{
    tendered:tendered
  },
  function(data){
    if (data['status'] == 'failed'){
      $('#confirmDeliveryModalBody').html(data['error']);
      $('#confirmDeliveryLoading').hide();
      $('#confirmDeliveryBtn').attr('disabled',false);
    }
    else{
      $('#confirmDeliveryLoading').hide();
      $('.modal').modal('hide');
    }
  })
}

function items_add_row(){
  $.post('/row/add',
  function(data){
    $('#item_allocation_container').append(data);
    $('.selectpicker').selectpicker();
  })
}

function add_item_alloc(item_id,consumption){
  item_array[item_id] = consumption;
}

function save_item_consumption(item_id,consumption){
  $.post('/consumption/new',{
    item_id:item_id,
    consumption:consumption
  },
  function(data){
    $('#addItemConsumptionModal').modal('hide');
    $('#itemAllocationTable').html(data);

    var name = $('#newProductName').val();
    var category = $('#newProductCategory').val();
    var price = $('#newProductPrice').val();
    var markup = $('#newProductMarkup').val();

    validate_product(name,category,price,markup);
  })
}

function delete_consumption(item_id){
  $.post('/consumption/delete',{
    item_id:item_id
  },
  function(data){
    $('#itemAllocationTable').html(data);

    var name = $('#newProductName').val();
    var category = $('#newProductCategory').val();
    var price = $('#newProductPrice').val();
    var markup = $('#newProductMarkup').val();

    validate_product(name,category,price,markup);
  })
}

function clear_consumption_items(){
  $.post('/consumption/clear',
  function(data){
    $('#itemAllocationTable').html(data);
    $('.new-product-input-container').find('.form-control').val('');
  })
}

function validate_product(name,category,price,markup){
  if ((name != '') && (category != '') && (price != '') && (markup != '') && 
     (!isNaN(price)) && (!isNaN(markup)) && ($('#notEmpty').val() == 'not_empty')){
      $('#saveProductBtn').attr('disabled',false);
  }
  else{
      $('#saveProductBtn').attr('disabled',true);   
  }
}

function save_product(name,category,price,markup){
  $.post('/products/new',{
    name:name,
    category:category,
    price:price,
    markup:markup
  },
  function(data){
    $('#newProductModal').modal('hide');
    $('#itemTab').html(data);
    var item = $('.item');
    item.css('height',item.width() - 10);
  })
}

function get_items(){
  $.post('/items/get',
  function(data){
    $('#itemConsumptionSelect').html(data);
    $('.selectpicker').selectpicker('refresh');
  })
}