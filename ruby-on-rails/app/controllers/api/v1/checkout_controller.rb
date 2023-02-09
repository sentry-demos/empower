# require "pg"
require 'json'

class Api::V1::CheckoutController < ApplicationController
  def index

  infoin = {
    "cart":
      {"items":
        [
          {"id":4,
          "title":"Botana Voice",
          "description":"Lets plants speak for themselves.",
          "descriptionfull":"Now we don't want him to get lonely, so we'll give him a little friend. Let your imagination just wonder around when you're doing these things. Let your imagination be your guide. Nature is so fantastic, enjoy it. Let it make you happy.",
          "price":175,
          "img":"https://storage.googleapis.com/application-monitoring/plant-to-text.jpg",
          "imgcropped":"https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg",
          "pg_sleep":"",
          "reviews":[
            {"id":4,"productid":4,"rating":4,"customerid":nil,"description":nil,"created":"2021-06-04 00:12:33.553939","pg_sleep":""},
            {"id":5,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-06-04 00:12:45.558259","pg_sleep":""},
            {"id":6,"productid":4,"rating":2,"customerid":nil,"description":nil,"created":"2021-06-04 00:12:50.510322","pg_sleep":""},
            {"id":13,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:12:43.312186","pg_sleep":""},
            {"id":14,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:12:54.719873","pg_sleep":""},
            {"id":15,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:12:57.760686","pg_sleep":""},
            {"id":16,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:00.140407","pg_sleep":""},
            {"id":17,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:00.971730","pg_sleep":""},
            {"id":18,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:01.665798","pg_sleep":""},
            {"id":19,"productid":4,"rating":3,"customerid":nil,"description":nil,"created":"2021-07-01 00:13:02.278934","pg_sleep":""}
          ]},
          {"id":3,
          "title":"Plant Mood",
          "description":"The mood ring for plants.",
          "descriptionfull":"This is an example of what you can do with just a few things, a little imagination and a happy dream in your heart. I'm a water fanatic. I love water. There's not a thing in the world wrong with washing your brush. Everybody needs a friend. Here we're limited by the time we have.",
          "price":155,
          "img":"https://storage.googleapis.com/application-monitoring/mood-planter.jpg",
          "imgcropped":"https://storage.googleapis.com/application-monitoring/mood-planter-cropped.jpg",
          "pg_sleep":"",
          "reviews":[
            {"id":1,"productid":3,"rating":5,"customerid":nil,"description":nil,"created":"2021-06-04 00:04:01.739234","pg_sleep":""},
            {"id":2,"productid":3,"rating":4,"customerid":nil,"description":nil,"created":"2021-06-04 00:04:26.233562","pg_sleep":""},
            {"id":3,"productid":3,"rating":3,"customerid":nil,"description":nil,"created":"2021-06-04 00:05:05.060103","pg_sleep":""}
          ]}
        ],
      "quantities":{"3":1,"4":2},
      "total":505
      },
    "form":
      {"email":"","subscribe":"","firstName":"","lastName":"","address":"","city":"","country":"","state":"","zipCode":""}
  }

  

  total = ""
  cart_cnts = Hash.new
  infoin.each do |key, value|
    if key.to_s == "cart"
      value.each do |key2, value2|
        if key2.to_s == "quantities"
          value2.each do | prodid, prodidcnt |
            cart_cnts[prodid.to_s] = prodidcnt.to_s
          end
        elsif key2.to_s == "total"
          total = value2.to_s
        end
      end
    end
  end




  logged = "Thanks for your order. Total cost is $" + total #default message, rewritten if needed
  #logged += cart_cnts.to_s + "\n"
  #TODO: array of productids passed in
  products_in_inventory = Inventory.all()
  #products = Inventory.where(productid: [4, 5])
  # logger.debug("debug::" + "messageNEW3" + products.to_yaml)

  # -- winner --
  products_in_inventory.each_with_index { |inv_objs, i|
      if cart_cnts[inv_objs["productid"].to_s] != nil
        #logged += objs["productid"].to_s + ": " + h_cnts[objs["productid"].to_s] + "\n"
        if cart_cnts[inv_objs["productid"].to_s] > inv_objs["count"].to_s
          #begin
            raise Exception.new "Not enough inventory for " + "product"
            STDERR.puts "Not enough inventory for " + "product"
          #rescue Exception => e
            logged = "Not enough inventory for " + "product" #e.message #"Not enough inventory for " + "product"
          #end       
          break
        end
      end
  }
  # / winner 

  #render json: products, status: 200
  render json: {"message": logged}, status: 200

  end
end