package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	sentry "github.com/getsentry/sentry-go"
	sentryhttp "github.com/getsentry/sentry-go/http"

	"github.com/jackc/pgx/v5/pgxpool"
	redis "github.com/redis/go-redis/v9"
	openai "github.com/sashabaranov/go-openai"
	statsig "github.com/statsig-io/go-sdk"
)

type server struct {
	db           *pgxpool.Pool
	redis        *redis.Client
	rubyBackend  string
	runSlow      bool
	openaiClient *openai.Client
}

func firstEnv(keys ...string) string {
	for _, k := range keys {
		if v := os.Getenv(k); v != "" {
			return v
		}
	}
	return ""
}

func mustEnv(key string, alts ...string) string {
	v := firstEnv(append([]string{key}, alts...)...)
	if v == "" {
		log.Fatalf("missing required env %s", key)
	}
	return v
}

func initSentry() {
	// Release is optional for local development, required for production
	release := firstEnv("GO_RELEASE", "RELEASE")
	if release == "" {
		release = "development"
		log.Printf("Warning: No RELEASE env found, using 'development' for Sentry release")
	}

	err := sentry.Init(sentry.ClientOptions{
		Dsn:           mustEnv("GO_APP_DSN", "FLASK_APP_DSN"),
		Release:       release,
		Environment:   mustEnv("GO_ENV", "FLASK_ENV"),
		EnableTracing: true,
		EnableLogs:    true,

		TracesSampler: sentry.TracesSampler(func(ctx sentry.SamplingContext) float64 {
			if ctx.Span.Name == "OPTIONS /" || strings.Contains(ctx.Span.Name, "OPTIONS") {
				return 0.0
			}
			return 1.0
		}),

		BeforeSend: func(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
			var se string
			if event.Tags != nil {
				if seTag, exists := event.Tags["se"]; exists {
					se = seTag
				}
			}

			if se != "" && se != "undefined" {
				seFingerprint := se
				tda_regex := regexp.MustCompile(`[^-]+-tda-[^-]+-`)
				if match := tda_regex.FindString(se); match != "" {
					// Now that TDA puts platform/browser and test path into SE tag we want to prevent
					// creating separate issues for those. See https://github.com/sentry-demos/empower/pull/332
					seFingerprint = match
				}

				if strings.HasPrefix(se, "prod-tda-") {
					event.Fingerprint = []string{"{{ default }}", seFingerprint, release}
				} else {
					event.Fingerprint = []string{"{{ default }}", seFingerprint}
				}
			}

			return event
		},
		AttachStacktrace: true,
		Debug:            firstEnv("GO_ENV", "FLASK_ENV") != "production",
	})
	if err != nil {
		log.Fatalf("sentry init: %v", err)
	}
	log.Printf("Sentry initialized successfully with release: %s", release)
}

func initStatsig() {
	key := firstEnv("STATSIG_SERVER_KEY")
	if key == "" {
		log.Printf("Warning: STATSIG_SERVER_KEY not found, skipping Statsig initialization for local development")
		return
	}
	tier := firstEnv("GO_ENV", "FLASK_ENV")
	statsig.InitializeWithOptions(key, &statsig.Options{Environment: statsig.Environment{Tier: tier}})
	log.Printf("Statsig initialized successfully")
}

func initDB(ctx context.Context) *pgxpool.Pool {
	env := mustEnv("GO_ENV", "FLASK_ENV")
	log.Printf("initDB: GO_ENV=%s", env)
	var connStr string
	if env == "test" {
		host := mustEnv("DB_HOST")
		user := mustEnv("DB_USERNAME")
		pass := mustEnv("DB_PASSWORD")
		db := mustEnv("DB_DATABASE")
		// Use pgxpool.ParseConfig to properly handle special characters in password
		sslMode := os.Getenv("PGSSLMODE")
		if sslMode == "" {
			sslMode = "require"
		}
		connStr = fmt.Sprintf("postgres://%s:%s@%s:5432/%s?sslmode=%s",
			url.QueryEscape(user), url.QueryEscape(pass), host, db, sslMode)
		log.Printf("initDB: test connection string: %s", connStr)
	} else {
		user := mustEnv("DB_USERNAME")
		pass := mustEnv("DB_PASSWORD")
		db := mustEnv("DB_DATABASE")
		instance := mustEnv("DB_CLOUD_SQL_CONNECTION_NAME")
		// unix socket path used on App Engine standard
		socketDir := "/cloudsql/" + instance
		connStr = fmt.Sprintf("user=%s password=%s dbname=%s host=%s port=5432 sslmode=disable", user, pass, db, filepath.Join(socketDir))
	}
	cfg, err := pgxpool.ParseConfig(connStr)
	if err != nil {
		log.Fatalf("pgx parse: %v", err)
	}
	log.Printf("initDB: parsed config successfully, attempting connection...")
	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		log.Fatalf("pgx pool: %v", err)
	}
	log.Printf("initDB: connection pool created successfully")
	return pool
}

