require 'test_helper'

class Api::V1::CheckoutControllerTest < ActionController::TestCase
  def setup
    @controller = Api::V1::CheckoutController.new
    # Create test data
    @product = Product.create!(
      id: 1,
      title: "Test Plant",
      price: 100
    )
    
    @inventory = Inventory.create!(
      product_id: @product.id,
      count: 1
    )

    @cart_contents = {
      "1" => "2" # Requesting 2 items when only 1 is in stock
    }
  end

  def teardown
    Product.delete_all
    Inventory.delete_all
  end

  test "should return 400 when inventory is insufficient" do
    post :index, params: {
      cart: {
        quantities: @cart_contents,
        total: "200"
      }
    }

    assert_response 400
    assert_equal "Error: Not enough inventory for productid 1", JSON.parse(response.body)["message"]
  end

  test "should return 200 when inventory is sufficient" do
    @inventory.update!(count: 3) # Update inventory to have enough stock
    
    post :index, params: {
      cart: {
        quantities: @cart_contents,
        total: "200"
      }
    }

    assert_response 200
    assert_equal "Thanks for your order. Total cost is $200", JSON.parse(response.body)["message"]
  end

  test "inventory check helper returns correct boolean" do
    # Test when inventory is insufficient
    assert_not @controller.send(:enough_inventory?, @cart_contents)
    
    # Test when inventory is sufficient
    @inventory.update!(count: 3)
    assert @controller.send(:enough_inventory?, @cart_contents)
  end
end