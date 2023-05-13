using Npgsql;

namespace Empower.Backend;

internal static class AppUtils
{
    public static string GetConnectionString(IConfiguration configuration)
    {
        // Try to use the environment variables we set in the startup scripts.
        var connectionStringBuilder = new NpgsqlConnectionStringBuilder
        {
            Host = Environment.GetEnvironmentVariable("DB_HOST"),
            Database = Environment.GetEnvironmentVariable("DB_DATABASE"),
            Username = Environment.GetEnvironmentVariable("DB_USERNAME"),
            Password = Environment.GetEnvironmentVariable("DB_PASSWORD")
        };

        if (!string.IsNullOrWhiteSpace(connectionStringBuilder.Host))
        {
            return connectionStringBuilder.ConnectionString;
        }

        // Otherwise, get it from configuration.
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        if (!string.IsNullOrWhiteSpace(connectionString))
        {
            return connectionString;
        }

        throw new Exception("Failed to get the database connection string.");
    }
}