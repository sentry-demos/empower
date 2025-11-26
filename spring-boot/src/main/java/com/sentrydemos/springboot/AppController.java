package com.sentrydemos.springboot;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import jakarta.annotation.PostConstruct;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.sentry.Sentry;
import io.sentry.protocol.User;
// Removed IScopes import as it's not available in current Sentry configuration

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import jakarta.servlet.http.HttpServletRequest;

import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.web.client.RestTemplate;

import com.sentrydemos.springboot.utils.SpanUtils;

import static com.sentrydemos.springboot.utils.SpanUtils.executeWithSpan;
import static com.sentrydemos.springboot.utils.Utils.getIterator;

@RestController
public class AppController {

	private final Logger logger = LoggerFactory.getLogger(Application.class);
	private List<String> headerTags = new ArrayList<>();

	private HttpHeaders headers = new HttpHeaders();
	private final RestTemplate restTemplate;

	@Autowired
	private Environment environment;

	public AppController(RestTemplate restTemplate) {
		this.restTemplate = restTemplate;
	}
	
	@Autowired
	private DatabaseHelper dbHelper = new DatabaseHelper();

	// Removed IScopes autowiring as it's not available in current Sentry configuration
	
	// headers passed by frontend
	@PostConstruct
	public void initHeaders() {
		headerTags.add("se");
		headerTags.add("customerType");
		headerTags.add("email");

	}

	private void setTags(HttpServletRequest request) {

		for (String tag : headerTags) {
			String header = request.getHeader(tag);
			if (header != null && header != "null") {
				headers.set(tag,header);
				if (tag == "email") {
					User user = new User();
					user.setEmail(header);
					Sentry.setUser(user);
				} else {
					Sentry.setTag(tag, header);
				}
			}
		}

	}
	
	@CrossOrigin
	@GetMapping("/")
	public String index() {
		logger.info("[springboot - logback] - returning from / call: Greetings from Spring Boot!");
		return "Greetings from Spring Boot!";

	}

	@CrossOrigin
	@GetMapping("/success")
	public String Success(HttpServletRequest request) {
		logger.info("[springboot - logback] - success");
		setTags(request);
		return "success from springboot";

	}

	@CrossOrigin
	@GetMapping("/handled")
	public String HandledError() {
		String someLocalVariable = "stack locals";

		try {
			int example = 1 / 0;
		} catch (Exception e) {
			logger.error("[springboot - logback] - caught exception", e);
			return "Fail";
		}
		return "Success";
	}

	@CrossOrigin
	@GetMapping("/unhandled")
	public String UnhandledError() {
		throw new RuntimeException("Unhandled Exception!");
	}

	@CrossOrigin
	@GetMapping("/api")
	public String Api(HttpServletRequest request) {
		logger.info("[springboot - logback] - > /api");
		setTags(request);

		Sentry.logger().info("[springboot] - Making external API call to Ruby backend");
		String BACKEND_URL_RUBY = environment.getProperty("empower.rubyonrails_backend");
		ResponseEntity<String> response = restTemplate.exchange(BACKEND_URL_RUBY + "/api", HttpMethod.GET,new HttpEntity<>(headers), String.class);
		Sentry.logger().info("[springboot] - External API call completed", "response_status", response.getStatusCode().value());
		
		return "springboot /api";
	}

	@CrossOrigin
	@GetMapping("/connect")
	public String Connect(HttpServletRequest request) {
		setTags(request);
		return "springboot /connect";
	}

	@CrossOrigin
	@GetMapping("/organization")
	public String Organization(HttpServletRequest request) {
		setTags(request);
		return "springboot /organization";
	}

	@CrossOrigin
	@GetMapping("/logback")
	public String Logback() {
		logger.info("[springboot - logback] - info log");
		logger.warn("[springboot - logback] - warn log");
		logger.error("[springboot - logback] - error log");
		return "Made an info, warn, and error log entry.\n"
				+ "Whether they go to Sentry depends on the application.properties value: sentry.logging.minimum-event-level";

	}