func initRedis() *redis.Client {
	host := os.Getenv("GO_REDISHOST")
	if host == "" {
		host = "localhost"
	}
	port := os.Getenv("GO_LOCAL_REDISPORT")
	if port == "" {
		port = "6379"
	}
	addr := host + ":" + port
	rdb := redis.NewClient(&redis.Options{Addr: addr})
	return rdb
}

func parseBoolEnv(key string, def bool) bool {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	b, err := strconv.ParseBool(v)
	if err != nil {
		return def
	}
	return b
}

func main() {
	defer sentry.Flush(2 * time.Second)
	initSentry()
	initStatsig()

	ctx := context.Background()
	pool := initDB(ctx)
	rdb := initRedis()

	oaKey := os.Getenv("OPENAI_API_KEY")
	var oaClient *openai.Client
	if oaKey != "" {
		oaClient = openai.NewClient(oaKey)
	}

	srv := &server{
		db:           pool,
		redis:        rdb,
		rubyBackend:  mustEnv("GO_RUBY_BACKEND", "RUBY_BACKEND"),
		runSlow:      parseBoolEnv("GO_RUN_SLOW_PROFILE", true),
		openaiClient: oaClient,
	}

	mux := http.NewServeMux()

	// routes
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"service":   "go",
			"status":    "ok",
			"endpoints": []string{"/products", "/enqueue", "/checkout", "/success", "/products-join", "/api", "/organization", "/healthz", "/readyz", "/livez"},
		})
	})
	mux.HandleFunc("/enqueue", srv.handleEnqueue)
	mux.HandleFunc("/suggestion", srv.handleSuggestion)
	mux.HandleFunc("/checkout", srv.handleCheckout)
	mux.HandleFunc("/success", srv.handleSuccess)
	mux.HandleFunc("/products", srv.handleProducts)
	mux.HandleFunc("/products-join", srv.handleProductsJoin)
	mux.HandleFunc("/handled", srv.handleHandled)
	mux.HandleFunc("/unhandled", srv.handleUnhandled)
	mux.HandleFunc("/api", srv.handleAPI)
	mux.HandleFunc("/organization", srv.cachedOrganization())
	mux.HandleFunc("/connect", func(w http.ResponseWriter, r *http.Request) { fmt.Fprint(w, "go /connect") })
	mux.HandleFunc("/showSuggestion", func(w http.ResponseWriter, r *http.Request) {
		ok := os.Getenv("OPENAI_API_KEY") != ""
		json.NewEncoder(w).Encode(map[string]bool{"response": ok})
	})
	mux.HandleFunc("/product/0/info", func(w http.ResponseWriter, r *http.Request) {
		// Let Sentry HTTP middleware handle transaction creation automatically
		// This is crucial for N+1 detection to work properly
		logger := sentry.NewLogger(r.Context())

		logger.Info().Emit("Received /product/0/info endpoint request")

		time.Sleep(550 * time.Millisecond)

		logger.Info().Emit("Completed /product/0/info request")

		w.Header().Set("Content-Type", "text/plain")
		fmt.Fprint(w, "go /product/0/info")
	})
	mux.Handle("/uncompressed_assets/", http.StripPrefix("/uncompressed_assets/", assetHandler("../flask/uncompressed_assets", true)))
	mux.Handle("/compressed_assets/", http.StripPrefix("/compressed_assets/", assetHandler("../flask/compressed_assets", false)))

	// health endpoints
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})
	mux.HandleFunc("/livez", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
		defer cancel()
		ready := true
		// simple DB ping
		if err := srv.db.Ping(ctx); err != nil {
			ready = false
		}
		// simple Redis ping
		if err := srv.redis.Ping(ctx).Err(); err != nil {
			ready = false
		}
		w.Header().Set("Content-Type", "application/json")
		if !ready {
			w.WriteHeader(http.StatusServiceUnavailable)
		}
		json.NewEncoder(w).Encode(map[string]bool{"ready": ready})
	})

	// sentry HTTP middleware + CORS wrapper
	sentryHandler := sentryhttp.New(sentryhttp.Options{Repanic: true})
	// wrap mux with a 404 logger
	logged := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		rw := &statusRecorder{ResponseWriter: w, status: 200}
		mux.ServeHTTP(rw, r)
		if rw.status == http.StatusNotFound {
			log.Printf("404 Not Found: %s %s", r.Method, r.URL.Path)
		}
	})
	// Apply middleware chain: CORS -> Sentry HTTP -> Sentry context -> logging
	// Note: sentryContextMiddleware must be INSIDE sentryHandler to access the hub
	handler := withCORS(sentryHandler.Handle(sentryContextMiddleware(logged)))

	port := os.Getenv("LOCAL_PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("listening on :%s", port)
	if err := http.ListenAndServe(":"+port, handler); err != nil {
		log.Fatal(err)
	}
}

