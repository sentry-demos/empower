Demo ASP.NET Core 9 HTTP service

Uses the controller-based Web API approach.
See https://learn.microsoft.com/aspnet/core/web-api

1. Install the latest .NET 9 SDK from https://dotnet.microsoft.com/download
   - Use the OS and architecture that matches your machine.
   - For example, choose Arm64 if you have an Apple Sillicon (M1) machine, or x64 if you have an Intel processor. 

```
./deploy --env=local aspnetcore
```

Open in browser: http://localhost:8091/products

## Run locally with front end:

```
./deploy --env=local aspnetcore react
```

Open in browser: http://localhost:3000/?backend=aspnetcore

## Deploy to production : 
**(requires ASPNETCORE_APP_ENGINE_SERVICE=application-monitoring-aspnetcore in env-config/production.env)**


```
./deploy --env=production aspnetcore
```
