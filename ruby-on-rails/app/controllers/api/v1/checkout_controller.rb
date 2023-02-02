# require "pg"

class Api::V1::CheckoutController < ApplicationController
  def index
    # results = []

    products = Products.all()

    # products = Products.where('id = 3')

    #product = products.each_with_object({}) do |attr_name, attr_value|
    #  id, title = attr_name.values_at(:id, :title)
    #  product[id] = title
    #end
    logged = "init: "
    product = products.count.to_s
    
    products.each_with_index { |objs, i|
      logged += "id:" + objs["id"].to_s + "\n"

      if objs["id"].to_s == '4'
        logged += "found " + "id=" + objs["id"].to_s + "\n"
      end
    }

    #products.each_with_object({}) do |h|  
    #  logged = h[0]
      #if h["id"].to_s == '4'
      #  logged += "found " + h["id"].to_s
      #end
      #end
    #end
    # render json: products, status: 200
    render json: {"message": products.count.to_s + ": " + product.to_s, "logged": logged}, status: 200

  end
end