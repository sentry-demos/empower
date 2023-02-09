class Products < ActiveRecord::Base
    has_one :inventory
    #has_many :review, class_name: "Reviews", foreign_key: "productid"
    #has_many :reviews, :through => :review
    #has_many :review, -> { where("products.id == reviews.productid")}, class_name: "Reviews"
end