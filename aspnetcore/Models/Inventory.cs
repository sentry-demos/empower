using System;
using System.Collections.Generic;

// Code scaffolded by EF Core assumes nullable reference types (NRTs) are not used or disabled.
// If you have enabled NRTs for your project, then un-comment the following line:
// #nullable disable

namespace aspnetcore.Models
{
    public partial class Inventory
    {
        public int Id { get; set; }
        public string Sku { get; set; }
        public int Count { get; set; }
        public int? Productid { get; set; }
    }
}