type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.status = code
	r.ResponseWriter.WriteHeader(code)
}

func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Headers", "*")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}

// sentryContextMiddleware enriches Sentry events with request context
// Matches Flask's @app.before_request sentry_event_context() behavior
func sentryContextMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hub := sentry.GetHubFromContext(r.Context())

		if se := r.Header.Get("se"); se != "" && se != "undefined" {
			hub.Scope().SetTag("se", se)
		} else if se := r.URL.Query().Get("se"); se != "" && se != "undefined" {
			hub.Scope().SetTag("se", se)
		}

		if customerType := r.Header.Get("customerType"); customerType != "" && customerType != "undefined" {
			hub.Scope().SetTag("customerType", customerType)
		}

		if email := r.Header.Get("email"); email != "" && email != "undefined" {
			hub.Scope().SetUser(sentry.User{Email: email})
		}

		next.ServeHTTP(w, r)
	})
}

func assetHandler(dir string, disableCompression bool) http.Handler {
	fs := http.FileServer(http.Dir(dir))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Timing-Allow-Origin", "*")
		if disableCompression {
			w.Header().Set("Content-Type", "application/octet-stream")
		}
		fs.ServeHTTP(w, r)
	})
}

// --- Handlers ---

type enqueuePayload struct {
	Email string `json:"email"`
}

func (s *server) handleEnqueue(w http.ResponseWriter, r *http.Request) {
	hub := sentry.GetHubFromContext(r.Context())
	logger := sentry.NewLogger(r.Context())

	logger.Info().Emit("Received /enqueue endpoint request")

	var p enqueuePayload
	if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
		logger.Error().Emitf("Error decoding request body: %v", err)
		hub.CaptureException(fmt.Errorf("enqueue decode error: %w", err))
		http.Error(w, "bad request", 400)
		return
	}
	q := "celery-new-subscriptions"
	if err := s.redis.RPush(r.Context(), q, p.Email).Err(); err != nil {
		logger.Error().Emitf("Redis enqueue error: %v", err)
		hub.CaptureException(fmt.Errorf("redis enqueue error: %w", err))
		http.Error(w, "enqueue failed", 500)
		return
	}

	logger.Info().Emit("Completed /enqueue request - email task enqueued")
	json.NewEncoder(w).Encode(map[string]string{"status": "success"})
}

