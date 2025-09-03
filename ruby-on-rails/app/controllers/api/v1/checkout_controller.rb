#require 'json'

class Api::V1::CheckoutController < ApplicationController
  def index
    Sentry.logger.info("Starting checkout process")
    
    # get Sentry tags in application_controller.rb
    set_Sentry_tags 

    # mock data for testing local
    # infoin = {
    #   "cart":
    #     {"items":
    #       [
    #         {"id":4,
    #         "title":"Botana Voice",
    #         "description":"Lets plants speak for themselves.",
    #         "descriptionfull":"Now we don't want him to get lonely, so we'll give him a little friend. Let your imagination just wonder around when you're doing these things. Let your imagination be your guide. Nature is so fantastic, enjoy it. Let it make you happy.",
    #         "price":175,
    #         "img":"https://storage.googleapis.com/application-monitoring/plant-to-text.jpg",
    #         "imgcropped":"https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg",
    #         "pg_sleep":"",
    #         "reviews":[
    #           {"id":4,"productid":4,"rating":4,"customerid":nil,"description":nil,"created":"2021-06-04 00:12:33.553939","pg_sleep":""},
    #           {"id":5,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-06-04 00:12:45.558259","pg_sleep":""},
    #           {"id":6,"productid":4,"rating":2,"customerid":nil,"description":nil,"created":"2021-06-04 00:12:50.510322","pg_sleep":""},
    #           {"id":13,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:12:43.312186","pg_sleep":""},
    #           {"id":14,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:12:54.719873","pg_sleep":""},
    #           {"id":15,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:12:57.760686","pg_sleep":""},
    #           {"id":16,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:00.140407","pg_sleep":""},
    #           {"id":17,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:00.971730","pg_sleep":""},
    #           {"id":18,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:01.665798","pg_sleep":""},
    #           {"id":19,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:02.278934","pg_sleep":""}
    #         ]},
    #         {"id":3,
    #         "title":"Plant Mood",
    #         "description":"The mood ring for plants.",
    #         "descriptionfull":"This is an example of what you can do with just a few things, a little imagination and a happy dream in your heart. I'm a water fanatic. I love water. There's not a thing in the world wrong with washing your brush. Everybody needs a friend. Here we're limited by the time we have.",
    #         "price":155,
    #         "img":"https://storage.googleapis.com/application-monitoring/mood-planter.jpg",
    #         "imgcropped":"https://storage.googleapis.com/application-monitoring/mood-planter-cropped.jpg",
    #         "pg_sleep":"",
    #         "reviews":[
    #           {"id":1,"productid":3,"rating":5,"customerid":nil,"description":nil,"created":"2021-06-04 00:04:01.739234","pg_sleep":""},
    #           {"id":2,"productid":3,"rating":4,"customerid":nil,"description":nil,"created":"2021-06-04 00:04:26.233562","pg_sleep":""},
    #           {"id":3,"productid":3,"rating":3,"customerid":nil,"description":nil,"created":"2021-06-04 00:05:05.060103","pg_sleep":""}
    #         ]}
    #       ],
    #     "quantities":{"3":1,"4":2},
    #     "total":505
    #     },
    #   "form":
    #     {"email":"","subscribe":"","firstName":"","lastName":"","address":"","city":"","country":"","state":"","zipCode":""}
    # }

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")
    span_read_params = transaction.start_child(op: "custom.read_params")

    total = ""
    cart_contents = Hash.new
    params.each do |key, value|
      if key.to_s == "cart"
        Sentry.logger.debug("Processing cart data for checkout")
        value.each do |key2, value2|
         if key2.to_s == "quantities"
           value2.each do | product_id, product_quantity |
             cart_contents[product_id.to_s] = product_quantity.to_s
             Sentry.logger.debug("Cart item: product_id %{product_id}, quantity %{quantity}", product_id: product_id, quantity: product_quantity)
           end
         elsif key2.to_s == "total"
           total = value2.to_s
           Sentry.logger.debug("Cart total: %{total}", total: total)
         end
        end
      end
    end

    span_read_params.finish

    #default message, rewritten if exception
    logged = "Thanks for your order. Total cost is $" + total 

    Sentry.logger.trace("Starting inventory database connection")
    span_inventory_call = transaction.start_child(op: "custom.inventory_db_call")
    products_in_inventory = Inventory.all()
    span_inventory_call.finish
    Sentry.logger.trace("Completed inventory database query, found %{count} items", count: products_in_inventory.length)

    span_logic = transaction.start_child(op: "custom.inventory_vs_cart_logic")

    # Check if we have enough inventory for the entire cart
    if !enough_inventory?(cart_contents)
      begin
        Sentry.logger.error("Failed to process payment. Insufficient inventory for cart contents")
        raise Exception.new "Not enough inventory for one or more products in cart"
        STDERR.puts "Not enough inventory for cart contents"
        logged = "Error: Not enough inventory"
        render json: {"message": logged}, status: 500
        return
      end
    end

    span_logic.finish

    Sentry.logger.info("Checkout completed successfully for total %{total}", total: total)
    render json: {"message": logged}, status: 200

  end

  def enough_inventory?(cart_contents)
    Sentry.logger.info("Performing inventory check for cart contents")
    
    # Check each product in the cart
    cart_contents.each do |product_id_str, quantity_str|
      product_id = product_id_str.to_i
      requested_quantity = quantity_str.to_i
      
      Sentry.logger.debug("Checking inventory for product %{product_id}, requested quantity: %{quantity}", product_id: product_id, quantity: requested_quantity)
      
      # Find inventory record for this product
      inventory_record = Inventory.find_by(productid: product_id)
      
      if inventory_record.nil?
        Sentry.logger.warn("No inventory record found for product %{product_id}", product_id: product_id)
        return false
      end
      
      available_quantity = inventory_record.count
      Sentry.logger.debug("Product %{product_id} has %{available} items available, %{requested} requested", 
                         product_id: product_id, available: available_quantity, requested: requested_quantity)
      
      if available_quantity < requested_quantity
        Sentry.logger.warn("Insufficient inventory for product %{product_id}: %{available} available, %{requested} requested", 
                          product_id: product_id, available: available_quantity, requested: requested_quantity)
        return false
      end
    end
    
    Sentry.logger.info("Inventory check passed - sufficient stock for all items")
    return true
  end
end