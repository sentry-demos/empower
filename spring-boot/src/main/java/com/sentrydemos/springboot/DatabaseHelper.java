package com.sentrydemos.springboot;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Component;

import io.sentry.ISpan;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.json.JSONArray;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class DatabaseHelper {

	private final Logger logger = LoggerFactory.getLogger(Application.class);
	//Leverage Item & Review class getters to map DB results into JSONObject/JSONArray
	
	@Autowired
	JdbcTemplate jdbcTemplate;
	
	
	public String mapAllProducts(ISpan span) {

		String sql = "SELECT * FROM products";
		ISpan sqlSpan = span.startChild("db", sql);
		
		List<Item> allItems = jdbcTemplate.query(sql,
				(rs, rowNum) -> new Item(rs.getInt("id"), rs.getString("title"), rs.getString("description"),
						rs.getString("descriptionfull"), rs.getInt("price"), rs.getString("img"),
						rs.getString("imgcropped"), mapAllReviews(rs.getInt("id"), sqlSpan)));
		
		JSONArray ja = new JSONArray();
		for (Item i : allItems) {
			JSONObject jsonItemObject = new JSONObject(i);

			ja.put(jsonItemObject);
		}
		
		sqlSpan.setTag("totalProducts", String.valueOf(allItems.size()));
		
		sqlSpan.finish();
		
		return ja.toString();
	}

	public List<Review> mapAllReviews(int productId, ISpan span) {		
		// weekly_promotions is a "sleepy view", run the following query to get current sleep duration:
		// SELECT pg_get_viewdef('weekly_promotions', true)
		String sql = "SELECT * FROM reviews, weekly_promotions WHERE productId = " + String.valueOf(productId);

		ISpan sqlSpan = span.startChild("db", sql);
		List<Review> allReviews = jdbcTemplate.query(sql, (rs, rowNum) -> new Review(rs.getInt("id"), rs.getInt("productid"),
				rs.getInt("rating"), rs.getInt("customerid"), rs.getString("description"), rs.getString("created"))); 
		//TODO: sqlSpan.setData() on reviews. setData() currently unavailable
		sqlSpan.finish();
		return allReviews;

	}

	public String mapAllProductsJoin(ISpan transaction) {
		
		String sql = "SELECT * FROM products";
		ISpan sqlSpan = transaction.startChild("db", sql);

		List<Item> allItems = jdbcTemplate.query(sql,
				(rs, rowNum) -> new Item(rs.getInt("id"), rs.getString("title"), rs.getString("description"),
						rs.getString("descriptionfull"), rs.getInt("price"), rs.getString("img"),
						rs.getString("imgcropped"), null));
		
		sqlSpan.setTag("totalProducts", String.valueOf(allItems.size()));
		
		sqlSpan.finish();
		
		allItems = getAllItemsRowMapper(allItems, transaction);

		JSONArray ja = new JSONArray();
		for (Item i : allItems) {
			JSONObject jsonItemObject = new JSONObject(i);

			ja.put(jsonItemObject);
		}
		
		return ja.toString();
	}
	
	public List<Item> getAllItemsRowMapper(List<Item> items, ISpan transaction) {
		Map<Integer, List<Review>> reviewsMap = new HashMap<>();
		String sql = "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id";
		ISpan sqlSpan = transaction.startChild("db", sql);
		
		List<Map<String, Object>> resultList = jdbcTemplate.queryForList(sql);
		for (int i = 0; i < resultList.size(); i++) {
			Map<String, Object> m = resultList.get(i);
			
			//customerId and description are null. TODO: Set SQL table to prevent null values
			String desc = "";
			if (m.containsKey("description") && m.get("description") != null) {
				desc = String.valueOf(m.get("description"));
			}
			int custId = 0;
			if (m.containsKey("customerId") && m.get("customerId") != null) {
				custId = (int)m.get("customerId");
			}

        	Review r = new Review((int)m.get("id"), (int)m.get("productid"),
    				(int)m.get("rating"), custId, desc, m.get("created").toString());
        	
        	if (reviewsMap.containsKey((int)m.get("productid"))) {
        		reviewsMap.get((int)m.get("productid")).add(r);
        	} else {
        		List<Review> rl = new ArrayList<Review>();
        		rl.add(r);
        		reviewsMap.put((int)m.get("productid"), rl);
        	}
		}
		
		for (Item i : items) {
			i.setReviews(reviewsMap.get(i.getId()));
		}
		
		sqlSpan.finish();
		
		return items;

	}
	
	public Map<String, Integer> getInventory(Set<String> set, ISpan span) {
		
		String sql = "SELECT * FROM inventory WHERE productId in " + formatArray(set);
		ISpan sqlSpan = span.startChild("db", sql);
		
		List<Map<String, Object>> results = jdbcTemplate.queryForList(sql);

		Map<String, Integer> inventory = new HashMap<String, Integer>();
		for (Map m : results) {
			if (m.get("productid") != null && m.get("count") != null) {
				inventory.put(m.get("productid").toString(), (int) m.get("count"));
			}
		}
		sqlSpan.finish();
		
		return inventory;

	}
	
	private String formatArray(Set<String> set) {
		StringBuilder sb = new StringBuilder("(");
		
		String prefix = "";
		for (String productId : set) {
			sb.append(prefix + productId);
			prefix = ",";
		}
		sb.append(")");
		return sb.toString();
	}
	
}