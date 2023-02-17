using System;
using System.Collections.Generic;

// Code scaffolded by EF Core assumes nullable reference types (NRTs) are not used or disabled.
// If you have enabled NRTs for your project, then un-comment the following line:
// #nullable disable

namespace aspnetcore.Models
{
    public partial class Review
    {
        public int Id { get; set; }
        public int Productid { get; set; }
        public int Rating { get; set; }
        public int? Customerid { get; set; }
        public string Description { get; set; }
        public DateTime? Created { get; set; }
        public Product Product { get; set; }
    }
}