func (s *server) handleSuggestion(w http.ResponseWriter, r *http.Request) {
	hub := sentry.GetHubFromContext(r.Context())
	logger := sentry.NewLogger(r.Context())

	logger.Info().Emit("Received /suggestion endpoint request")

	catalog := r.URL.Query().Get("catalog")
	geo := r.URL.Query().Get("geo")

	logger.Info().Emit("Processing /suggestion - starting AI pipeline")

	prompt := fmt.Sprintf("You are witty plant salesman. Here is your catalog of plants: %s. Provide a suggestion based on the user's location. Pick one plant from the catalog provided. Keep your response short and concise. Try to incorporate the weather and current season.", catalog)
	suggestion := ""
	if s.openaiClient != nil {
		func(ctx context.Context) {
			model := os.Getenv("OPENAI_MODEL")
			if model == "" {
				model = "gpt-4o-mini"
			}

			req := openai.ChatCompletionRequest{
				Model: model,
				Messages: []openai.ChatCompletionMessage{
					{Role: openai.ChatMessageRoleSystem, Content: prompt},
					{Role: openai.ChatMessageRoleUser, Content: geo},
				},
			}
			resp, err := s.openaiClient.CreateChatCompletion(ctx, req)
			if err != nil || len(resp.Choices) == 0 {
				suggestion = ""
				if err != nil {
					hub.CaptureException(err)
				}
				return
			}
			suggestion = resp.Choices[0].Message.Content
		}(r.Context())
	}

	logger.Info().Emit("Completed /suggestion request - AI suggestion generated")
	json.NewEncoder(w).Encode(map[string]string{"suggestion": suggestion})
}

func (s *server) handleCheckout(w http.ResponseWriter, r *http.Request) {
	defer func() {
		if err := recover(); err != nil {
			sentry.GetHubFromContext(r.Context()).CaptureException(fmt.Errorf("%v", err))
			http.Error(w, fmt.Sprintf("%v", err), 500) // FAIL the request
			return
		}
	}()

	hub := sentry.GetHubFromContext(r.Context())
	logger := sentry.NewLogger(r.Context())
	start := time.Now()

	logger.Info().Emit("Received /checkout endpoint request")

	type order struct {
		Cart              map[string]interface{} `json:"cart"`
		Form              map[string]interface{} `json:"form"`
		ValidateInventory string                 `json:"validate_inventory"`
	}
	var o order
	if err := json.NewDecoder(r.Body).Decode(&o); err != nil {
		hub.CaptureException(fmt.Errorf("checkout decode error: %w", err))
		http.Error(w, "bad request", 400)
		return
	}

	log.Printf("Checkout called with cart: %v", o.Cart)

	func() {
		defer func() {
			if err := recover(); err != nil {
				hub.CaptureException(fmt.Errorf("%v", err))
				logger.Error().Emitf("Error evaluating flags in /checkout: %v", err)
			}
		}()
		_ = evaluateStatsigFlags()
	}()

	var inventory []inventoryRow
	var inventoryErr error
	func() {
		span := sentry.StartSpan(r.Context(), "/checkout.get_inventory", sentry.WithDescription("function"))
		defer span.Finish()

		inventory, inventoryErr = s.getInventory(span.Context(), o.Cart)
		if inventoryErr != nil {
			hub.CaptureException(fmt.Errorf("inventory error: %w", inventoryErr))
		}
	}()

	if inventoryErr != nil {
		http.Error(w, "inventory error", 500)
		return
	}

	logger.Info().Emitf("> /checkout inventory %v", inventory)

	validate := true
	if o.ValidateInventory != "" {
		validate = strings.ToLower(o.ValidateInventory) == "true"
	}
	logger.Info().Emitf("> validate_inventory %v", validate)

	if validate {
		log.Printf("Processing /checkout - validating order details")

		span := sentry.StartSpan(r.Context(), "process_order", sentry.WithDescription("function"))
		defer span.Finish()

		var quantities map[int]int
		var fulfilledCount int
		var outOfStock []string

		if o.ValidateInventory == "true" && len(o.Cart) > 0 {
			if m, ok := o.Cart["quantities"].(map[string]interface{}); ok && len(m) > 0 {
				// quantities = make(map[int]int)  // ← Missing: Go requires map initialization
				for k, v := range m {
					if f, ok := v.(float64); ok {
						if id, _ := strconv.Atoi(k); id > 0 {
							quantities[id] = int(f) // Go panic: assignment to entry in nil map
						}
					}
				}
			}
		}

		inventoryDict := make(map[int]inventoryRow)
		for _, item := range inventory {
			inventoryDict[item.ProductID] = item
		}

		for productId, requestedQty := range quantities {
			if invItem, exists := inventoryDict[productId]; exists {
				if invItem.Count >= requestedQty {
					fulfilledCount++
					log.Printf("Product %d: sufficient inventory (%d >= %d)", productId, invItem.Count, requestedQty)
				} else {
					if cartItems, ok := o.Cart["items"].([]interface{}); ok {
						for _, item := range cartItems {
							if itemMap, ok := item.(map[string]interface{}); ok {
								if id, ok := itemMap["id"].(float64); ok && int(id) == productId {
									if title, ok := itemMap["title"].(string); ok {
										outOfStock = append(outOfStock, title)
									}
								}
							}
						}
					}
				}
			}
		}

		if len(outOfStock) > 0 {
			log.Printf("Out of stock items: %v", outOfStock)
		}

		logger.Info().Emitf("checkout counts: fulfilled=%d out_of_stock=%d", fulfilledCount, len(outOfStock))
	}

	logger.Info().Emitf("Completed /checkout request in %s", time.Since(start))
	json.NewEncoder(w).Encode(map[string]string{"status": "success"})
}

