Demo ASP.NET Core 3.1 HTTP service

Based on: https://dotnet.microsoft.com/en-us/learn/aspnet/microservice-tutorial/intro

1. Install .NET Core 3.1.19 from https://github.com/dotnet/core/blob/main/release-notes/3.1/3.1.19/3.1.19.md (Use x64 version on macOS, runs fine on M1 apple)

2. Copy contents of `aspnetcore/validate_env.list` and paste at the end of your `env-config/local.env` and fill them out.

```
./deploy.sh --env=local aspnetcore
```

Open in browser: http://localhost:8091/products

## Deploy to production : 
**(requires ASPNETCORE_APP_ENGINE_SERVICE=application-monitoring-aspnetcore in env-config/production.env)**


```
./deploy.sh --env=production aspnetcore
```

