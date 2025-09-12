import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import com.sentrydemos.springboot.Utils;

public class UtilsTest {

    @Test
    public void testGetIteratorNegative() {
        int result = Utils.getIterator(-1);
        assertEquals(0, result, "Negative input should return 0");
    }

    @Test
    public void testGetIteratorZero() {
        int result = Utils.getIterator(0);
        assertEquals(0, result, "Input 0 should return 0");
    }

    @Test
    public void testGetIteratorOne() {
        int result = Utils.getIterator(1);
        assertEquals(1, result, "Input 1 should return 1");
    }

    @Test
    public void testGetIteratorTwo() {
        int result = Utils.getIterator(2);
        assertEquals(1, result, "Input 2 should return 1");
    }

    @Test
    public void testGetIteratorFive() {
        int result = Utils.getIterator(5);
        assertEquals(5, result, "Input 5 should return 5");
    }

    @Test
    public void testGetIteratorTen() {
        int result = Utils.getIterator(10);
        assertEquals(55, result, "Input 10 should return 55");
    }
}