func (s *server) handleProducts(w http.ResponseWriter, r *http.Request) {
	hub := sentry.GetHubFromContext(r.Context())
	logger := sentry.NewLogger(r.Context())
	start := time.Now()

	logger.Info().Emit("Received /products endpoint request")

	if transaction := sentry.TransactionFromContext(r.Context()); transaction != nil {
		transaction.Name = "products"
		transaction.SetTag("http.method", "GET")
		transaction.SetTag("http.route", "/products")
	} else {
		log.Printf("WARNING: No transaction found, creating manual transaction")
		transaction := sentry.StartTransaction(r.Context(), "products")
		defer transaction.Finish()
		r = r.WithContext(transaction.Context())
	}

	cacheKey := strconv.Itoa(rand.Intn(100))
	fetchPromotions := r.URL.Query().Get("fetch_promotions") != ""

	timeoutSeconds := 2.0
	if fetchPromotions {
		timeoutSeconds = 24
	}
	rubyDelay := 0.0
	if cacheKey != "7" {
		timeoutSeconds -= 0.5
		rubyDelay = 0.5
	}

	functionSpan := sentry.StartSpan(r.Context(), "function", sentry.WithDescription("/products.get_products"))
	functionSpan.SetTag("function.name", "get_products")

	// Pass the request context (not a span context) to avoid "span ID does not exist" errors
	// The transaction is in r.Context() and will be available throughout the call
	rows, err := s.getProducts(r.Context())
	functionSpan.Finish()

	if err != nil {
		logger.Error().Emitf("Processing /products - error occurred: %v", err)
		hub.CaptureException(fmt.Errorf("products database error: %w", err))
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	if s.runSlow {
		slowSpan := sentry.StartSpan(r.Context(), "function", sentry.WithDescription("/get_iterator"))
		slowSpan.SetTag("function.name", "get_iterator")
		start := time.Now()
		for time.Since(start).Seconds() <= timeoutSeconds {
			_ = fibonacci(20)
		}
		slowSpan.Finish()
	}

	s.getAPIRequest(cacheKey, rubyDelay, r.Context())
	var productsArray []map[string]interface{}
	if err := json.Unmarshal([]byte(rows), &productsArray); err == nil {
		logger.Info().Emitf("Completed /products request in %s products_count=%d", time.Since(start), len(productsArray))
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(productsArray)
	} else {
		logger.Info().Emitf("Completed /products request in %s", time.Since(start))
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(rows))
	}
}

func (s *server) handleProductsJoin(w http.ResponseWriter, r *http.Request) {
	defer sentry.RecoverWithContext(r.Context())

	hub := sentry.GetHubFromContext(r.Context())
	logger := sentry.NewLogger(r.Context())

	logger.Info().Emit("Received /products-join endpoint request")

	rows, err := s.getProductsJoin(r.Context())
	if err != nil {
		logger.Error().Emitf("Processing /products-join - error getting data: %v", err)
		hub.CaptureException(err)
		http.Error(w, "db error", 500)
		return
	}

	logger.Info().Emit("Processing /products-join - data retrieved")

	if err := s.proxyRuby(r); err != nil {
		logger.Error().Emit("Processing /products-join - backend API call failed")
	} else {
		logger.Info().Emit("Processing /products-join - backend API call successful")
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(rows))
}

func (s *server) handleSuccess(w http.ResponseWriter, r *http.Request) {
	defer sentry.RecoverWithContext(r.Context())

	w.Header().Set("Content-Type", "text/plain")
	w.Write([]byte("success from go"))
}

