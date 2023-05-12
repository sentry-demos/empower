Demo ASP.NET Core 7 HTTP service

Uses the controller-based Web API approach.
See https://learn.microsoft.com/aspnet/core/web-api

1. Install the latest .NET 7 SDK from https://dotnet.microsoft.com/download
   - Use the OS and architecture that matches your machine.
   - For example, choose Arm64 if you have an Apple Sillicon (M1) machine, or x64 if you have an Intel processor. 

2. Copy contents of `aspnetcore/validate_env.list` and paste at the end of your `env-config/local.env` and fill them out.

```
./deploy.sh --env=local aspnetcore
```

Open in browser: http://localhost:8091/products

## Run locally with front end:

```
./deploy.sh --env=local aspnetcore react
```

Open in browser: http://localhost:3000/?backend=aspnetcore

## Deploy to production : 
**(requires ASPNETCORE_APP_ENGINE_SERVICE=application-monitoring-aspnetcore in env-config/production.env)**


```
./deploy.sh --env=production aspnetcore
```
