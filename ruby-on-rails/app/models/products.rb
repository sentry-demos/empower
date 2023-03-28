class Products < ActiveRecord::Base
    has_one :inventory
    # may reuse below for a more elegant query
    #has_many :review, class_name: "Reviews", foreign_key: "productid"
    #has_many :reviews, :through => :review
    #has_many :review, -> { where("products.id == reviews.productid")}, class_name: "Reviews"
end