func (s *server) handleHandled(w http.ResponseWriter, r *http.Request) {
	defer sentry.RecoverWithContext(r.Context())

	hub := sentry.GetHubFromContext(r.Context())
	logger := sentry.NewLogger(r.Context())

	logger.Info().Emit("Received /handled endpoint request")

	func() {
		defer func() {
			if err := recover(); err != nil {
				logger.Error().Emit("Processing /handled - intentional exception occurred")
				hub.CaptureException(fmt.Errorf("%v", err))
			}
		}()

		var str string = "2"
		var num int = 2
		_ = str + string(rune(num))
		panic("unsupported operand type(s) for +: 'str' and 'int'")
	}()

	w.Header().Set("Content-Type", "text/plain")
	w.Write([]byte("failed"))
}

func (s *server) handleUnhandled(w http.ResponseWriter, r *http.Request) {
	defer sentry.RecoverWithContext(r.Context())

	logger := sentry.NewLogger(r.Context())
	logger.Info().Emit("Received /unhandled endpoint request")

	obj := make(map[string]interface{})
	_ = obj["keyDoesnt  Exist"].(string)

	w.Write([]byte("should not reach here"))
}

func (s *server) handleAPI(w http.ResponseWriter, r *http.Request) {
	defer sentry.RecoverWithContext(r.Context())

	w.Header().Set("Content-Type", "text/plain")
	w.Write([]byte("go /api"))
}

// --- Helpers ---

func fibonacci(n int) int {
	if n < 2 {
		return n
	}
	return fibonacci(n-1) + fibonacci(n-2)
}

func evaluateStatsigFlags() bool {
	if firstEnv("STATSIG_SERVER_KEY") == "" {
		log.Printf("Warning: Statsig SDK not initialized during flag evaluation.")
		return false
	}

	id := fmt.Sprintf("user-%d", time.Now().UnixNano())
	log.Printf("Evaluating Statsig flags for user: %s", id)

	u := statsig.User{UserID: id}
	gates := []string{"beta_feature", "alpha_feature", "new_products_fetch_feature"}
	on := false
	for _, g := range gates {
		result := statsig.CheckGate(u, g)
		log.Printf("  -> statsig %s: %v", g, result)
		if result {
			on = true
		}
	}
	return on
}

type inventoryRow struct {
	ID        int
	SKU       string
	Count     int
	ProductID int
}

func (s *server) getInventory(ctx context.Context, cart map[string]interface{}) ([]inventoryRow, error) {
	log.Printf("> get_inventory")

	var quantities map[string]interface{}
	if m, ok := cart["quantities"].(map[string]interface{}); ok {
		quantities = m
		log.Printf("> quantities %v", quantities)
	}

	ids := []int{}
	if quantities != nil {
		for k := range quantities {
			if id, err := strconv.Atoi(k); err == nil {
				log.Printf("Processing product ID: %s", k)
				ids = append(ids, id)
			}
		}
	}
	log.Printf("> productIds %v", ids)
	if len(ids) == 0 {
		return []inventoryRow{}, nil
	}

	var out []inventoryRow

	connectSpan := sentry.StartSpan(ctx, "get_inventory", sentry.WithDescription("db.connect"))
	connectSpan.Finish()

	querySpan := sentry.StartSpan(ctx, "get_inventory", sentry.WithDescription("db.query"))
	defer querySpan.Finish()

	sqlSpan := sentry.StartSpan(querySpan.Context(), "db", sentry.WithDescription("SELECT * FROM inventory WHERE productId"))

	rows, err := s.db.Query(ctx, "SELECT id, sku, count, productId FROM inventory WHERE productId = ANY($1)", ids)
	if err != nil {
		sqlSpan.Finish() // Finish span on error
		return nil, err
	}
	defer rows.Close()
	sqlSpan.Finish() // Finish span after successful query

	out = []inventoryRow{}
	for rows.Next() {
		var r inventoryRow
		if err := rows.Scan(&r.ID, &r.SKU, &r.Count, &r.ProductID); err != nil {
			return nil, err
		}
		out = append(out, r)
	}

	querySpan.SetData("inventory", out)

	return out, rows.Err()
}

