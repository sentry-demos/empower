package com.sentrydemos.springboot;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Cart {
	private static final Logger logger = LoggerFactory.getLogger(Application.class);
	private List<Item> items;
	private Map<String, Integer> quantities = new HashMap<String, Integer>();
	private int total;
	
    
    public Cart() {}

    public Cart(List<Item> items, Map<String, Integer> quantities, int total) {
        this.items = items;
        this.quantities = quantities;
        this.total = total;
    }

    public List<Item> getItems() {
        return items;
    }
    
    public String getItemIDs() {
    	StringBuilder s = new StringBuilder();
    	for (Item i : items) {
    		s.append(i.getId() + " ");
    	}
        return s.toString();
    }
    
    public int getTotal() {
    	return total;
    }
    
    public Map<String, Integer> getQuantities() {
    	return quantities;
    }

}