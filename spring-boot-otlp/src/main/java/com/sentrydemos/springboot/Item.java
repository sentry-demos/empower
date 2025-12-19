package com.sentrydemos.springboot;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

//used to ignore unknown field pg_sleep
@JsonIgnoreProperties(ignoreUnknown = true)
public class Item {
	private static final Logger logger = LoggerFactory.getLogger(Application.class);
	private int id;
    private String title;
    private String description;
    private String descriptionfull;
    private int price;
    private String img;
    private String imgcropped;
    private List<Review> reviews;
    
    public Item() {}

    public Item(int id, String title, String description, String descriptionfull, int price, String img, String imgcropped, List<Review> reviews) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.descriptionfull = descriptionfull;
        this.price = price;
        this.img = img;
        this.imgcropped = imgcropped;
        this.reviews = reviews;        
    }
    
    public int getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }
    
    public String getDescription() {
        return description;
    }
    
    public String getDescriptionfull() {
        return descriptionfull;
    }
    
    public int getPrice() {
        return price;
    }

    public String getImg() {
        return img;
    }
    
    public String getImgcropped() {
        return imgcropped;
    }
    
    public List<Review> getReviews() {
    	return reviews;
    }
    
    public void setReviews(List<Review> reviews) {
    	this.reviews = reviews;
    }
}