func (s *server) getProducts(ctx context.Context) (string, error) {

	// Ensure we have a transaction in context (critical for N+1 detection)
	transaction := sentry.TransactionFromContext(ctx)
	if transaction == nil {
		// If no transaction exists, this is a problem - spans won't be detected
		log.Printf("WARNING: No Sentry transaction found in context for N+1 detection")
		return "", fmt.Errorf("no transaction in context")
	}
	log.Printf("SUCCESS: Found Sentry transaction '%s' for N+1 detection", transaction.Name)

	// Use transaction context for creating all spans
	// This ensures spans are siblings at the transaction level for N+1 detection
	transactionCtx := transaction.Context()

	span := sentry.StartSpan(transactionCtx, "db", sentry.WithDescription("connect"))
	span.SetTag("db.operation", "connect")
	// Use original ctx for DB operations (for cancellation, timeouts, etc.)
	conn, err := s.db.Acquire(ctx)
	if err != nil {
		span.Finish()
		return "", err
	}
	defer conn.Release()
	span.Finish()

	parameterizedProductsQuery := "SELECT * FROM products WHERE id IN (SELECT id FROM products, pg_sleep(%s))"
	actualProductsQuery := "SELECT * FROM products WHERE id IN (SELECT id from products)"

	productsSpan := sentry.StartSpan(transactionCtx, "db.query", sentry.WithDescription(parameterizedProductsQuery))
	productsSpan.SetTag("db.operation", "select")
	productsSpan.SetTag("db.system", "postgresql")
	productsSpan.SetData("db.statement", parameterizedProductsQuery)

	time.Sleep(25 * time.Millisecond)

	// Use original ctx for DB operations (for cancellation, timeouts, etc.)
	products, err := conn.Query(ctx, actualProductsQuery)
	if err != nil {
		productsSpan.Finish()
		return "", err
	}
	defer products.Close()

	// Don't finish productsSpan yet - we need it as parent for review spans
	type product struct {
		M       map[string]interface{}
		Reviews []map[string]interface{}
	}
	var list []product
	for products.Next() {
		values, _ := products.Values()
		fds := products.FieldDescriptions()
		pm := map[string]interface{}{}
		for i, fd := range fds {
			pm[string(fd.Name)] = values[i]
		}
		pid, ok := pm["id"].(int64)
		if !ok {
			if pidInt32, ok := pm["id"].(int32); ok {
				pid = int64(pidInt32)
			} else if pidInt, ok := pm["id"].(int); ok {
				pid = int64(pidInt)
			}
		}
		parameterizedQuery := "SELECT * FROM reviews, product_bundles WHERE productId = %s"
		actualQuery := fmt.Sprintf("SELECT * FROM reviews, product_bundles WHERE productId = %d", pid)
		log.Printf("Creating N+1 span %d: %s (parameterized: %s)", pid, actualQuery, parameterizedQuery)

		// Create review spans at transaction level (siblings, not nested)
		// This allows Sentry to detect the N+1 pattern by seeing multiple similar spans at the same level
		// Use transactionCtx (from transaction) to avoid "span ID does not exist" errors
		reviewSpan := sentry.StartSpan(transactionCtx, "db.query", sentry.WithDescription(parameterizedQuery))
		reviewSpan.SetTag("db.operation", "select")
		reviewSpan.SetTag("db.system", "postgresql")
		reviewSpan.SetData("db.statement", parameterizedQuery) // Use parameterized for grouping
		reviewSpan.SetData("productId", pid)                   // Store actual value as metadata

		time.Sleep(30 * time.Millisecond)

		// Use original ctx for DB operations (for cancellation, timeouts, etc.)
		revs, err := s.db.Query(ctx, "SELECT * FROM reviews, product_bundles WHERE productId = $1", pid)
		if err != nil {
			reviewSpan.Finish()
			return "", err
		}

		rlist := make([]map[string]interface{}, 0)
		for revs.Next() {
			vals, _ := revs.Values()
			fdr := revs.FieldDescriptions()
			rm := map[string]interface{}{}
			for i, fd := range fdr {
				rm[string(fd.Name)] = vals[i]
			}
			rlist = append(rlist, rm)
		}
		revs.Close()

		time.Sleep(5 * time.Millisecond)
		reviewSpan.Finish()
		list = append(list, product{M: pm, Reviews: rlist})
	}

	// Now finish the productsSpan after all review queries
	productsSpan.Finish()

	serializationSpan := sentry.StartSpan(transactionCtx, "serialize", sentry.WithDescription("json"))
	serializationSpan.SetTag("format", "json")
	out := []map[string]interface{}{}
	for _, p := range list {
		m := map[string]interface{}{}
		for k, v := range p.M {
			m[k] = v
		}
		m["reviews"] = p.Reviews
		out = append(out, m)
	}
	b, _ := json.Marshal(out)
	serializationSpan.Finish()

	return string(b), nil
}

