class Inventory < ActiveRecord::Base
    self.table_name = "inventory"
    belongs_to :product
    #scope :for_product, ->(product) {where(product_id: product)}
    #def change
    #    rename_column :inventory, :product_id, :productid
    #end
end
