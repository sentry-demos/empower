using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using aspnetcore.Models;
using Microsoft.Extensions.Configuration;
using Sentry;

namespace aspnetcore.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class CheckoutController : ControllerBase
    {
        private readonly ILogger<CheckoutController> _logger;
        private hardwarestoreContext _context = null;
        private readonly IConfiguration Configuration;

        /* These arguments are wired up automagically by the framework */
        public CheckoutController(ILogger<CheckoutController> logger, hardwarestoreContext context, IConfiguration configuration)
        {
            _logger = logger;
            _context = context;
            Configuration = configuration;
        }

        // seems like this can return any object - will be automatically serialized to JSON
        [HttpPost("/checkout")]
        public ActionResult Checkout()
        { 
            Response.Headers.Add("access-control-allow-origin", "*");
            var se = Request.Headers["se"];
            var customerType = Request.Headers["customerType"];
            var email = Request.Headers["email"];
            SentrySdk.ConfigureScope(scope =>
            {
                scope.SetTag("se", se);
                scope.SetTag("customerType", customerType);
                scope.User = new User {
                    Email = email
                };
            });
            throw new Exception("Not enough inventory");
        }
    }
}
