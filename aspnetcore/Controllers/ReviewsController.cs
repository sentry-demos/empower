namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ReviewsController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;
    
    public ReviewsController(HardwareStoreContext dbContext)
    {
        _dbContext = dbContext;
    }
    
    [HttpGet]
    public async Task<IList<Review>> Get() => await _dbContext.Reviews.ToListAsync();
}
