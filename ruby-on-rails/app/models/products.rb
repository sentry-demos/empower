class Products < ActiveRecord::Base
    has_one :inventory
    # may reuse below for a more elegant query
    #has_many :review, class_name: "Reviews", foreign_key: "productid"
    #has_many :reviews, :through => :review
    #has_many :review, -> { where("products.id == reviews.productid")}, class_name: "Reviews"
    
    after_initialize :log_product_creation
    
    private
    
    def log_product_creation
        if new_record?
            Sentry.logger.debug("New product instance created: %{title}", title: self.title || "untitled")
        else
            Sentry.logger.trace("Product loaded from database: %{id}", id: self.id)
        end
    end
end