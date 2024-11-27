class AddQuantityToInventory < ActiveRecord::Migration[6.1]
  def change
    # Add quantity column if it doesn't exist
    unless column_exists?(:inventory, :quantity)
      add_column :inventory, :quantity, :integer, null: false, default: 0
    end
    
    # Add index for faster lookups
    unless index_exists?(:inventory, :product_id)
      add_index :inventory, :product_id
    end
  end
end