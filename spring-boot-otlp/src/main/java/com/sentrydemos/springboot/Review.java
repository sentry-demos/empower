package com.sentrydemos.springboot;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

//used to ignore unknown field pg_sleep
@JsonIgnoreProperties(ignoreUnknown = true)
public class Review {
	private static final Logger logger = LoggerFactory.getLogger(Application.class);
    private int id;
    private int productid;
    private int rating;
    private int customerid;
    private String description;
    private String created;

    public Review() {}
    
    public Review(int id, int productid, int rating, int customerid, String description, String created) {
    	this.id = id;
    	this.productid = productid;
    	this.rating = rating;
    	this.customerid = customerid;
    	
    	this.description = description;
    	this.created = created;
    }
    public int getId() {
        return id;
    }
    
    public int getProductid() {
        return productid;
    }
    
    public int getRating() {
        return rating;
    }
    
    public int getCustomerid() {
        return customerid;
    }
    
    
    public String getDescription() {
        return description;
    }
    
    public String getCreated() {
        return created;
    }
    
}