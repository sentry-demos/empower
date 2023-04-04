using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using aspnetcore.Models;
using Microsoft.Extensions.Configuration;

namespace aspnetcore.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ApiController : ControllerBase
    {
        private readonly ILogger<ApiController> _logger;
        private hardwarestoreContext _context = null;
        private readonly IConfiguration Configuration;

        /* These arguments are wired up automagically by the framework */
        public ApiController(ILogger<ApiController> logger, hardwarestoreContext context, IConfiguration configuration)
        {
            _logger = logger;
            _context = context;
            Configuration = configuration;
        }

        // seems like this can return any object - will be automatically serialized to JSON
        [HttpGet("/api")]
        public ActionResult Get()
        {
            string dsn = Configuration["Sentry:Dsn"];
            return Ok("aspnetcore /api DSN: " + dsn);
        }
    }
}
