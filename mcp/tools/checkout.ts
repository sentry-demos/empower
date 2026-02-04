import { CheckoutRequest } from "../types.js";
import { z } from "zod";
import { maybeThrow } from "../utils.js";

export const checkoutTool = {
  title: "Checkout",
  annotations: {
    description: "Process checkout with cart items and customer information",
  },
  inputSchema: {
    cart: z
      .object({
        items: z.array(
          z.object({
            id: z.number(),
            title: z.string(),
            description: z.string(),
            descriptionfull: z.string(),
            price: z.number(),
            img: z.string(),
            imgcropped: z.string(),
            reviews: z.array(
              z.object({
                id: z.number(),
                productid: z.number(),
                rating: z.number(),
                customerid: z.number().nullable(),
                description: z.string().nullable(),
                created: z.string(),
                pg_sleep: z.string(),
              })
            ),
          })
        ),
        quantities: z.record(z.number()),
        total: z.number(),
      })
      .describe("Shopping cart with items and quantities"),
    form: z
      .object({
        email: z.string(),
        subscribe: z.string().optional().default(""),
        firstName: z.string(),
        lastName: z.string(),
        address: z.string(),
        city: z.string(),
        country: z.string(),
        state: z.string(),
        zipCode: z.string(),
      })
      .describe("Customer information form"),
    validate_inventory: z
      .string()
      .optional()
      .default("true")
      .describe("Whether to validate inventory"),
  },
  handler: async (args: any) => {
    maybeThrow(0.3, new Error("Empower Plant API unreachable"));

    const checkoutData: CheckoutRequest = {
      cart: args.cart,
      form: args.form,
      validate_inventory: args.validate_inventory || "true",
    };

    const result = await processCheckout(checkoutData);

    // Format response with clear structure
    let responseText = "";

    if (result.success) {
      responseText = `✅ CHECKOUT SUCCESSFUL\n\n`;
      responseText += `📊 Request Summary:\n`;
      responseText += `  • Customer: ${result.requestSummary.customerEmail}\n`;
      responseText += `  • Items: ${result.requestSummary.itemCount}\n`;
      responseText += `  • Total: $${result.requestSummary.cartTotal}\n\n`;
      responseText += `🌐 Response Details:\n`;
      responseText += `  • Status: ${result.status} ${result.statusText}\n\n`;
      responseText += `📦 Response Data:\n`;
      responseText += JSON.stringify(result.data, null, 2);
    } else {
      responseText = `❌ CHECKOUT FAILED\n\n`;
      responseText += `📊 Request Summary:\n`;
      responseText += `  • Customer: ${result.requestSummary.customerEmail}\n`;
      responseText += `  • Items: ${result.requestSummary.itemCount}\n`;
      responseText += `  • Total: $${result.requestSummary.cartTotal}\n\n`;
      responseText += `🌐 Error Details:\n`;
      responseText += `  • Status: ${result.status} ${result.statusText}\n`;
      responseText += `  • Error: ${result.error}\n`;
    }

    return {
      content: [
        {
          type: "text" as const,
          text: responseText,
        },
      ],
    };
  },
};

interface CheckoutResponse {
  success: boolean;
  status: number;
  statusText: string;
  data?: any;
  error?: string;
  requestSummary: {
    cartTotal: number;
    itemCount: number;
    customerEmail: string;
  };
}

async function processCheckout(
  checkoutData: CheckoutRequest
): Promise<CheckoutResponse> {
  const requestSummary = {
    cartTotal: checkoutData.cart.total,
    itemCount: checkoutData.cart.items.length,
    customerEmail: checkoutData.form.email,
  };

  try {
    const response = await fetch(
      "https://flask.empower-plant.com/checkout?v2=true",
      {
        method: "POST",
        headers: {
          accept: "*/*",
          "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
          baggage:
            "sentry-environment=production,sentry-release=application.monitoring.javascript%4025.9.3,sentry-public_key=7bbdb0e36b1b40c09b1e0d23e5524a11,sentry-trace_id=a99478aec91a468c872eaa5aa573270d,sentry-replay_id=ca1501db65bb4840979a425e0c24fc26,sentry-transaction=%2Fcheckout,sentry-sampled=true,sentry-sample_rand=0.5744976832613148,sentry-sample_rate=1",
          "content-type": "application/json",
          customertype: "small-plan",
          email: checkoutData.form.email, // Use actual customer email
          origin:
            "https://application-monitoring-react-dot-sales-engineering-sf.appspot.com",
          priority: "u=1, i",
          referer:
            "https://application-monitoring-react-dot-sales-engineering-sf.appspot.com/",
          se: "undefined",
          "sec-ch-ua":
            '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
          "sec-ch-ua-mobile": "?0",
          "sec-ch-ua-platform": '"macOS"',
          "sec-fetch-dest": "empty",
          "sec-fetch-mode": "cors",
          "sec-fetch-site": "cross-site",
          "sentry-trace": "a99478aec91a468c872eaa5aa573270d-a09d5b179af67574-1",
          "user-agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        },
        body: JSON.stringify(checkoutData),
      }
    );

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status} ${response.statusText}`;
      let errorBody = null;

      try {
        errorBody = await response.text();
        if (errorBody) {
          try {
            const parsedError = JSON.parse(errorBody);
            errorMessage += ` - ${
              parsedError.message || parsedError.error || errorBody
            }`;
          } catch {
            errorMessage += ` - ${errorBody}`;
          }
        }
      } catch {
        // Ignore errors reading response body
      }

      return {
        success: false,
        status: response.status,
        statusText: response.statusText,
        error: errorMessage,
        requestSummary,
      };
    }

    const responseData = await response.json();

    return {
      success: true,
      status: response.status,
      statusText: response.statusText,
      data: responseData,
      requestSummary,
    };
  } catch (error) {
    return {
      success: false,
      status: 0,
      statusText: "Network Error",
      error: error instanceof Error ? error.message : "Unknown network error",
      requestSummary,
    };
  }
}
