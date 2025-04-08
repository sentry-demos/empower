using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading.Tasks;

namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    [HttpPost]
    public IActionResult Checkout([FromBody] CheckoutRequest request)
    {
        if (request.validate_inventory == "true")
        {
            throw new Exception("Not enough inventory");
        }
        return Ok(new { status = "success" });
    }
}

public class CheckoutRequest
{
    public string validate_inventory { get; set; }
}
