package com.sentrydemos.springboot;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import io.sentry.ISpan;

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
	
	@Autowired
	JdbcTemplate jdbcTemplate;
	
	//Leverage Item & Review class getters to map DB results into JSONObject/JSONArray
	public String mapAllProducts(ISpan span) {
		logger.info("mapAllProducts");

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
		String sql = "SELECT *, pg_sleep(0.25) FROM reviews WHERE productId = " + String.valueOf(productId);

		ISpan sqlSpan = span.startChild("db", sql);
		List<Review> allReviews = jdbcTemplate.query(sql, (rs, rowNum) -> new Review(rs.getInt("id"), rs.getInt("productid"),
				rs.getInt("rating"), rs.getInt("customerid"), rs.getString("description"), rs.getString("created"))); 
		//TODO: sqlSpan.setData() on reviews. setData() currently unavailable
		sqlSpan.finish();
		return allReviews;

	}

	public String mapAllProductsJoin(ISpan transaction) {
		logger.info("mapAllProductsJoin");
		
		String sql = "SELECT * FROM products";
		ISpan sqlSpan = transaction.startChild("db", sql);


		List<Item> allItems = jdbcTemplate.query(sql,
				(rs, rowNum) -> new Item(rs.getInt("id"), rs.getString("title"), rs.getString("description"),
						rs.getString("descriptionfull"), rs.getInt("price"), rs.getString("img"),
						rs.getString("imgcropped"), mapAllReviewsJoin(rs.getInt("id"), sqlSpan)));

		JSONArray ja = new JSONArray();
		for (Item i : allItems) {
			JSONObject jsonItemObject = new JSONObject(i);

			ja.put(jsonItemObject);
		}
		
		sqlSpan.setTag("totalProducts", String.valueOf(allItems.size()));
		
		sqlSpan.finish();
		
		return ja.toString();
	}

	public List<Review> mapAllReviewsJoin(int productId, ISpan span) {
		String sql = "SELECT * FROM reviews WHERE productId = " + String.valueOf(productId);

		ISpan sqlSpan = span.startChild("db", sql);
		List<Review> reviews = jdbcTemplate.query(sql, (rs, rowNum) -> new Review(rs.getInt("id"), rs.getInt("productid"),
				rs.getInt("rating"), rs.getInt("customerid"), rs.getString("description"), rs.getString("created")));
		//TODO: sqlSpan.setData() on reviews. setData() currently unavailable
		sqlSpan.finish();
		return reviews; 

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