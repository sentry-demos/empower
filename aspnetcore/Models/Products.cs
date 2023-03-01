using System;
using System.Collections.Generic;

// Code scaffolded by EF Core assumes nullable reference types (NRTs) are not used or disabled.
// If you have enabled NRTs for your project, then un-comment the following line:
// #nullable disable

namespace aspnetcore.Models
{
    public partial class Product
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Descriptionfull { get; set; }
        public int Price { get; set; }
        public string Img { get; set; }
        public string Imgcropped { get; set; }
        public ICollection<Review> Reviews { get; set; }
    }
}