	@CrossOrigin
	@GetMapping("/products")
	public String GetProductsDelay(HttpServletRequest request) throws Exception {
		try {
			// Set tags with span tracking
			executeWithSpan("overhead", "Set tags", () -> setTags(request));
			
			// Execute iterator calculation with span tracking
			executeWithSpan("get_iterator", "Iterator calculation", () -> Thread.sleep(getIterator(16)));

			String fooResourceUrl = environment.getProperty("empower.rubyonrails_backend");
			ResponseEntity<String> response = restTemplate.exchange(fooResourceUrl + "/api", HttpMethod.GET,new HttpEntity<>(headers), String.class);

			String allProducts = dbHelper.mapAllProducts(Sentry.getSpan());
			return allProducts;
		} catch (Exception e) {
			logger.error("[springboot - logback] - Failed to get products", e);
			throw new RuntimeException("Failed to retrieve products", e);
		}
	}

	@CrossOrigin
	@GetMapping("/products-join")
	public String GetProducts(HttpServletRequest request) throws Exception {
		setTags(request);

		String fooResourceUrl = environment.getProperty("empower.rubyonrails_backend");
		ResponseEntity<String> response = restTemplate.exchange(fooResourceUrl + "/api", HttpMethod.GET,new HttpEntity<>(headers), String.class);

		String allProducts = dbHelper.mapAllProductsJoin(Sentry.getSpan());
		return allProducts;
	}

	@CrossOrigin
	@PostMapping("/checkout")
	public String CheckoutCart(HttpServletRequest request, @RequestBody String payload) throws Exception {
		Sentry.logger().info("[springboot] - Checkout process started", "payload_size", payload.length());
    	setTags(request);

		// Parse cart with span tracking
		Cart cart = executeWithSpan("map_payload", "Set tags and map payload to Cart object", () -> {
			JSONObject json = new JSONObject(payload);
			ObjectMapper objectMapper = new ObjectMapper();
			try {
				Cart parsedCart = objectMapper.readValue(json.get("cart").toString(), Cart.class);
				
				Sentry.logger().info("[springboot] - Cart parsed successfully", 
					"cart_items_count", parsedCart.getItems() != null ? parsedCart.getItems().size() : 0,
					"cart_total", parsedCart.getTotal(),
					"quantities_count", parsedCart.getQuantities().size());
				
				return parsedCart;
			} catch (Exception e) {
				throw new RuntimeException("Failed to parse cart", e);
			}
		});
		
		// Process checkout with span tracking
		executeWithSpan("process_order", "Checkout Cart quantities", () -> checkout(cart.getQuantities()));
		
		Sentry.logger().info("[springboot] - Checkout completed successfully");
		return "Checkout completed";
	}

	private void checkout(Map<String, Integer> quantities) throws Exception {
		Map<String, Integer> tempInventory = dbHelper.getInventory(quantities.keySet(), Sentry.getSpan());
		Sentry.logger().info("[springboot] - Inventory size: " + tempInventory.size());

		SpanUtils.executeWithSpan("reduce_inventory", "Reduce inventory from Cart quantities", () -> {
			for (String key : quantities.keySet()) {
				logger.info("[springboot - logback] - Item " + key + " has quantity " + quantities.get(key));

				int currentInventory = tempInventory.get(key);
				currentInventory = currentInventory - quantities.get(key);
				Sentry.logger().info("[springboot] - Item " + key + " has quantity " + quantities.get(key) + " and current inventory " + currentInventory);
				
				if (!hasInventory()) {
					String message = "No inventory for item";
					Sentry.logger().warn("[springboot] - " + message);
					throw new RuntimeException(message);
				}

				tempInventory.put(key, currentInventory);
			}
		});
	}

	/*
	 * BELOW ARE TEST FUNCTIONS
	 */
	@CrossOrigin
	@PostMapping("/postbody")
	public String postBody(@RequestBody String fullName) {
		return "Hello " + fullName;
	}
	
	public Boolean hasInventory() {
		return false;
	}
	
}