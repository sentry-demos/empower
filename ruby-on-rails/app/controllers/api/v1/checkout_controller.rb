#require 'json'

class Api::V1::CheckoutController < ApplicationController
  def index
    # get Sentry tags in application_controller.rb
    set_Sentry_tags 

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")
    span_read_params = transaction.start_child(op: "custom.read_params")

    total = ""
    cart_contents = Hash.new
    params.each do |key, value|
      if key.to_s == "cart"
        value.each do |key2, value2|
         if key2.to_s == "quantities"
           value2.each do | product_id, product_quantity |
             cart_contents[product_id.to_s] = product_quantity.to_s
           end
         elsif key2.to_s == "total"
           total = value2.to_s
         end
        end
      end
    end

    span_read_params.finish

    #default message, rewritten if exception
    logged = "Thanks for your order. Total cost is $" + total 

    span_inventory_call = transaction.start_child(op: "custom.inventory_db_call")
    products_in_inventory = Inventory.all()
    span_inventory_call.finish


    span_logic = transaction.start_child(op: "custom.inventory_vs_cart_logic")

    unless enough_inventory?(cart_contents)
      logged = "Error: Not enough inventory for productid #{cart_contents.keys.first}"
      Sentry.capture_message(logged, extra: { 
        cart_contents: cart_contents,
        inventory_state: products_in_inventory.as_json
      })
      render json: {"message": logged}, status: 400 and return
    end

    span_logic.finish
    render json: {"message": logged}, status: 200
  end

  private

  def enough_inventory?(cart_contents)
    cart_contents.all? do |product_id, requested_quantity|
      inventory = Inventory.find_by(product_id: product_id)
      inventory && inventory.count >= requested_quantity.to_i
    end
  end
end