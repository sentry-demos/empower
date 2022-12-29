using System;
using System.Collections.Generic;

// Code scaffolded by EF Core assumes nullable reference types (NRTs) are not used or disabled.
// If you have enabled NRTs for your project, then un-comment the following line:
// #nullable disable

namespace aspnetcore.Model
{
    public partial class Products
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Descriptionfull { get; set; }
        public int Price { get; set; }
        public string Img { get; set; }
        public string Imgcropped { get; set; }
    }
}
