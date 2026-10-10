var builder = DistributedApplication.CreateBuilder(args);
var configDirectory = AppContext.BaseDirectory;

builder.AddContainer("otel-dashboard", "mcr.microsoft.com/dotnet/aspire-dashboard")
    .WithEnvironment("ASPIRE_ALLOW_UNSECURED_TRANSPORT", "true")
    .WithEnvironment("DOTNET_DASHBOARD_UNSECURED_ALLOW_ANONYMOUS", "true")
    .WithEndpoint(
        port: 18880,
        targetPort: 18888,
        name: "dashboard",
        scheme: "http")
    .WithEndpoint(
        port: 18889,
        targetPort: 18889,
        name: "otlp-grpc",
        scheme: "http",
        isExternal: false);

builder.AddContainer("otel-collector", "otel/opentelemetry-collector-contrib")
    .WithBindMount(
        Path.Combine(configDirectory, "otel-collector.yaml"),
        "/etc/otelcol-contrib/config.yaml",
        isReadOnly: true)
    .WithArgs("--config=/etc/otelcol-contrib/config.yaml")
    .WithHttpEndpoint(port: 4318, targetPort: 4318, name: "otlp-http");

builder.AddContainer("tempo", "grafana/tempo")
    .WithBindMount(
        Path.Combine(configDirectory, "tempo.yaml"),
        "/etc/tempo.yaml",
        isReadOnly: true)
    .WithArgs("-config.file=/etc/tempo.yaml");

builder.AddContainer("loki", "grafana/loki")
    .WithBindMount(
        Path.Combine(configDirectory, "loki.yaml"),
        "/etc/loki/local-config.yaml",
        isReadOnly: true)
    .WithArgs("-config.file=/etc/loki/local-config.yaml");

builder.AddContainer("prometheus", "prom/prometheus")
    .WithBindMount(
        Path.Combine(configDirectory, "prometheus.yml"),
        "/etc/prometheus/prometheus.yml",
        isReadOnly: true)
    .WithArgs("--config.file=/etc/prometheus/prometheus.yml")
    .WithHttpEndpoint(port: 9090, targetPort: 9090, name: "http");

builder.AddContainer("grafana", "grafana/grafana")
    .WithBindMount(
        Path.Combine(configDirectory, "grafana-datasources.yaml"),
        "/etc/grafana/provisioning/datasources/datasources.yaml",
        isReadOnly: true)
    .WithEnvironment("GF_AUTH_ANONYMOUS_ENABLED", "false")
    .WithEnvironment("GF_SECURITY_ADMIN_USER", "admin")
    .WithEnvironment("GF_SECURITY_ADMIN_PASSWORD", "change-me")
    .WithHttpEndpoint(port: 3000, targetPort: 3000, name: "http");

builder.Build().Run();