func (s *server) getProductsJoin(ctx context.Context) (string, error) {
	conn, err := s.db.Acquire(ctx)
	if err != nil {
		return "", err
	}
	defer conn.Release()
	rows, err := conn.Query(ctx, "SELECT * FROM products")
	if err != nil {
		return "", err
	}
	defer rows.Close()
	prods := []map[string]interface{}{}
	for rows.Next() {
		vals, _ := rows.Values()
		fds := rows.FieldDescriptions()
		m := map[string]interface{}{}
		for i, fd := range fds {
			m[string(fd.Name)] = vals[i]
		}
		prods = append(prods, m)
	}
	revRows, err := conn.Query(ctx, "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id")
	if err != nil {
		return "", err
	}
	defer revRows.Close()
	reviews := []map[string]interface{}{}
	for revRows.Next() {
		vals, _ := revRows.Values()
		fds := revRows.FieldDescriptions()
		m := map[string]interface{}{}
		for i, fd := range fds {
			m[string(fd.Name)] = vals[i]
		}
		reviews = append(reviews, m)
	}
	res := []map[string]interface{}{}
	for _, p := range prods {
		pid := toInt(p["id"])
		m := map[string]interface{}{}
		for k, v := range p {
			m[k] = v
		}
		rv := make([]map[string]interface{}, 0)
		for _, r := range reviews {
			if toInt(r["productid"]) == pid {
				rv = append(rv, r)
			}
		}
		m["reviews"] = rv
		res = append(res, m)
	}
	b, _ := json.Marshal(res)
	return string(b), nil
}

func toInt(v interface{}) int {
	switch t := v.(type) {
	case int64:
		return int(t)
	case int32:
		return int(t)
	case int:
		return t
	case float64:
		return int(t)
	default:
		return 0
	}
}

func (s *server) proxyRuby(r *http.Request) error {
	hub := sentry.GetHubFromContext(r.Context())

	req, _ := http.NewRequest(http.MethodGet, s.rubyBackend+"/api", nil)
	for _, k := range []string{"se", "customerType", "email"} {
		if v := r.Header.Get(k); v != "" && v != "undefined" {
			req.Header.Set(k, v)
		}
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		hub.CaptureException(err)
		return err
	}
	_ = resp.Body.Close()
	if resp.StatusCode >= 400 {
		hub.CaptureMessage(fmt.Sprintf("ruby backend error: status %d", resp.StatusCode))
	}
	return nil
}

func (s *server) getAPIRequest(key string, delay float64, ctx context.Context) string {
	logger := sentry.NewLogger(ctx)
	start := time.Now()

	logger.Info().Emit("Processing /products - starting API request")

	cached, err := s.redis.Get(ctx, "ruby.api.cache:"+key).Result()
	if err == nil && cached != "" {
		logger.Info().Emit("Processing /products - cache hit for API request")
		return cached
	}

	logger.Info().Emit("Processing /products - cache miss for API request")

	sleep := delay - time.Since(start).Seconds()
	if sleep > 0 {
		time.Sleep(time.Duration(sleep*1000) * time.Millisecond)
	}
	if key == "7" {
		logger.Info().Emit("Processing /products - caching API response")
		s.redis.Set(ctx, "ruby.api.cache:"+key, key, 0)
	}
	return key
}

func (s *server) cachedOrganization() http.HandlerFunc {
	var cached string
	var expiry time.Time
	return func(w http.ResponseWriter, r *http.Request) {
		now := time.Now()
		if now.After(expiry) {
			if rand.Float64() < 0.01 {
				_, _ = s.getProducts(r.Context())
			}
			cached = "go /organization"
			expiry = now.Add(1000 * time.Second)
		}
		fmt.Fprint(w, cached)
	}
}
