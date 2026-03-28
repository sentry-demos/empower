package main

import (
	"context"
	"fmt"
	"log/slog"
	"math/rand"
	"os"
	"time"

	sentry "github.com/getsentry/sentry-go"
	redis "github.com/redis/go-redis/v9"
)

func mustEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		slog.Error("missing required env", "key", key)
		os.Exit(1)
	}
	return v
}

func initSentry() {
	_ = sentry.Init(sentry.ClientOptions{
		Dsn:              mustEnv("GO_DSN"),
		Release:          mustEnv("GO_RELEASE"),
		Environment:      mustEnv("GO_ENVIRONMENT"),
		EnableTracing:    true,
		EnableLogs:       true,
		TracesSampleRate: 1.0,
		// Note: ProfilesSampleRate not available in current Go SDK version
		// Flask equivalent: profiles_sample_rate: 1.0
		Debug: false,
	})
}

func main() {
	initSentry()

	host := os.Getenv("GO_REDISHOST")
	if host == "" {
		host = "localhost"
	}
	port := os.Getenv("GO_LOCAL_REDISPORT")
	if port == "" {
		port = "6379"
	}
	addr := host + ":" + port

	// Ensure we can reach Redis
	rdb := redis.NewClient(&redis.Options{Addr: addr, DB: 1})
	if err := rdb.Ping(context.Background()).Err(); err != nil {
		slog.Error("redis connection failed", "error", err)
		os.Exit(1)
	}

	// Simple loop to pop from Redis list and process
	queue := "celery-new-subscriptions"
	slog.Info("Worker listening", "queue", queue)
	for {
		res, err := rdb.BLPop(context.Background(), 0, queue).Result()
		if err != nil {
			slog.Error("BLPop error", "error", err)
			time.Sleep(2 * time.Second)
			continue
		}
		// res[0] is key, res[1] is value
		if len(res) < 2 {
			continue
		}
		email := res[1]
		x := rand.Intn(5)
		if x == 0 {
			err := fmt.Errorf("sending email error")
			sentry.CaptureException(err)
			// simulate retry delay
			time.Sleep(10 * time.Second)
			// requeue
			_ = rdb.RPush(context.Background(), queue, email).Err()
			continue
		}
		time.Sleep(time.Duration(x) * time.Second)
		slog.Info("Sending email", "to", email, "delay_seconds", x)
	}
}
