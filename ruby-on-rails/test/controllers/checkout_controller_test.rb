require 'test_helper'

class CheckoutControllerTest < ActionDispatch::IntegrationTest
  test "checkout succeeds when validate_inventory is false" do
    cart_data = {
      "cart" => {
        "items" => [],
        "quantities" => { "3" => 1 },
        "total" => 155
      },
      "form" => {
        "email" => "test@example.com",
        "firstName" => "Test",
        "lastName" => "User"
      },
      "validate_inventory" => "false"
    }

    post "/checkout", params: cart_data, as: :json
    
    assert_response :success
    json_response = JSON.parse(response.body)
    assert_includes json_response["message"], "Thanks for your order"
  end

  test "checkout fails when validate_inventory is true" do
    cart_data = {
      "cart" => {
        "items" => [],
        "quantities" => { "3" => 1 },
        "total" => 155
      },
      "form" => {
        "email" => "test@example.com",
        "firstName" => "Test",
        "lastName" => "User"
      },
      "validate_inventory" => "true"
    }

    post "/checkout", params: cart_data, as: :json
    
    # Should return 500 because mock inventory check always returns false
    assert_response :internal_server_error
  end
end
