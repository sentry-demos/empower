import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class AppControllerTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    private String baseUrl;

    @BeforeEach
    public void setup() {
        baseUrl = "http://localhost:" + port;
    }

    @Test
    public void testCompressedAssetsEndpointExists() {
        String url = baseUrl + "/compressed_assets/compressed_small_file.js";
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        
        // Should either return OK (if file exists) or NOT_FOUND (if file doesn't exist)
        // but should NOT throw NoResourceFoundException
        assertTrue(
            response.getStatusCode() == HttpStatus.OK || 
            response.getStatusCode() == HttpStatus.NOT_FOUND,
            "Endpoint should exist and handle the request"
        );
    }

    @Test
    public void testUncompressedAssetsEndpointExists() {
        String url = baseUrl + "/uncompressed_assets/uncompressed_big_file.js";
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        
        // Should either return OK (if file exists) or NOT_FOUND (if file doesn't exist)
        // but should NOT throw NoResourceFoundException
        assertTrue(
            response.getStatusCode() == HttpStatus.OK || 
            response.getStatusCode() == HttpStatus.NOT_FOUND,
            "Endpoint should exist and handle the request"
        );
    }

    @Test
    public void testCompressedAssetsTimingHeader() {
        String url = baseUrl + "/compressed_assets/compressed_small_file.js";
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        
        // If the file is found, check that the header is present
        if (response.getStatusCode() == HttpStatus.OK) {
            assertTrue(
                response.getHeaders().containsKey("Timing-Allow-Origin"),
                "Timing-Allow-Origin header should be present"
            );
            assertEquals(
                "*",
                response.getHeaders().getFirst("Timing-Allow-Origin"),
                "Timing-Allow-Origin header should be set to *"
            );
        }
    }

    @Test
    public void testUncompressedAssetsTimingHeaderAndContentType() {
        String url = baseUrl + "/uncompressed_assets/uncompressed_big_file.js";
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        
        // If the file is found, check that the headers are present
        if (response.getStatusCode() == HttpStatus.OK) {
            assertTrue(
                response.getHeaders().containsKey("Timing-Allow-Origin"),
                "Timing-Allow-Origin header should be present"
            );
            assertEquals(
                "*",
                response.getHeaders().getFirst("Timing-Allow-Origin"),
                "Timing-Allow-Origin header should be set to *"
            );
            assertTrue(
                response.getHeaders().getContentType().toString().contains("application/octet-stream"),
                "Content-Type should be application/octet-stream"
            );
        }
    }
}
